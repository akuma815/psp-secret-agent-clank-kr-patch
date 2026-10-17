# -*- coding: utf-8 -*-
"""
audit_help_quality.py
Inspects helplocaldat_ja_ko_aligned.jsonl for translation quality and defects.
"""
import json
import re

with open("workspace/translation/helplocaldat_ja_ko_aligned.jsonl", "r", encoding="utf-8") as f:
    help_entries = [json.loads(line) for line in f if line.strip()]

with open("workspace/translation/translation_patches.json", "r", encoding="utf-8") as f:
    existing_patches = json.load(f)

existing_help_ids = {p["ko_id"] for p in existing_patches if p.get("source") == "HELPLOCALDAT"}

print(f"Total HELPLOCALDAT entries: {len(help_entries)}")
print(f"Already patched HELPLOCALDAT entries: {len(existing_help_ids)}")

# Check for further issues in help entries
suspicious = []
for e in help_entries:
    kid = e["ko_id"]
    ja = e["ja_text"]
    ko = e["ko_text"]
    
    # Check for untranslated macros or broken tokens
    if "_[" in ko:
        suspicious.append((kid, "Broken macro _[...]", ja, ko))
    if "#오류" in ko:
        suspicious.append((kid, "#오류 raw string", ja, ko))
    if "꺼에요" in ko or "할꺼" in ko or "볼꺼" in ko:
        suspicious.append((kid, "Typo 꺼 -> 거", ja, ko))
    if "가져다 좋으세요" in ko:
        suspicious.append((kid, "Typo 좋으세요 -> 놓으세요", ja, ko))
    if "엉덩이을" in ko:
        suspicious.append((kid, "Josa error 엉덩이을 -> 엉덩이를", ja, ko))
    if "패드을" in ko:
        suspicious.append((kid, "Josa error 패드을 -> 패드를", ja, ko))
    if re.search(r'<COL:02>[가-힣]+<COL:01>[가-힣]', ko):
        # mid-word split
        m = re.search(r'[가-힣]*<COL:02>[가-힣]+<COL:01>[가-힣]+', ko)
        if m:
            suspicious.append((kid, f"Mid-word color collision: {m.group(0)}", ja, ko))

print(f"Suspicious help entries: {len(suspicious)}")
for s in suspicious:
    status = "ALREADY_PATCHED" if s[0] in existing_help_ids else "NEW_DEFECT"
    print(f"[{s[0]}] ({status}) {s[1]}\n  KO: {s[3]}\n")

