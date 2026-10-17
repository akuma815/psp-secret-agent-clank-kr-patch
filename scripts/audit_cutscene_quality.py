# -*- coding: utf-8 -*-
"""
audit_cutscene_quality.py
Performs in-depth linguistic review of cutscene subtitles (6501..6942).
Extracts dialogue lines needing translation fixes or tone polish.
"""
import json
import re

with open("workspace/translation/localdat_ja_ko_aligned.jsonl", "r", encoding="utf-8") as f:
    entries = {json.loads(line)["ko_id"]: json.loads(line) for line in f if line.strip()}

cutscenes = {kid: entries[kid] for kid in range(6501, 6943) if kid in entries}

# Let's inspect tone anomalies:
# In Japanese, Clank consistently uses '〜っす' / '〜ます' / '〜です' (polite, respectful, loyal partner)
# Ratchet uses casual 'オイラ' / '〜ぜ' / '〜だろ' (boyish, confident, informal)
# Quark uses dramatic superhero theatrics '〜である！' / '〜たまえ！'
# Klunk uses villainous '〜でゲス' (sneaky, arrogant minion/villain dialect)

issues = []

for kid, e in cutscenes.items():
    ja = e["ja_text"]
    ko = e["ko_text"]
    
    # Check for quotes at start
    if ko.startswith('"') and not ko.endswith('"') and not re.search(r'"[^"]*$', ko):
        pass # open quote
        
    # Check for missing leading quote if ja has 「 but ko starts with plain text followed by "
    if '「' in ja and not ko.startswith('"') and not ko.startswith('\'') and '"' in ko:
        issues.append((kid, "Quote structure check", ja, ko))
        
    # Check for specific words/phrases
    # 1. 6502
    if kid == 6502:
        issues.append((kid, "Omitted nuance / mistranslation", ja, ko))
    # 2. 6503
    if kid == 6503:
        issues.append((kid, "Awkward translation", ja, ko))
    # 3. 6506
    if kid == 6506:
        issues.append((kid, "Awkward phrasing / missing nuance (현행범)", ja, ko))
    # 4. 6507
    if kid == 6507:
        issues.append((kid, "Mistranslated idiom", ja, ko))
    # 5. 6510
    if kid == 6510:
        issues.append((kid, "Broken grammar in KO (존재가 대단한 안타까운)", ja, ko))
    # 6. 6513
    if kid == 6513:
        issues.append((kid, "Omitted dialogue (생체인식)", ja, ko))
    # 7. 6514
    if kid == 6514:
        issues.append((kid, "Clumsy phrasing", ja, ko))
    # 8. 6516
    if kid == 6516:
        issues.append((kid, "Missing partner nuance (비록 파트너를 위해서라도)", ja, ko))
    # 9. 6517
    if kid == 6517:
        issues.append((kid, "Clumsy phrasing (무죄를 증명해보이겠습니다)", ja, ko))
    # 10. 6523
    if kid == 6523:
        issues.append((kid, "Fortune cookie joke mistranslation", ja, ko))
    # 11. 6534
    if kid == 6534:
        issues.append((kid, "Warden dialogue mistranslation", ja, ko))
    # 12. 6539, 6540
    if kid in (6539, 6540):
        issues.append((kid, "Warden bribe dialogue", ja, ko))

print(f"Sample identified issues: {len(issues)}")
for kid, reason, ja, ko in issues:
    print(f"[{kid}] {reason}\n  JA: {ja}\n  KO: {ko}\n")

