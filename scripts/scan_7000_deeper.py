# -*- coding: utf-8 -*-
"""
scan_7000_deeper.py
Deeper check into 7000..7450.
"""
import json
import re

with open("workspace/translation/localdat_ja_ko_aligned.jsonl", "r", encoding="utf-8") as f:
    entries = {json.loads(line)["ko_id"]: json.loads(line) for line in f if line.strip()}

profiles = {kid: entries[kid] for kid in range(7000, 7451) if kid in entries}

suspicious = []
for kid, e in sorted(profiles.items()):
    ja = e["ja_text"]
    ko = e["ko_text"]
    
    # Check for color tag collisions in 7000..7450
    # e.g., <COL:02>클립<COL:01>온이에요 (we saw KO ID 7355 before!)
    if re.search(r'<COL:02>[가-힣]+<COL:01>[가-힣]', ko):
        # tag immediately followed by hangul
        match = re.search(r'<COL:02>[가-힣]+<COL:01>[가-힣]+', ko)
        suspicious.append((kid, "Color tag mid-word split", ja, ko, match.group(0)))
        
    # Check for quotes
    if ko.startswith('"') != ko.endswith('"') and '"' in ko:
        # unbalanced quotes
        if ko.count('"') % 2 != 0:
            suspicious.append((kid, "Unbalanced double quote", ja, ko, ""))

    # Check for double spaces or trailing spaces
    if "  " in ko:
        suspicious.append((kid, "Double space", ja, ko, ""))

print(f"Suspicious count: {len(suspicious)}")
for s in suspicious[:15]:
    print(f"[{s[0]}] {s[1]}: {s[4]}\n  KO: {s[3]}\n")

