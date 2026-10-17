# -*- coding: utf-8 -*-
"""
scan_cutscenes.py
Scans cutscene lines 6501..6942 in chunks of 50, outputting them for review.
"""
import json

with open("workspace/translation/localdat_ja_ko_aligned.jsonl", "r", encoding="utf-8") as f:
    entries = {json.loads(line)["ko_id"]: json.loads(line) for line in f if line.strip()}

def dump_range(start, end, out_path):
    with open(out_path, "w", encoding="utf-8") as f:
        for kid in range(start, end + 1):
            if kid in entries:
                e = entries[kid]
                f.write(f"[{kid}]\nJA: {e['ja_text']}\nKO: {e['ko_text']}\n\n")

dump_range(6501, 6600, "workspace/analysis/cs_6501_6600.txt")
dump_range(6601, 6700, "workspace/analysis/cs_6601_6700.txt")
dump_range(6701, 6800, "workspace/analysis/cs_6701_6800.txt")
dump_range(6801, 6942, "workspace/analysis/cs_6801_6942.txt")
print("Cutscenes dumped into 4 chunks.")

