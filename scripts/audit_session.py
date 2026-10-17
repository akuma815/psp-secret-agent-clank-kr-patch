"""Audit session artifacts, source ISO hashes, UTF-8 encoding, and handoff documents."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(8 * 1024 * 1024):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    manifest = json.loads((ROOT / "manifests/sources.json").read_text(encoding="utf-8"))
    for key, entry in manifest["sources"].items():
        iso = ROOT / entry["path"]
        root_iso = ROOT / entry["received_filename"]
        if iso.stat().st_size != entry["size"] or sha256_file(iso) != entry["sha256"]:
            raise ValueError(f"Preserved ISO mismatch for {key}")
        if root_iso.stat().st_size != entry["size"] or sha256_file(root_iso) != entry["sha256"]:
            raise ValueError(f"Root ISO mismatch for {key}")

    tracked_files = [
        "AGENTS.md",
        "README.md",
        ".gitignore",
        "manifests/sources.json",
        "manifests/iso_inventory_ja.json",
        "manifests/iso_inventory_ko.json",
        "scripts/survey.py",
        "scripts/analyze_localdat.py",
        "scripts/audit_translation_diff.py",
        "scripts/build_patched_localdat.py",
        "scripts/build_iso.py",
        "scripts/audit_session.py",
        "config/glossary.json",
        "extracted/text/localdat_ja.jsonl",
        "extracted/text/localdat_ko.jsonl",
        "extracted/text/helplocaldat_ja.jsonl",
        "extracted/text/helplocaldat_ko.jsonl",
        "workspace/translation/localdat_ja_ko_aligned.jsonl",
        "workspace/translation/helplocaldat_ja_ko_aligned.jsonl",
        "workspace/translation/translation_patches.json",
        "workspace/analysis/translation_diff_report.md",
        "qa/reports/source_survey.json",
        "qa/reports/localdat_analysis.json",
        "qa/reports/translation_diff_audit.json",
        "qa/reports/build_localdat_report.json",
        "qa/reports/build_iso_report.json",
        "docs/LOCALDAT_ANALYSIS_2026-10-16.md",
        "docs/archive/HANDOFF_2026-10-16_init.md",
        "docs/HANDOFF.md",
        "docs/HANDOFF_2026-10-16.md",
        "docs/HANDOFF_2026-10-17.md",
    ]
    hashes: dict[str, str] = {}
    for rel in tracked_files:
        p = ROOT / rel
        if not p.exists():
            raise FileNotFoundError(f"Missing required project file: {rel}")
        text = p.read_text(encoding="utf-8")
        if "\ufffd" in text:
            raise ValueError(f"Replacement character U+FFFD found in {rel}")
        hashes[rel] = sha256_file(p)

    out_path = ROOT / "qa/reports/session_audit.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    report = {
        "schema_version": 1,
        "date_kst": "2026-10-16",
        "sources_verified": True,
        "utf8_verified": True,
        "tracked_file_hashes": hashes,
    }
    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"audit_passed": True, "tracked_files": len(hashes)}, ensure_ascii=False))


if __name__ == "__main__":
    main()

