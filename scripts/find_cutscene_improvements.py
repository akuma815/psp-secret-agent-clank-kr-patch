# -*- coding: utf-8 -*-
"""
find_cutscene_improvements.py
Compares cutscene lines and drafts high-quality Korean dialogue translations
that fix errors, preserve character voices, and improve natural flow.
"""
import json

with open("workspace/translation/localdat_ja_ko_aligned.jsonl", "r", encoding="utf-8") as f:
    entries = {json.loads(line)["ko_id"]: json.loads(line) for line in f if line.strip()}

# Let's inspect specific scenes
scenes = [
    ("Prologue Museum / News Report", 6501, 6520),
    ("Prison Yard & Warden", 6521, 6555),
    ("Quark & Clank Meeting", 6556, 6595),
    ("Casino & Le Paradox / Bar Scene", 6596, 6650),
    ("Slime Cognito / Prison Phone Call", 6651, 6700),
    ("Quark Show / Opera House", 6701, 6760),
    ("Underwater / Graveyard / Laboratory", 6761, 6820),
    ("Boss Clunk Encounter / Showdown", 6821, 6890),
    ("Ending & Epilogue", 6891, 6942),
]

for name, s, e in scenes:
    print(f"=== {name} ({s}..{e}) ===")
    for kid in range(s, min(e + 1, s + 5)):
        if kid in entries:
            ja = entries[kid]["ja_text"]
            ko = entries[kid]["ko_text"]
            print(f"[{kid}] JA: {ja}")
            print(f"     KO: {ko}")

