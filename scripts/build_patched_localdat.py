#!/usr/bin/env python3
"""Build patched LOCALDAT_K.BIN and HELPLOCALDAT_K.BIN from translation_patches.json
and verify 100% binary format integrity, encoding roundtrip, and sector slot fitting.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import sys
from datetime import datetime, timezone, timedelta

# Import analyze_localdat functions
from analyze_localdat import (
    parse_loc_data,
    serialize_loc_data,
    encode_loc_payload,
    decode_loc_payload,
    sha256_bytes,
)

KST = timezone(timedelta(hours=9))
ROOT = pathlib.Path(__file__).resolve().parent.parent

# ISO slot limits from sector allocation analysis
# LOCALDAT_K starts at LBA 23296 (0x02D80000), next file starts at LBA 23376 (0x02DA8000) -> 80 sectors = 163,840 bytes
LOCALDAT_SLOT_LIMIT = 163840
# HELPLOCALDAT_K starts at LBA 23376 (0x02DA8000), next file starts at LBA 23408 (0x02DB8000) -> 32 sectors = 65,536 bytes
HELPLOCALDAT_SLOT_LIMIT = 65536


def main() -> int:
    parser = argparse.ArgumentParser(description="Build patched LOCALDAT_K and HELPLOCALDAT_K binaries.")
    parser.add_argument("--patches", default=str(ROOT / "workspace/translation/translation_patches.json"), help="Path to patches JSON.")
    args = parser.parse_args()

    patches_path = pathlib.Path(args.patches)
    if not patches_path.exists():
        raise FileNotFoundError(f"Patches file not found: {patches_path}")

    patches_list = json.loads(patches_path.read_text(encoding="utf-8"))
    patches_by_src: dict[str, dict[int, str]] = {"LOCALDAT": {}, "HELPLOCALDAT": {}}
    for p in patches_list:
        patches_by_src[p["source"]][p["ko_id"]] = p["new_ko"]

    targets = [
        ("LOCALDAT", "extracted/disc_ko/PSP_GAME/USRDIR/DATA/HUD/LOCALDAT_K.BIN", "build/PSP_GAME/USRDIR/DATA/HUD/LOCALDAT_K.BIN", LOCALDAT_SLOT_LIMIT),
        ("HELPLOCALDAT", "extracted/disc_ko/PSP_GAME/USRDIR/DATA/HUD/HELPLOCALDAT_K.BIN", "build/PSP_GAME/USRDIR/DATA/HUD/HELPLOCALDAT_K.BIN", HELPLOCALDAT_SLOT_LIMIT),
    ]

    build_report = {
        "generated_at": datetime.now(KST).isoformat(timespec="seconds"),
        "status": "ok",
        "patches_applied_count": len(patches_list),
        "files": {},
    }

    for src_name, in_rel, out_rel, slot_limit in targets:
        in_path = ROOT / in_rel
        out_path = ROOT / out_rel
        out_path.parent.mkdir(parents=True, exist_ok=True)

        if not in_path.exists():
            iso_path = ROOT / "Secret Agent Clank [K].iso"
            if not iso_path.exists():
                iso_path = ROOT / "original/iso/Secret Agent Clank [K].iso"
            inv_path = ROOT / "manifests/iso_inventory_ko.json"
            if iso_path.exists() and inv_path.exists():
                inv = json.loads(inv_path.read_text(encoding="utf-8"))["files"]
                files_by_path = {item["path"]: item for item in inv}
                rel_path = in_path.relative_to(ROOT / "extracted/disc_ko").as_posix()
                if rel_path in files_by_path:
                    info = files_by_path[rel_path]
                    print(f"[*] Auto-extracting {rel_path} from {iso_path.name}...")
                    in_path.parent.mkdir(parents=True, exist_ok=True)
                    with iso_path.open("rb") as f:
                        f.seek(info["iso_offset"])
                        in_path.write_bytes(f.read(info["size"]))
            if not in_path.exists():
                print(f"[-] Source file not found: {in_path}", file=sys.stderr)
                print(f"[-] Please place 'Secret Agent Clank [K].iso' in project root.", file=sys.stderr)
                return 1

        orig_data = in_path.read_bytes()
        parsed = parse_loc_data(orig_data, lang="ko")

        applied_in_file = 0
        file_patches = patches_by_src[src_name]

        for entry in parsed["entries"]:
            kid = entry["id"]
            if kid in file_patches:
                new_text = file_patches[kid]
                entry["text"] = new_text
                # Test payload encode
                payload = encode_loc_payload(entry, lang="ko", include_alignment_zeros=True)
                entry["byte_length"] = len(payload)
                entry["raw_hex"] = payload.hex()
                applied_in_file += 1

        # Serialize patched binary
        patched_binary = serialize_loc_data(parsed)
        out_path.write_bytes(patched_binary)

        # Re-parse to verify 100% binary and decoder integrity
        re_parsed = parse_loc_data(patched_binary, lang="ko")
        if len(re_parsed["entries"]) != len(parsed["entries"]):
            raise ValueError(f"Re-parsed entry count mismatch: {len(re_parsed['entries'])} != {len(parsed['entries'])}")

        for e_orig, e_new in zip(parsed["entries"], re_parsed["entries"]):
            if e_orig["id"] != e_new["id"]:
                raise ValueError(f"Entry ID mismatch at index {e_orig['index']}")
            if e_orig["text"] != e_new["text"]:
                raise ValueError(f"Decoded text mismatch for ID {e_orig['id']}:\n  {e_orig['text']!r}\n  !=\n  {e_new['text']!r}")

        # Check ISO sector allocation slot
        fits_slot = len(patched_binary) <= slot_limit
        if not fits_slot:
            raise ValueError(f"Patched binary exceeds ISO slot limit ({len(patched_binary)} > {slot_limit})")

        build_report["files"][src_name] = {
            "output_path": str(out_path.relative_to(ROOT)).replace("\\", "/"),
            "original_size": len(orig_data),
            "patched_size": len(patched_binary),
            "size_difference": len(patched_binary) - len(orig_data),
            "iso_slot_limit": slot_limit,
            "fits_in_iso_slot": fits_slot,
            "original_sha256": sha256_bytes(orig_data),
            "patched_sha256": sha256_bytes(patched_binary),
            "entries_total": len(parsed["entries"]),
            "entries_patched": applied_in_file,
            "reparse_verification_passed": True,
        }

    report_path = ROOT / "qa/reports/build_localdat_report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(build_report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(json.dumps(build_report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())

