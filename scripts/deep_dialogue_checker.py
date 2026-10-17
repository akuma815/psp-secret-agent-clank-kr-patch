# -*- coding: utf-8 -*-
"""
deep_dialogue_checker.py
Examines cutscenes (6501..6942) and dialogues (7000..7450)
Identifies suspicious patterns, mistranslations, awkward phrasing, and discrepancies.
"""

import json
import re

def main():
    with open("workspace/translation/localdat_ja_ko_aligned.jsonl", "r", encoding="utf-8") as f:
        localdat = [json.loads(line) for line in f if line.strip()]

    cutscenes = {e["ko_id"]: e for e in localdat if 6501 <= e["ko_id"] <= 6942}
    dialogues = {e["ko_id"]: e for e in localdat if 7000 <= e["ko_id"] <= 7450}

    print(f"Total cutscenes: {len(cutscenes)}, Total in-game dialogues: {len(dialogues)}")

    # Check for known issues and flag candidates for review:
    # 1. Particles mismatch (은/는, 이/가, 을/를, 와/과, 로/으로)
    # 2. Awkward translation patterns (e.g. "당신", "그것", literal "남는 장사가 아니다")
    # 3. Missing punctuation or quotes
    # 4. Negation checks (JA has ない / ません vs KO not having 안/않/못/없, or vice versa)
    # 5. Question mark mismatch (JA has ? / か vs KO missing ?)
    
    suspicious = []
    
    # Common Korean particle errors regex:
    # 받침 있는 글자 + 를 / 가 / 와 / 로(ㄹ 제외)
    # 받침 없는 글자 + 을 / 이 / 과 / 으로
    josa_check_patterns = [
        (r'([가-힣])을', True), # should have batchim
        (r'([가-힣])를', False), # should NOT have batchim
        (r'([가-힣])은', True),
        (r'([가-힣])는', False),
        (r'([가-힣])이', True),
        (r'([가-힣])가', False),
        (r'([가-힣])과', True),
        (r'([가-힣])와', False),
    ]

    def has_jongseong(ch):
        code = ord(ch) - 0xAC00
        if 0 <= code <= 11171:
            return (code % 28) != 0
        return None

    all_dialogue_ids = sorted(list(cutscenes.keys()) + list(dialogues.keys()))
    
    josa_errors = []
    for kid in all_dialogue_ids:
        entry = cutscenes.get(kid) or dialogues.get(kid)
        ko = entry["ko_text"]
        ja = entry["ja_text"]
        
        # Check josa
        # Strip tags like <COL:01>, <COL:02>, <BTN_...>, etc.
        clean_ko = re.sub(r'<[^>]+>', '', ko)
        
        for pat, req_jong in josa_check_patterns:
            for m in re.finditer(pat, clean_ko):
                ch = m.group(1)
                has_j = has_jongseong(ch)
                if has_j is not None and has_j != req_jong:
                    # check if false positive (e.g. '로' vs '으로' when ㄹ batchim)
                    josa_errors.append({
                        "id": kid,
                        "char": ch,
                        "matched": m.group(0),
                        "ko": ko,
                        "ja": ja
                    })

    print(f"Josa anomalies detected: {len(josa_errors)}")
    for j in josa_errors:
        print(f"[{j['id']}] {j['matched']} in '{j['ko']}'")

if __name__ == "__main__":
    main()

