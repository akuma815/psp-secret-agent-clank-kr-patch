# -*- coding: utf-8 -*-
"""
find_profile_defects.py
Systematically searches 7000..7450 for typos, mistranslations, and unnatural phrasing.
"""
import json
import re

with open("workspace/translation/localdat_ja_ko_aligned.jsonl", "r", encoding="utf-8") as f:
    entries = {json.loads(line)["ko_id"]: json.loads(line) for line in f if line.strip()}

profiles = {kid: entries[kid] for kid in range(7000, 7451) if kid in entries}

findings = []

for kid, e in sorted(profiles.items()):
    ja = e["ja_text"]
    ko = e["ko_text"]
    
    # 1. Spelling / Typo checks
    if "꺼에요" in ko:
        findings.append((kid, "Typo '꺼에요' -> '거예요'", ja, ko))
    if "소움" in ko:
        findings.append((kid, "Typo '소움' -> '소음'", ja, ko))
    if "안되서" in ko:
        findings.append((kid, "Typo '안되서' -> '안 돼서'", ja, ko))
    if "그린하우스 가스" in ko:
        findings.append((kid, "Unnatural loanword '그린하우스 가스' -> '온실가스'", ja, ko))
    if "엑세서리" in ko:
        findings.append((kid, "Typo '엑세서리' -> '액세서리'", ja, ko))
    if "핀스트라이트" in ko and "ピンストライプ" in ja:
        findings.append((kid, "Typo '핀스트라이트' -> '핀스트라이프'", ja, ko))
    if "중안 보안" in ko:
        findings.append((kid, "Typo '중안 보안' -> '중앙 보안'", ja, ko))
    if "고정 하기" in ko:
        findings.append((kid, "Spacing '고정 하기' -> '고정하기'", ja, ko))
    if "좋을 꺼에요" in ko:
        findings.append((kid, "Typo '좋을 꺼에요' -> '좋을 거예요'", ja, ko))
    if "비프" in ko and "ビーフ" in ja:
        # Check context of 7243: '말 없는 마차의 비프'
        pass

print(f"Total specific pattern findings in 7000..7450: {len(findings)}")
for f in findings:
    print(f"[{f[0]}] {f[1]}\n  JA: {f[2]}\n  KO: {f[3]}\n")

