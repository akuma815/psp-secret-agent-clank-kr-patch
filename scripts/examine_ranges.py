# -*- coding: utf-8 -*-
"""
examine_ranges.py
Examines structure of 6501..6942 and 7000..7450.
"""
import json

with open("workspace/translation/localdat_ja_ko_aligned.jsonl", "r", encoding="utf-8") as f:
    entries = [json.loads(line) for line in f if line.strip()]

by_id = {e["ko_id"]: e for e in entries}

print("=== Cutscenes 6501..6942 sample boundaries ===")
for kid in [6501, 6550, 6600, 6650, 6700, 6750, 6800, 6850, 6900, 6942]:
    if kid in by_id:
        print(f"[{kid}] KO: {by_id[kid]['ko_text'][:50]}")

print("\n=== Range 7000..7450 sample boundaries ===")
for kid in range(7000, 7451, 30):
    if kid in by_id:
        print(f"[{kid}] JA: {by_id[kid]['ja_text'][:40]} | KO: {by_id[kid]['ko_text'][:40]}")

