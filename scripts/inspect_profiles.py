# -*- coding: utf-8 -*-
"""
inspect_profiles.py
Inspects 7000..7450: character/enemy profiles and descriptions.
Checks for typos, awkward translations, and tone issues.
"""
import json
import re

with open("workspace/translation/localdat_ja_ko_aligned.jsonl", "r", encoding="utf-8") as f:
    entries = {json.loads(line)["ko_id"]: json.loads(line) for line in f if line.strip()}

profiles = {kid: entries[kid] for kid in range(7000, 7451) if kid in entries}
print(f"Total entries in 7000..7450: {len(profiles)}")

# Print every 20th entry
for kid in sorted(profiles.keys()):
    if kid % 25 == 0 or kid in (7000, 7100, 7200, 7300, 7400, 7450):
        e = profiles[kid]
        print(f"[{kid}] JA: {e['ja_text']}")
        print(f"       KO: {e['ko_text']}\n")

