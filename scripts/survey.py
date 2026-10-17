"""Read-only ISO9660 survey and source verification for Clank & Ratchet (JP) and Secret Agent Clank (KR)."""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SOURCES_SPEC = {
    "ja": {
        "role": "japanese_reference_source",
        "path": "original/iso/Clank & Ratchet - Maruhi Mission Ignition! (Japan).iso",
        "root_path": "Clank & Ratchet - Maruhi Mission Ignition! (Japan).iso",
        "extract_dir": "extracted/disc_ja",
        "inventory_manifest": "manifests/iso_inventory_ja.json",
    },
    "ko": {
        "role": "korean_base_target",
        "path": "original/iso/Secret Agent Clank [K].iso",
        "root_path": "Secret Agent Clank [K].iso",
        "extract_dir": "extracted/disc_ko",
        "inventory_manifest": "manifests/iso_inventory_ko.json",
    },
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(8 * 1024 * 1024):
            h.update(chunk)
    return h.hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def save_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def parse_sfo(data: bytes) -> dict[str, str | int]:
    magic, version, keys_off, values_off, count = struct.unpack_from("<5I", data, 0)
    if magic != 0x46535000:
        raise ValueError(f"Invalid PARAM.SFO magic: 0x{magic:08X}")
    result: dict[str, str | int] = {}
    for i in range(count):
        key_off, fmt, length, capacity, val_off = struct.unpack_from("<HHIII", data, 20 + 16 * i)
        key_name = data[keys_off + key_off :].split(b"\x00", 1)[0].decode("utf-8")
        raw = data[values_off + val_off : values_off + val_off + length]
        if fmt == 0x0404:
            result[key_name] = int.from_bytes(raw, "little")
        else:
            result[key_name] = raw.rstrip(b"\x00").decode("utf-8", errors="replace")
    return result


def inspect_iso(iso_path: Path) -> tuple[list[dict[str, object]], dict[str, str | int]]:
    file_size = iso_path.stat().st_size
    files: list[dict[str, object]] = []
    visited: set[int] = set()
    param_sfo_data: bytes | None = None

    with iso_path.open("rb") as f:
        f.seek(16 * 2048)
        pvd = f.read(2048)
        if pvd[:7] != b"\x01CD001\x01":
            raise ValueError(f"Unsupported PVD in {iso_path}")
        block_size = struct.unpack_from("<H", pvd, 128)[0]
        if block_size != 2048:
            raise ValueError(f"Unsupported logical block size {block_size} in {iso_path}")

        def both32(record: bytes, offset: int) -> int:
            le = struct.unpack_from("<I", record, offset)[0]
            be = struct.unpack_from(">I", record, offset + 4)[0]
            if le != be:
                raise ValueError(f"ISO dual-endian mismatch: {le} != {be}")
            return le

        def walk(record: bytes, parent: Path) -> None:
            nonlocal param_sfo_data
            lba = both32(record, 2)
            size = both32(record, 10)
            if lba in visited:
                raise ValueError(f"Directory cycle at LBA {lba}")
            visited.add(lba)
            start = lba * 2048
            if start + size > file_size:
                raise ValueError(f"Directory outside ISO bounds at LBA {lba}")
            f.seek(start)
            block = f.read(size)
            pos = 0
            while pos < size:
                n = block[pos]
                if not n:
                    pos = (pos // 2048 + 1) * 2048
                    continue
                rec = block[pos : pos + n]
                if n < 34 or len(rec) != n or 33 + rec[32] > n:
                    raise ValueError("Truncated ISO directory record")
                pos += n
                raw_name = rec[33 : 33 + rec[32]]
                if raw_name in (b"\x00", b"\x01"):
                    continue
                name = raw_name.decode("ascii").removesuffix(";1")
                if name in ("", ".", "..") or any(c in name for c in "/\\:"):
                    raise ValueError(f"Unsafe ISO path component: {name}")
                rel_path = parent / name
                flags = rec[25]
                if flags & 0x80:
                    raise ValueError(f"Multi-extent record unsupported: {rel_path}")
                if flags & 0x02:
                    walk(rec, rel_path)
                else:
                    extent = both32(rec, 2)
                    length = both32(rec, 10)
                    iso_offset = extent * 2048
                    if iso_offset + length > file_size:
                        raise ValueError(f"File outside ISO bounds: {rel_path}")
                    f.seek(iso_offset)
                    h = hashlib.sha256()
                    remaining = length
                    magic_bytes = b""
                    chunks_for_sfo: list[bytes] = []
                    is_sfo = rel_path.as_posix().upper() == "PSP_GAME/PARAM.SFO"
                    while remaining > 0:
                        chunk = f.read(min(remaining, 4 * 1024 * 1024))
                        if not chunk:
                            raise ValueError(f"Unexpected EOF reading {rel_path}")
                        if len(magic_bytes) < 16:
                            magic_bytes += chunk[: 16 - len(magic_bytes)]
                        if is_sfo:
                            chunks_for_sfo.append(chunk)
                        h.update(chunk)
                        remaining -= len(chunk)
                    if is_sfo:
                        param_sfo_data = b"".join(chunks_for_sfo)
                    files.append(
                        {
                            "path": rel_path.as_posix(),
                            "lba": extent,
                            "iso_offset": iso_offset,
                            "size": length,
                            "sha256": h.hexdigest(),
                            "magic_hex": magic_bytes.hex(),
                        }
                    )

        root_rec = pvd[156 : 156 + pvd[156]]
        walk(root_rec, Path())

    if len({item["path"] for item in files}) != len(files):
        raise ValueError(f"Duplicate file paths in {iso_path}")
    if param_sfo_data is None:
        raise ValueError(f"Missing PSP_GAME/PARAM.SFO in {iso_path}")
    return files, parse_sfo(param_sfo_data)


def extract_metadata_files(iso_path: Path, files: list[dict[str, object]], out_root: Path) -> list[str]:
    extracted: list[str] = []
    with iso_path.open("rb") as f:
        for item in files:
            rel = str(item["path"])
            upper = rel.upper()
            # Extract PARAM.SFO, UMD_DATA.BIN, PSP_GAME/SYSDIR/*, ICON0.PNG, FRONTEND.PRX, and PSP_GAME/USRDIR/DATA/HUD/*
            if (
                upper
                in (
                    "UMD_DATA.BIN",
                    "PSP_GAME/PARAM.SFO",
                    "PSP_GAME/ICON0.PNG",
                    "PSP_GAME/USRDIR/BIN/FRONTEND.PRX",
                )
                or upper.startswith("PSP_GAME/SYSDIR/")
                or upper.startswith("PSP_GAME/USRDIR/DATA/HUD/")
            ):
                target = out_root / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                f.seek(int(item["iso_offset"]))
                payload = f.read(int(item["size"]))
                if sha256_bytes(payload) != item["sha256"]:
                    raise ValueError(f"SHA-256 mismatch while extracting {rel}")
                if target.exists() and sha256_file(target) != item["sha256"]:
                    raise ValueError(f"Refusing to overwrite modified file: {target}")
                if not target.exists():
                    target.write_bytes(payload)
                extracted.append(rel)
    return extracted


def verify_source_only() -> None:
    manifest_path = ROOT / "manifests/sources.json"
    if not manifest_path.exists():
        raise FileNotFoundError("manifests/sources.json not found; run survey.py --init first")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    results = {}
    for key, entry in manifest["sources"].items():
        iso_path = ROOT / entry["path"]
        root_path = ROOT / entry["received_filename"]
        size = iso_path.stat().st_size
        digest = sha256_file(iso_path)
        root_digest = sha256_file(root_path)
        if size != entry["size"] or digest != entry["sha256"] or root_digest != entry["sha256"]:
            raise ValueError(f"Source verification failed for {key}")
        results[key] = {
            "verified": True,
            "disc_id": entry["disc_id"],
            "disc_version": entry["disc_version"],
            "size": size,
            "sha256": digest,
            "root_copy_matches": True,
        }
    print(json.dumps({"sources_verified": True, "sources": results}, ensure_ascii=False))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--init", action="store_true", help="Scan ISOs, create manifests, and extract metadata/SYSDIR")
    parser.add_argument("--verify-source-only", action="store_true", help="Verify registered ISO sizes and SHA-256")
    args = parser.parse_args()

    if args.verify_source_only:
        verify_source_only()
        return

    sources_manifest: dict[str, object] = {"schema_version": 1, "sources": {}}
    survey_report: dict[str, object] = {
        "schema_version": 1,
        "validation_class": "static source and ISO9660 inventory verification",
        "iso_rebuild_tested": False,
        "runtime_tested": False,
        "sources": {},
    }

    for key, spec in SOURCES_SPEC.items():
        iso_path = ROOT / spec["path"]
        root_path = ROOT / spec["root_path"]
        if not iso_path.exists():
            raise FileNotFoundError(f"Missing preserved ISO: {iso_path}")
        if not root_path.exists():
            raise FileNotFoundError(f"Missing root ISO: {root_path}")
        size = iso_path.stat().st_size
        digest = sha256_file(iso_path)
        root_digest = sha256_file(root_path)
        if digest != root_digest:
            raise ValueError(f"Root and preserved ISO hash mismatch for {key}")

        files, sfo = inspect_iso(iso_path)
        extracted_meta = extract_metadata_files(iso_path, files, ROOT / spec["extract_dir"])

        save_json(
            ROOT / spec["inventory_manifest"],
            {
                "schema_version": 1,
                "source_key": key,
                "source_sha256": digest,
                "source_size": size,
                "disc_id": sfo.get("DISC_ID", ""),
                "disc_version": sfo.get("DISC_VERSION", ""),
                "title": sfo.get("TITLE", ""),
                "file_count": len(files),
                "files": files,
            },
        )

        sources_manifest["sources"][key] = {
            "role": spec["role"],
            "path": spec["path"],
            "received_filename": spec["root_path"],
            "size": size,
            "sha256": digest,
            "disc_id": sfo.get("DISC_ID", ""),
            "disc_version": sfo.get("DISC_VERSION", ""),
            "title": sfo.get("TITLE", ""),
            "root_copy_retained": True,
            "identity_scope": "user supplied image; verified between root and original/iso",
        }

        survey_report["sources"][key] = {
            "role": spec["role"],
            "path": spec["path"],
            "size": size,
            "sha256": digest,
            "root_copy_sha256_matches": True,
            "file_count": len(files),
            "param_sfo": sfo,
            "extracted_metadata_files": extracted_meta,
        }

    # Compare file lists between JA and KO
    ja_inv = json.loads((ROOT / SOURCES_SPEC["ja"]["inventory_manifest"]).read_text(encoding="utf-8"))["files"]
    ko_inv = json.loads((ROOT / SOURCES_SPEC["ko"]["inventory_manifest"]).read_text(encoding="utf-8"))["files"]
    ja_map = {f["path"]: f for f in ja_inv}
    ko_map = {f["path"]: f for f in ko_inv}
    common_paths = sorted(set(ja_map) & set(ko_map))
    only_ja = sorted(set(ja_map) - set(ko_map))
    only_ko = sorted(set(ko_map) - set(ja_map))
    identical_files = [p for p in common_paths if ja_map[p]["sha256"] == ko_map[p]["sha256"]]
    differing_files = [
        {
            "path": p,
            "ja_size": ja_map[p]["size"],
            "ko_size": ko_map[p]["size"],
            "ja_sha256": ja_map[p]["sha256"],
            "ko_sha256": ko_map[p]["sha256"],
        }
        for p in common_paths
        if ja_map[p]["sha256"] != ko_map[p]["sha256"]
    ]
    survey_report["disc_comparison"] = {
        "common_file_count": len(common_paths),
        "identical_file_count": len(identical_files),
        "differing_file_count": len(differing_files),
        "only_in_ja": only_ja,
        "only_in_ko": only_ko,
        "differing_files": differing_files,
    }

    save_json(ROOT / "manifests/sources.json", sources_manifest)
    save_json(ROOT / "qa/reports/source_survey.json", survey_report)
    print(
        json.dumps(
            {
                "ja_disc_id": survey_report["sources"]["ja"]["param_sfo"].get("DISC_ID"),
                "ko_disc_id": survey_report["sources"]["ko"]["param_sfo"].get("DISC_ID"),
                "ja_files": survey_report["sources"]["ja"]["file_count"],
                "ko_files": survey_report["sources"]["ko"]["file_count"],
                "common_files": len(common_paths),
                "identical_files": len(identical_files),
                "differing_files": len(differing_files),
                "only_in_ja_count": len(only_ja),
                "only_in_ko_count": len(only_ko),
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
