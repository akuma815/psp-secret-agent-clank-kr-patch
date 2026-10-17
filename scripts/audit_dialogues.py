# -*- coding: utf-8 -*-
"""
audit_dialogues.py
Audit cutscenes (6501..6942) and in-game dialogues (7000..7450)
comparing Japanese original (UCJS10084) and Korean release (UCKS45096).
Outputs an audit report and proposed patches.
"""

import json
import os
import sys

def main():
    aligned_localdat = "workspace/translation/localdat_ja_ko_aligned.jsonl"
    aligned_help = "workspace/translation/helplocaldat_ja_ko_aligned.jsonl"
    
    entries = []
    with open(aligned_localdat, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                entries.append(json.loads(line))
                
    help_entries = []
    with open(aligned_help, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                help_entries.append(json.loads(line))
                
    print(f"Loaded {len(entries)} LOCALDAT entries and {len(help_entries)} HELPLOCALDAT entries.")
    
    cutscenes = [e for e in entries if 6501 <= e["ko_id"] <= 6942]
    dialogues = [e for e in entries if 7000 <= e["ko_id"] <= 7450]
    
    print(f"Cutscenes: {len(cutscenes)} lines")
    print(f"In-game dialogues: {len(dialogues)} lines")
    
    # Save a readable utf-8 text file of all in-game dialogues for inspection
    out_dialogues = "workspace/analysis/ingame_dialogues_raw.txt"
    with open(out_dialogues, "w", encoding="utf-8") as f:
        for d in dialogues:
            f.write(f"[{d['ko_id']} | JA:{d['ja_id']}]\n")
            f.write(f"JA: {d['ja_text']}\n")
            f.write(f"KO: {d['ko_text']}\n\n")
    print(f"Saved {out_dialogues}")

if __name__ == "__main__":
    main()

