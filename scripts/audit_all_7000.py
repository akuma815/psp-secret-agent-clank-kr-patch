# -*- coding: utf-8 -*-
"""
audit_all_7000.py
Outputs any notable differences or defects in 7000..7450.
"""
import json

with open("workspace/translation/localdat_ja_ko_aligned.jsonl", "r", encoding="utf-8") as f:
    entries = {json.loads(line)["ko_id"]: json.loads(line) for line in f if line.strip()}

profiles = {kid: entries[kid] for kid in range(7000, 7451) if kid in entries}

with open("workspace/analysis/profiles_audit.txt", "w", encoding="utf-8") as out:
    for kid, e in sorted(profiles.items()):
        ja = e["ja_text"]
        ko = e["ko_text"]
        out.write(f"[{kid}]\nJA: {ja}\nKO: {ko}\n\n")

print("Saved workspace/analysis/profiles_audit.txt")

