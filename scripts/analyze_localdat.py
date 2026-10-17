#!/usr/bin/env python3
"""Deterministic parser, serializer, round-trip verifier, and JA<->KO catalog aligner
for Clank & Ratchet: Maruhi Mission Ignition! (UCJS10084) / Secret Agent Clank (UCKS45096)
LOC_DATA localization containers (LOCALDAT_*.BIN and HELPLOCALDAT_*.BIN).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
import struct
import sys
from datetime import datetime, timezone, timedelta
from typing import Any

KST = timezone(timedelta(hours=9))
ROOT = pathlib.Path(__file__).resolve().parent.parent

# Single-byte icon / symbol tokens (verified from BOOT.BIN 0x9d1c..0xa140 & FRONTEND.PRX)
SINGLE_BYTE_TOKENS: dict[int, str] = {
    0x80: "<BTN_CROSS>",
    0x81: "<BTN_SQUARE>",
    0x82: "<BTN_TRIANGLE>",
    0x83: "<BTN_CIRCLE>",
    0x86: "<ICON_86>",
    0x89: "<ELLIPSIS>",
    0x8A: "<ICON_8A>",
    0x8B: "<ICON_8B>",
    0x9E: "<BTN_L>",
    0x9F: "<BTN_R>",
    0xA4: "<SYM_TM>",
}
INV_SINGLE_BYTE_TOKENS: dict[str, int] = {v: k for k, v in SINGLE_BYTE_TOKENS.items()}

# Special 0x93 XX punctuation mappings in Japanese font (outside standard U+3000+XX Kana range)
JA_93_SPECIAL: dict[int, str] = {
    0x01: "、",
    0x02: "。",
    0x0C: "「",
    0x0D: "」",
    0x27: "〜",
    0x28: "！",
    0x29: "？",
    0x2A: "♪",
}
INV_JA_93_SPECIAL: dict[str, int] = {v: k for k, v in JA_93_SPECIAL.items()}

TOKEN_RE = re.compile(
    r"<(?:"
    r"BTN_CROSS|BTN_SQUARE|BTN_TRIANGLE|BTN_CIRCLE|BTN_L|BTN_R|SYM_TM|ELLIPSIS|"
    r"ICON_86|ICON_8A|ICON_8B|"
    r"COL:[0-9A-F]{2}|SCALE:[0-9A-F]{2}|JA93:[0-9A-F]{2}|RAW:[0-9A-F]{2}"
    r")>"
)
PRINTF_RE = re.compile(r"%(?:\d+\$)?[-+ #0]*(?:\d+|\*)?(?:\.(?:\d+|\*))?[hlL]?[diuoxXfFeEgGaAcspn%]")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def decode_loc_payload(payload: bytes, lang: str) -> dict[str, Any]:
    """Decode a single ENTR payload (bytes after b'ENTR') into a lossless dict."""
    if not payload:
        raise ValueError("Empty ENTR payload")

    if payload[0] == 0x00 and len(payload) > 4:
        # Format 1: PSP Savedata UTF-8 entry: \x00 + len_byte + utf8_bytes + \xc0\x80
        declared_len = payload[1]
        if declared_len != len(payload) - 2 or payload[-2:] != b"\xc0\x80":
            raise ValueError(f"Invalid UTF-8 savedata payload header/trailer: {payload.hex()}")
        text = payload[2:-2].decode("utf-8")
        return {
            "format": "utf8_savedata",
            "text": text,
            "trailing_zeros": 0,
            "byte_length": len(payload),
        }

    # Format 2: Null-terminated in-game HUD/dialogue string
    null_pos = payload.find(b"\x00")
    if null_pos == -1:
        raise ValueError(f"Missing null terminator in payload: {payload.hex()}")
    trail = payload[null_pos:]
    if any(b != 0 for b in trail):
        raise ValueError(f"Non-zero bytes after null terminator: {trail.hex()}")

    raw = payload[:null_pos]
    out: list[str] = []
    i = 0
    n = len(raw)
    while i < n:
        b = raw[i]
        if b == 0x90:
            if i + 1 >= n:
                raise ValueError(f"Truncated 0x90 color token at end of {raw.hex()}")
            out.append(f"<COL:{raw[i+1]:02X}>")
            i += 2
        elif b == 0x91:
            if i + 1 >= n:
                raise ValueError(f"Truncated 0x91 scale token at end of {raw.hex()}")
            out.append(f"<SCALE:{raw[i+1]:02X}>")
            i += 2
        elif b == 0x93:
            if i + 1 >= n:
                raise ValueError(f"Truncated 0x93 kana token at end of {raw.hex()}")
            c = raw[i + 1]
            if lang == "ja" and (c in JA_93_SPECIAL or 0x41 <= c <= 0x93 or 0xA1 <= c <= 0xFC):
                if c in JA_93_SPECIAL:
                    out.append(JA_93_SPECIAL[c])
                else:
                    out.append(chr(0x3000 + c))
            else:
                out.append(f"<JA93:{c:02X}>")
            i += 2
        elif 0xAC <= b <= 0xD7:
            if i + 1 >= n:
                raise ValueError(f"Truncated Hangul syllable at end of {raw.hex()}")
            b1 = raw[i + 1]
            code = (b << 8) | b1
            if 0xD7AC <= code <= 0xD7D7:
                # Null-byte escape for U+AC00, U+AD00, ..., U+D700
                code = (code & 0xFF) << 8
            out.append(chr(code))
            i += 2
        elif b in SINGLE_BYTE_TOKENS:
            out.append(SINGLE_BYTE_TOKENS[b])
            i += 1
        elif b == 0x0A:
            out.append("\n")
            i += 1
        elif 0x20 <= b <= 0x7E:
            out.append(chr(b))
            i += 1
        else:
            out.append(f"<RAW:{b:02X}>")
            i += 1

    return {
        "format": "hud_string",
        "text": "".join(out),
        "trailing_zeros": len(trail),
        "byte_length": len(payload),
    }


def encode_loc_payload(entry_info: dict[str, Any], lang: str, include_alignment_zeros: bool = True) -> bytes:
    """Re-encode a decoded entry dict back into exact ENTR payload bytes."""
    fmt = entry_info["format"]
    text: str = entry_info["text"]
    if fmt == "utf8_savedata":
        utf8_bytes = text.encode("utf-8")
        length_byte = len(utf8_bytes) + 2
        if length_byte > 255:
            raise ValueError(f"UTF-8 savedata string exceeds 253 bytes ({len(utf8_bytes)} bytes)")
        return bytes([0x00, length_byte]) + utf8_bytes + b"\xc0\x80"

    if fmt != "hud_string":
        raise ValueError(f"Unknown entry format: {fmt}")

    buf = bytearray()
    pos = 0
    length = len(text)
    while pos < length:
        if text[pos] == "<":
            m = TOKEN_RE.match(text, pos)
            if m:
                tok = m.group(0)
                if tok in INV_SINGLE_BYTE_TOKENS:
                    buf.append(INV_SINGLE_BYTE_TOKENS[tok])
                elif tok.startswith("<COL:"):
                    buf.extend([0x90, int(tok[5:7], 16)])
                elif tok.startswith("<SCALE:"):
                    buf.extend([0x91, int(tok[7:9], 16)])
                elif tok.startswith("<JA93:"):
                    buf.extend([0x93, int(tok[6:8], 16)])
                elif tok.startswith("<RAW:"):
                    buf.append(int(tok[5:7], 16))
                pos = m.end()
                continue

        ch = text[pos]
        code = ord(ch)
        if ch == "\n":
            buf.append(0x0A)
        elif 0x20 <= code <= 0x7E:
            buf.append(code)
        elif lang == "ja" and ch in INV_JA_93_SPECIAL:
            buf.extend([0x93, INV_JA_93_SPECIAL[ch]])
        elif lang == "ja" and (0x3041 <= code <= 0x3093 or 0x30A1 <= code <= 0x30FC):
            buf.extend([0x93, code - 0x3000])
        elif 0xAC00 <= code <= 0xD7A3:
            if (code & 0xFF) == 0x00:
                # Null-byte escape: 0xXX00 -> 0xD7XX
                buf.extend([0xD7, (code >> 8) & 0xFF])
            else:
                buf.extend([(code >> 8) & 0xFF, code & 0xFF])
        else:
            raise ValueError(f"Unencodable character {ch!r} (U+{code:04X}) for lang={lang}")
        pos += 1

    if include_alignment_zeros:
        zeros = int(entry_info.get("trailing_zeros", 1))
    else:
        zeros = 1
    buf.extend(b"\x00" * zeros)
    return bytes(buf)


def parse_loc_data(data: bytes, lang: str) -> dict[str, Any]:
    """Parse a complete LOC_DATA binary file into a structured representation."""
    if len(data) < 0x44 or data[:8] != b"LOC_DATA":
        raise ValueError("Invalid LOC_DATA magic or truncated header")

    version_flags, count_lang = struct.unpack_from("<II", data, 0x08)
    entry_count = count_lang >> 8
    num_languages = count_lang & 0xFF

    scol_tag = data[0x10:0x14]
    if scol_tag != b"SCOL":
        raise ValueError(f"Expected SCOL tag at 0x10, found {scol_tag!r}")
    colors = list(struct.unpack_from("<8I", data, 0x14))

    ltoc_tag = data[0x34:0x38]
    if ltoc_tag != b"LTOC":
        raise ValueError(f"Expected LTOC tag at 0x34, found {ltoc_tag!r}")
    ltoc_a, ltoc_b, ltoc_c = struct.unpack_from("<III", data, 0x38)

    tdefs: list[tuple[int, int]] = []
    for i in range(entry_count):
        tag, text_id, off_from_40 = struct.unpack_from("<4siI", data, 0x44 + i * 12)
        if tag != b"TDEF":
            raise ValueError(f"Expected TDEF tag at index {i}, found {tag!r}")
        tdefs.append((text_id, off_from_40))

    entries: list[dict[str, Any]] = []
    str_end_limit = 0x44 + ltoc_c
    for i, (text_id, off_from_40) in enumerate(tdefs):
        entr_start = 0x40 + off_from_40
        entr_end = (0x40 + tdefs[i + 1][1]) if (i + 1 < entry_count) else str_end_limit
        if data[entr_start : entr_start + 4] != b"ENTR":
            raise ValueError(f"Expected ENTR tag at 0x{entr_start:X} for ID {text_id}")
        payload = data[entr_start + 4 : entr_end]
        decoded = decode_loc_payload(payload, lang=lang)
        entries.append(
            {
                "index": i,
                "id": text_id,
                "offset_from_0x40": off_from_40,
                "file_offset": entr_start,
                "format": decoded["format"],
                "text": decoded["text"],
                "trailing_zeros": decoded["trailing_zeros"],
                "byte_length": decoded["byte_length"],
                "raw_hex": payload.hex(),
            }
        )

    timing_start = 0x44 + ltoc_c
    timing_end = 0x44 + ltoc_b
    timing_blob = data[timing_start:timing_end]
    if len(timing_blob) < 12:
        raise ValueError("Truncated subtitle timing table")
    n1, n2, n3 = struct.unpack_from("<III", timing_blob, 0)
    expected_timing_size = 12 + 4 * n1 + 4 * n2 + 8 * n3
    if len(timing_blob) != expected_timing_size:
        raise ValueError(
            f"Subtitle timing size mismatch: header ({n1},{n2},{n3}) -> {expected_timing_size} != {len(timing_blob)}"
        )

    tail_blob = data[timing_end:]

    return {
        "lang": lang,
        "version_flags": version_flags,
        "entry_count": entry_count,
        "num_languages": num_languages,
        "colors": colors,
        "ltoc": {"a": ltoc_a, "b": ltoc_b, "c": ltoc_c},
        "timing_header": {"n1": n1, "n2": n2, "n3": n3, "byte_length": len(timing_blob)},
        "timing_hex": timing_blob.hex(),
        "post_ltoc_tail_length": len(tail_blob),
        "post_ltoc_tail_hex": tail_blob.hex(),
        "entries": entries,
    }


def serialize_loc_data(parsed: dict[str, Any]) -> bytes:
    """Deterministically serialize a parsed LOC_DATA structure back into binary bytes."""
    lang = parsed["lang"]
    entries = parsed["entries"]
    entry_count = len(entries)
    num_languages = parsed["num_languages"]
    version_flags = parsed["version_flags"]
    colors = parsed["colors"]

    tdef_table_size = entry_count * 12
    # Offset from 0x40 where the first ENTR begins: 0x04 + tdef_table_size
    cur_off_from_40 = 4 + tdef_table_size

    tdef_buf = bytearray()
    entr_buf = bytearray()

    for i, entry in enumerate(entries):
        is_last = i == (entry_count - 1)
        payload = encode_loc_payload(entry, lang=lang, include_alignment_zeros=False)
        if is_last:
            # Pad end of string table so (0x44 + ltoc_c) is 4-byte aligned
            pos_after_payload = 0x40 + cur_off_from_40 + 4 + len(payload)
            pad_zeros = (-pos_after_payload) % 4
            payload = payload + (b"\x00" * pad_zeros)

        tdef_buf.extend(struct.pack("<4siI", b"TDEF", entry["id"], cur_off_from_40))
        entr_buf.extend(b"ENTR")
        entr_buf.extend(payload)
        cur_off_from_40 += 4 + len(payload)

    ltoc_a = 0x44
    ltoc_c = tdef_table_size + len(entr_buf)
    timing_blob = bytes.fromhex(parsed["timing_hex"])
    ltoc_b = ltoc_c + len(timing_blob)
    tail_blob = bytes.fromhex(parsed["post_ltoc_tail_hex"])

    header = bytearray()
    header.extend(b"LOC_DATA")
    header.extend(struct.pack("<II", version_flags, (entry_count << 8) | num_languages))
    header.extend(b"SCOL")
    header.extend(struct.pack("<8I", *colors))
    header.extend(b"LTOC")
    header.extend(struct.pack("<III", ltoc_a, ltoc_b, ltoc_c))

    return bytes(header) + bytes(tdef_buf) + bytes(entr_buf) + timing_blob + tail_blob


def classify_id_category(text_id: int) -> str:
    if text_id < 0:
        return "help_popup_voice"
    if text_id == 1:
        return "ui_camera_option"
    if 2 <= text_id <= 274:
        return "keyword_glossary_colored"
    if 275 <= text_id <= 639:
        return "ui_hud_menu_prompt"
    if 640 <= text_id <= 726:
        return "weapon_armor_wrench_desc"
    if 727 <= text_id <= 838 or 2501 <= text_id <= 2505:
        return "memstick_savedata_system"
    if 1000 <= text_id <= 1084:
        return "challenge_arena_title"
    if 2000 <= text_id <= 2226 or 4000 <= text_id <= 4226:
        return "rhythm_minigame_subtitle"
    if 3000 <= text_id <= 3063:
        return "skill_point_title"
    if 4600 <= text_id <= 4651:
        return "gadgebot_challenge_ui"
    if 5501 <= text_id <= 5675:
        return "mission_objective_title"
    if 6001 <= text_id <= 6005:
        return "character_boss_name"
    if 6501 <= text_id <= 6942:
        return "cutscene_movie_subtitle"
    if 7000 <= text_id <= 7450:
        return "in_game_dialogue_cinematic"
    if 8000 <= text_id <= 8063:
        return "treehouse_developer_secret"
    return "misc"


def map_ja_id_to_ko_id(ja_id: int) -> int:
    """Exact deterministic mapping from LOCALDAT_J.BIN text_id to LOCALDAT_K.BIN text_id.
    Due to 3 demo-menu strings inserted at KO IDs 637..639:
    - JA 637..835 -> KO 640..838 (+3)
    - JA 836..838 -> KO 2501..2503
    - JA 2501..2502 -> KO 2504..2505 (+3)
    - All other JA IDs map 1:1 to identical KO IDs.
    """
    if 637 <= ja_id <= 835:
        return ja_id + 3
    if 836 <= ja_id <= 838:
        return 2501 + (ja_id - 836)
    if 2501 <= ja_id <= 2502:
        return ja_id + 3
    return ja_id


def extract_tokens(text: str) -> list[str]:
    return TOKEN_RE.findall(text)


def extract_printf_specs(text: str) -> list[str]:
    return PRINTF_RE.findall(text)


def build_aligned_catalog(
    ja_parsed: dict[str, Any], ko_parsed: dict[str, Any], is_help: bool = False
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    ja_by_id = {e["id"]: e for e in ja_parsed["entries"]}
    ko_by_id = {e["id"]: e for e in ko_parsed["entries"]}

    # Reverse map KO ID -> JA ID
    ko_to_ja: dict[int, int | None] = {}
    if is_help:
        for kid in ko_by_id:
            ko_to_ja[kid] = kid
    else:
        for jid in ja_by_id:
            kid = map_ja_id_to_ko_id(jid)
            if kid not in ko_by_id:
                raise ValueError(f"Mapped KO ID {kid} (from JA ID {jid}) missing in LOCALDAT_K.BIN")
            ko_to_ja[kid] = jid
        for kid in ko_by_id:
            if kid not in ko_to_ja:
                ko_to_ja[kid] = None

    rows: list[dict[str, Any]] = []
    stats = {
        "total_ko_entries": len(ko_parsed["entries"]),
        "total_ja_entries": len(ja_parsed["entries"]),
        "paired_count": 0,
        "ko_only_count": 0,
        "shifted_id_count": 0,
        "printf_mismatch_count": 0,
        "button_token_diff_count": 0,
        "untranslated_or_placeholder_count": 0,
        "english_remnant_candidates": [],
        "button_token_diffs": [],
        "printf_mismatches": [],
    }

    for ko_entry in ko_parsed["entries"]:
        kid = ko_entry["id"]
        jid = ko_to_ja[kid]
        ja_entry = ja_by_id.get(jid) if jid is not None else None

        ko_text = ko_entry["text"]
        ja_text = ja_entry["text"] if ja_entry else None

        ko_printf = extract_printf_specs(ko_text)
        ja_printf = extract_printf_specs(ja_text) if ja_text is not None else []

        ko_btns = [t for t in extract_tokens(ko_text) if t.startswith("<BTN_")]
        ja_btns = [t for t in extract_tokens(ja_text) if t.startswith("<BTN_")] if ja_text is not None else []

        flags: list[str] = []
        if jid is None:
            flags.append("ko_only_inserted")
            stats["ko_only_count"] += 1
        else:
            stats["paired_count"] += 1
            if jid != kid:
                flags.append("id_shifted_plus_3")
                stats["shifted_id_count"] += 1
            if ko_printf != ja_printf:
                flags.append("printf_spec_mismatch")
                stats["printf_mismatch_count"] += 1
                stats["printf_mismatches"].append(
                    {"ko_id": kid, "ja_id": jid, "ja_printf": ja_printf, "ko_printf": ko_printf}
                )
            if ko_btns != ja_btns:
                flags.append("button_icon_diff")
                stats["button_token_diff_count"] += 1
                if len(stats["button_token_diffs"]) < 25:
                    stats["button_token_diffs"].append(
                        {"ko_id": kid, "ja_id": jid, "ja_btns": ja_btns, "ko_btns": ko_btns, "ja_text": ja_text, "ko_text": ko_text}
                    )

        if "DO NOT TRANSLATE" in ko_text or "DONT TRANSLATE" in ko_text or "<JA93:" in ko_text or ko_text == "?NDEF":
            flags.append("untranslated_or_dummy")
            stats["untranslated_or_placeholder_count"] += 1
        elif re.search(r"[A-Za-z]{5,}", TOKEN_RE.sub("", ko_text)):
            # Check if purely English sentence or notable English remnant (excluding Memory Stick / Secret Agent Clank)
            cleaned = TOKEN_RE.sub("", ko_text)
            cleaned_no_brand = (
                cleaned.replace("Memory Stick Duo", "")
                .replace("Memory Stick", "")
                .replace("Secret Agent Clank", "")
                .replace("High Impact Games", "")
                .replace("START", "")
                .replace("SELECT", "")
            )
            if re.search(r"[A-Za-z]{5,}", cleaned_no_brand):
                flags.append("contains_english_word")
                stats["english_remnant_candidates"].append(
                    {"ko_id": kid, "ja_id": jid, "ja_text": ja_text, "ko_text": ko_text}
                )

        rows.append(
            {
                "ko_index": ko_entry["index"],
                "ko_id": kid,
                "ja_index": ja_entry["index"] if ja_entry else None,
                "ja_id": jid,
                "category": classify_id_category(kid),
                "format": ko_entry["format"],
                "ja_text": ja_text,
                "ko_text": ko_text,
                "flags": flags,
            }
        )

    return rows, stats


def write_jsonl(path: pathlib.Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze and verify LOC_DATA files.")
    parser.add_argument("--verify-only", action="store_true", help="Only run round-trip verification.")
    args = parser.parse_args()

    targets = [
        ("localdat_ja", "ja", ROOT / "extracted/disc_ja/PSP_GAME/USRDIR/DATA/HUD/LOCALDAT_J.BIN"),
        ("localdat_ko", "ko", ROOT / "extracted/disc_ko/PSP_GAME/USRDIR/DATA/HUD/LOCALDAT_K.BIN"),
        ("helplocaldat_ja", "ja", ROOT / "extracted/disc_ja/PSP_GAME/USRDIR/DATA/HUD/HELPLOCALDAT_J.BIN"),
        ("helplocaldat_ko", "ko", ROOT / "extracted/disc_ko/PSP_GAME/USRDIR/DATA/HUD/HELPLOCALDAT_K.BIN"),
    ]

    parsed_map: dict[str, dict[str, Any]] = {}
    verification_results: dict[str, Any] = {}

    for key, lang, path in targets:
        raw = path.read_bytes()
        orig_sha = sha256_bytes(raw)
        parsed = parse_loc_data(raw, lang=lang)

        # Verify individual entry payload round-trip
        entry_rt_ok = 0
        for e in parsed["entries"]:
            re_enc = encode_loc_payload(e, lang=lang, include_alignment_zeros=True)
            if re_enc.hex() != e["raw_hex"]:
                raise AssertionError(
                    f"Entry round-trip mismatch in {path.name} ID={e['id']}: {re_enc.hex()} != {e['raw_hex']}"
                )
            entry_rt_ok += 1

        # Verify full binary container serialization round-trip
        rebuilt = serialize_loc_data(parsed)
        rebuilt_sha = sha256_bytes(rebuilt)
        if rebuilt != raw:
            raise AssertionError(f"Container round-trip mismatch for {path.name}: {rebuilt_sha} != {orig_sha}")

        parsed_map[key] = parsed
        verification_results[key] = {
            "path": str(path.relative_to(ROOT)).replace("\\", "/"),
            "size_bytes": len(raw),
            "sha256": orig_sha,
            "rebuilt_sha256": rebuilt_sha,
            "byte_identical_roundtrip": rebuilt == raw,
            "version_flags_hex": f"0x{parsed['version_flags']:08X}",
            "entry_count": parsed["entry_count"],
            "entry_payload_roundtrip_passed": entry_rt_ok,
            "utf8_savedata_entry_count": sum(1 for e in parsed["entries"] if e["format"] == "utf8_savedata"),
            "hud_string_entry_count": sum(1 for e in parsed["entries"] if e["format"] == "hud_string"),
            "ltoc": parsed["ltoc"],
            "timing_header": parsed["timing_header"],
            "post_ltoc_tail_length": parsed["post_ltoc_tail_length"],
        }

    if args.verify_only:
        print(json.dumps({"status": "ok", "verification": verification_results}, indent=2, ensure_ascii=False))
        return 0

    # Export extracted per-file JSONL catalogs
    for key, _, _ in targets:
        out_path = ROOT / "extracted/text" / f"{key}.jsonl"
        write_jsonl(out_path, parsed_map[key]["entries"])

    # Build aligned JA<->KO catalogs
    localdat_aligned, localdat_stats = build_aligned_catalog(
        parsed_map["localdat_ja"], parsed_map["localdat_ko"], is_help=False
    )
    helplocaldat_aligned, helplocaldat_stats = build_aligned_catalog(
        parsed_map["helplocaldat_ja"], parsed_map["helplocaldat_ko"], is_help=True
    )

    write_jsonl(ROOT / "workspace/translation/localdat_ja_ko_aligned.jsonl", localdat_aligned)
    write_jsonl(ROOT / "workspace/translation/helplocaldat_ja_ko_aligned.jsonl", helplocaldat_aligned)

    # Check timing table equality between JA and KO
    localdat_timing_identical = (
        parsed_map["localdat_ja"]["timing_hex"] == parsed_map["localdat_ko"]["timing_hex"]
    )
    helplocaldat_timing_identical = (
        parsed_map["helplocaldat_ja"]["timing_hex"] == parsed_map["helplocaldat_ko"]["timing_hex"]
    )

    report = {
        "generated_at": datetime.now(KST).isoformat(timespec="seconds"),
        "status": "ok",
        "verification": verification_results,
        "timing_tables_identical": {
            "localdat_ja_vs_ko": localdat_timing_identical,
            "helplocaldat_ja_vs_ko": helplocaldat_timing_identical,
        },
        "alignment": {
            "localdat": localdat_stats,
            "helplocaldat": helplocaldat_stats,
        },
    }

    report_path = ROOT / "qa/reports/localdat_analysis.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(
        json.dumps(
            {
                "status": "ok",
                "files_verified": len(verification_results),
                "total_entries_verified": sum(v["entry_count"] for v in verification_results.values()),
                "localdat_paired": localdat_stats["paired_count"],
                "localdat_ko_only": localdat_stats["ko_only_count"],
                "helplocaldat_paired": helplocaldat_stats["paired_count"],
                "report": str(report_path.relative_to(ROOT)).replace("\\", "/"),
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

