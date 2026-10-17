#!/usr/bin/env python3
"""Extract JA<->KO terminology glossary (config/glossary.json) and generate a
comprehensive translation diff & defect audit report across LOCALDAT and HELPLOCALDAT.
"""

from __future__ import annotations

import json
import pathlib
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone, timedelta
from typing import Any

KST = timezone(timedelta(hours=9))
ROOT = pathlib.Path(__file__).resolve().parent.parent

TOKEN_RE = re.compile(r"<[^>]+>")
COL_WRAP_RE = re.compile(r"^<COL:02>(.*)<COL:01>$", re.DOTALL)

# Valid grammatical suffixes after a <COL:02>keyword<COL:01> tag
VALID_SUFFIXES = {
    "은", "는", "이", "가", "을", "를", "의", "에", "에서", "에게", "께", "한테", "으로", "로",
    "과", "와", "도", "만", "까지", "부터", "처럼", "보다", "마다", "조차", "마저", "이나", "나",
    "이라도", "라도", "이라", "라", "이란", "란", "이고", "고", "이며", "며", "입니다", "이다",
    "인가", "인가요", "인지", "인", "들", "들이", "들은", "들을", "들의", "들에게", "들로", "들과",
    "하고", "랑", "이랑", "에는", "에도", "에서는", "으로도", "로는", "로서", "로써", "으로부터", "로부터",
    "에게로", "에서의", "엔", "에요", "이에요", "에서도",
    # Verbal / derivational suffixes legitimately attached to action/noun keywords ("추적", "충전", "화염", "냉동")
    "해서", "하여", "했더니", "하세요", "합니다", "하는", "시키고", "시킬", "시키기", "해야", "하면", "하려면",
}


def strip_tokens(text: str) -> str:
    return TOKEN_RE.sub("", text or "")


def strip_outer_col(text: str) -> str:
    s = (text or "").strip()
    m = COL_WRAP_RE.match(s)
    if m:
        return m.group(1)
    return strip_tokens(s)


def classify_keyword_subkind(ko_id: int) -> str:
    if ko_id in (36, 172):
        return "format_control_template"
    if 37 <= ko_id <= 62:
        return "ammo_pickup_noun"
    if 63 <= ko_id <= 116 or 273 <= ko_id <= 274:
        return "weapon_gadget_item"
    if 118 <= ko_id <= 167:
        return "weapon_mod_element_prefix"
    if 168 <= ko_id <= 171:
        return "collectible_bolt"
    if 173 <= ko_id <= 263:
        return "planet_location_chapter"
    if 264 <= ko_id <= 272:
        return "playable_character"
    return "misc_keyword"


def find_midword_col_collisions(rows: list[dict[str, Any]], source_name: str) -> list[dict[str, Any]]:
    """Find places where <COL:02>...<COL:01> splits an unrelated Korean compound word."""
    collisions: list[dict[str, Any]] = []
    pat = re.compile(r"([가-힣]*)<COL:02>([^<\n]+)<COL:01>([가-힣]*)")
    for r in rows:
        ko = r["ko_text"]
        for m in pat.finditer(ko):
            prefix, kw, suffix = m.group(1), m.group(2), m.group(3)
            if not prefix and not suffix:
                continue
            # Case 1: Hangul prefix immediately before <COL:02> (e.g. 축<COL:02>전기<COL:01>, 주파<COL:02>수로<COL:01>)
            is_collision = False
            reason = ""
            if prefix:
                is_collision = True
                reason = f"prefix_attached:{prefix}+<{kw}>"
            elif suffix and suffix not in VALID_SUFFIXES:
                is_collision = True
                reason = f"non_particle_suffix:<{kw}>+{suffix}"

            if is_collision:
                collisions.append(
                    {
                        "source": source_name,
                        "ko_id": r["ko_id"],
                        "ja_id": r["ja_id"],
                        "matched_fragment": m.group(0),
                        "keyword": kw,
                        "prefix": prefix,
                        "suffix": suffix,
                        "reason": reason,
                        "ja_text": r["ja_text"],
                        "ko_text": ko,
                    }
                )
    return collisions


def find_josa_mismatches(rows: list[dict[str, Any]], source_name: str) -> list[dict[str, Any]]:
    """Find clear Korean batchim/josa mismatches such as '흡입와' (batchim + 와 instead of 과)."""
    issues: list[dict[str, Any]] = []
    # Check Hangul syllable immediately followed by 와/과/을/를 followed by space or punctuation
    pat = re.compile(r"([가-힣]{2,})(와|과|을|를)(?=[\s.,!?\"']|$)")
    # Exclude common non-particle words ending in 와/과/을/를 (e.g. 도와, 통과, 결과, 효과, 사과, 마을, 겨울, 거울, 비늘, 오늘)
    EXEMPT_WORDS = {
        "도와", "통과", "결과", "효과", "사과", "일과", "초과", "부과", "전과", "경과", "여과", "다과",
        "마을", "겨울", "거울", "비늘", "오늘", "하늘", "바늘", "그늘", "마늘", "노을", "방울", "망울",
        "이슬", "구슬", "사슬", "보물", "괴물", "건물", "동물", "식물", "인물", "유물", "선물", "눈물",
        "우물", "약물", "독물", "화물", "기물", "폐기물", "사출물", "실험물", "장애물", "폭발물",
        "확률을", "전류를", "정보를", "데이터를",
    }
    for r in rows:
        ko_clean = strip_tokens(r["ko_text"])
        for m in pat.finditer(ko_clean):
            stem, josa = m.group(1), m.group(2)
            full_word = stem + josa
            if full_word in EXEMPT_WORDS or stem.endswith(("하", "되", "보", "주", "오", "가", "나", "마")):
                continue
            last_char = stem[-1]
            jong = (ord(last_char) - 0xAC00) % 28
            has_batchim = jong != 0
            # Strict check: batchim + '와' or batchim + '를', or no-batchim + '을'
            if has_batchim and josa in ("와", "를"):
                issues.append(
                    {
                        "source": source_name,
                        "ko_id": r["ko_id"],
                        "ja_id": r["ja_id"],
                        "word": full_word,
                        "expected": stem + ("과" if josa == "와" else "을"),
                        "ja_text": r["ja_text"],
                        "ko_text": r["ko_text"],
                    }
                )
            elif (not has_batchim) and josa == "을":
                issues.append(
                    {
                        "source": source_name,
                        "ko_id": r["ko_id"],
                        "ja_id": r["ja_id"],
                        "word": full_word,
                        "expected": stem + "를",
                        "ja_text": r["ja_text"],
                        "ko_text": r["ko_text"],
                    }
                )
    return issues


def main() -> int:
    loc_path = ROOT / "workspace/translation/localdat_ja_ko_aligned.jsonl"
    help_path = ROOT / "workspace/translation/helplocaldat_ja_ko_aligned.jsonl"

    loc_rows = [json.loads(line) for line in loc_path.read_text(encoding="utf-8").splitlines()]
    help_rows = [json.loads(line) for line in help_path.read_text(encoding="utf-8").splitlines()]

    # 1. Build Glossary (config/glossary.json)
    keyword_entries = []
    for r in sorted(
        (row for row in loc_rows if row["category"] == "keyword_glossary_colored" and row["ko_id"] != 117),
        key=lambda x: x["ko_id"],
    ):
        keyword_entries.append(
            {
                "id": r["ko_id"],
                "subkind": classify_keyword_subkind(r["ko_id"]),
                "ja_raw": r["ja_text"],
                "ko_raw": r["ko_text"],
                "ja_term": strip_outer_col(r["ja_text"]),
                "ko_term": strip_outer_col(r["ko_text"]),
            }
        )

    boss_names = [
        {
            "id": r["ko_id"],
            "ja_term": strip_tokens(r["ja_text"]),
            "ko_term": strip_tokens(r["ko_text"]),
        }
        for r in sorted((row for row in loc_rows if row["category"] == "character_boss_name"), key=lambda x: x["ko_id"])
    ]

    savedata_locations = [
        {
            "ko_id": r["ko_id"],
            "ja_id": r["ja_id"],
            "ja_title": r["ja_text"],
            "ko_title": r["ko_text"],
        }
        for r in loc_rows
        if r["format"] == "utf8_savedata" and r["ko_id"] >= 752
    ]

    glossary = {
        "schema_version": 1,
        "generated_at": datetime.now(KST).isoformat(timespec="seconds"),
        "description": "JA (UCJS10084) <-> KO (UCKS45096) aligned terminology glossary extracted from LOC_DATA",
        "counts": {
            "colored_keywords": len(keyword_entries),
            "character_boss_names": len(boss_names),
            "savedata_stage_titles": len(savedata_locations),
        },
        "character_boss_names": boss_names,
        "colored_keywords": keyword_entries,
        "savedata_stage_titles": savedata_locations,
    }

    glossary_path = ROOT / "config/glossary.json"
    glossary_path.parent.mkdir(parents=True, exist_ok=True)
    glossary_path.write_text(json.dumps(glossary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # 2. Collect Tier 1: Critical Broken Macros, Untranslated Strings, Raw JA Remnants
    tier1_critical: list[dict[str, Any]] = []
    for src, rows in [("LOCALDAT", loc_rows), ("HELPLOCALDAT", help_rows)]:
        for r in rows:
            ko = r["ko_text"]
            ja = r["ja_text"] or ""
            if "_[" in ko:
                tier1_critical.append(
                    {
                        "source": src,
                        "ko_id": r["ko_id"],
                        "ja_id": r["ja_id"],
                        "issue_type": "broken_icon_or_tm_macro",
                        "ja_text": ja,
                        "ko_text": ko,
                    }
                )
            elif "<JA93:" in ko:
                tier1_critical.append(
                    {
                        "source": src,
                        "ko_id": r["ko_id"],
                        "ja_id": r["ja_id"],
                        "issue_type": "raw_ja_bytes_in_ko",
                        "ja_text": ja,
                        "ko_text": ko,
                    }
                )
            elif r["ko_id"] in (587, 742, 743) and src == "LOCALDAT":
                tier1_critical.append(
                    {
                        "source": src,
                        "ko_id": r["ko_id"],
                        "ja_id": r["ja_id"],
                        "issue_type": "untranslated_english_in_ko",
                        "ja_text": ja,
                        "ko_text": ko,
                    }
                )

    # 3. Collect Tier 2: Mid-word <COL:02> Auto-Highlighter Collisions
    tier2_collisions = find_midword_col_collisions(loc_rows, "LOCALDAT") + find_midword_col_collisions(
        help_rows, "HELPLOCALDAT"
    )

    # 4. Collect Tier 3: Typos, Unmatched Quotes, Batchim/Josa Mismatches, Mistranslated Tokens
    tier3_typos: list[dict[str, Any]] = []
    for src, rows in [("LOCALDAT", loc_rows), ("HELPLOCALDAT", help_rows)]:
        for r in rows:
            ko = r["ko_text"]
            ja = r["ja_text"] or ""
            if "킬l!" in ko:
                tier3_typos.append(
                    {
                        "source": src,
                        "ko_id": r["ko_id"],
                        "ja_id": r["ja_id"],
                        "issue_type": "stray_ascii_typo",
                        "detail": "킬l! -> 킬!",
                        "ja_text": ja,
                        "ko_text": ko,
                    }
                )
            if ko.count("'") % 2 == 1:
                tier3_typos.append(
                    {
                        "source": src,
                        "ko_id": r["ko_id"],
                        "ja_id": r["ja_id"],
                        "issue_type": "unmatched_single_quote_excel_strip",
                        "detail": "Missing opening single quote stripped by spreadsheet export",
                        "ja_text": ja,
                        "ko_text": ko,
                    }
                )
            if "가져다 좋으세요" in ko:
                tier3_typos.append(
                    {
                        "source": src,
                        "ko_id": r["ko_id"],
                        "ja_id": r["ja_id"],
                        "issue_type": "hangul_typo",
                        "detail": "가져다 좋으세요 -> 가져다 놓으세요",
                        "ja_text": ja,
                        "ko_text": ko,
                    }
                )
            if "#오류" in ko:
                tier3_typos.append(
                    {
                        "source": src,
                        "ko_id": r["ko_id"],
                        "ja_id": r["ja_id"],
                        "issue_type": "mistranslated_floor_and_tag",
                        "detail": "JA 'フロア -1 ... [エラー]' -> KO '<COL:02>1층<COL:01> ... #오류'",
                        "ja_text": ja,
                        "ko_text": ko,
                    }
                )

    josa_issues = find_josa_mismatches(loc_rows, "LOCALDAT") + find_josa_mismatches(help_rows, "HELPLOCALDAT")
    for ji in josa_issues:
        tier3_typos.append(
            {
                "source": ji["source"],
                "ko_id": ji["ko_id"],
                "ja_id": ji["ja_id"],
                "issue_type": "josa_batchim_mismatch",
                "detail": f"{ji['word']} -> {ji['expected']}",
                "ja_text": ji["ja_text"],
                "ko_text": ji["ko_text"],
            }
        )

    # 5. Category summary statistics
    category_summary: list[dict[str, Any]] = []
    for src, rows in [("LOCALDAT", loc_rows), ("HELPLOCALDAT", help_rows)]:
        by_cat: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for r in rows:
            by_cat[r["category"]].append(r)
        for cat, items in by_cat.items():
            dnt_count = sum(1 for x in items if "untranslated_or_dummy" in x["flags"])
            btn_diff = sum(1 for x in items if "button_icon_diff" in x["flags"])
            category_summary.append(
                {
                    "source": src,
                    "category": cat,
                    "total_entries": len(items),
                    "active_translatable_entries": len(items) - dnt_count,
                    "dummy_or_dnt_entries": dnt_count,
                    "button_icon_diffs": btn_diff,
                    "id_range": f"{min(x['ko_id'] for x in items)}..{max(x['ko_id'] for x in items)}",
                }
            )

    audit_data = {
        "generated_at": datetime.now(KST).isoformat(timespec="seconds"),
        "status": "ok",
        "glossary_path": "config/glossary.json",
        "counts": {
            "glossary_colored_keywords": len(keyword_entries),
            "tier1_critical_count": len(tier1_critical),
            "tier2_midword_col_collision_count": len(tier2_collisions),
            "tier3_typo_and_josa_count": len(tier3_typos),
            "total_categories": len(category_summary),
        },
        "tier1_critical": tier1_critical,
        "tier2_midword_col_collisions": tier2_collisions,
        "tier3_typos_and_josa": tier3_typos,
        "category_summary": category_summary,
    }

    audit_json_path = ROOT / "qa/reports/translation_diff_audit.json"
    audit_json_path.write_text(json.dumps(audit_data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # 6. Generate Markdown Report (workspace/analysis/translation_diff_report.md)
    md_lines = [
        "# 일본판(`UCJS10084`) 기준 한국판(`UCKS45096`) 번역 감사 및 용어 대조 보고서",
        "",
        f"- **생성 시각**: `{audit_data['generated_at']}`",
        "- **추출 용어집**: [`config/glossary.json`](../../config/glossary.json)",
        "- **기계 판독 감사 보고서**: [`qa/reports/translation_diff_audit.json`](../../qa/reports/translation_diff_audit.json)",
        "",
        "---",
        "",
        "## 1. 카테고리별 전체 대사 분포 (`3,083`개 엔트리)",
        "",
        "| 파일 | 카테고리 | ID 범위 (`KO`) | 전체 수 | 실제 번역 대상 | 더미/`DNT` | 버튼 아이콘 차이 |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: |",
    ]
    for cs in category_summary:
        md_lines.append(
            f"| `{cs['source']}` | `{cs['category']}` | `{cs['id_range']}` | {cs['total_entries']} | "
            f"**{cs['active_translatable_entries']}** | {cs['dummy_or_dnt_entries']} | {cs['button_icon_diffs']} |"
        )

    md_lines.extend(
        [
            "",
            "---",
            "",
            f"## 2. Tier 1 — 즉시 수정 필수: 깨진 매크로·미번역 영문·일본어 더미 잔재 (`{len(tier1_critical)}`건)",
            "",
            "| 파일 | `KO ID` (`JA ID`) | 유형 | 일본판 원문 (`UCJS10084`) | 한국판 현행 (`UCKS45096`) |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for item in tier1_critical:
        ja_s = item["ja_text"].replace("\n", "\\n").replace("|", "\\|")
        ko_s = item["ko_text"].replace("\n", "\\n").replace("|", "\\|")
        md_lines.append(
            f"| `{item['source']}` | `{item['ko_id']}` (`{item['ja_id']}`) | `{item['issue_type']}` | {ja_s} | {ko_s} |"
        )

    md_lines.extend(
        [
            "",
            "---",
            "",
            f"## 3. Tier 2 — 공식 한국판 자동 색칠(`<COL:02>`) 단어 중간 깨짐 오류 (`{len(tier2_collisions)}`건)",
            "",
            "공식 한국판 빌드 당시 키워드 사전(`ID 2..274`)을 단순 부분 문자열 치환으로 적용하여 복합어 중간이 노란색(`<COL:02>...<COL:01>`)으로 분리된 오류 목록입니다.",
            "",
            "| 파일 | `KO ID` (`JA ID`) | 깨진 어절 | 원인 분류 | 한국판 현행 문장 |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for col in tier2_collisions:
        frag = col["matched_fragment"].replace("\n", "\\n").replace("|", "\\|")
        ko_s = col["ko_text"].replace("\n", "\\n").replace("|", "\\|")
        md_lines.append(
            f"| `{col['source']}` | `{col['ko_id']}` (`{col['ja_id']}`) | `{frag}` | `{col['reason']}` | {ko_s} |"
        )

    md_lines.extend(
        [
            "",
            "---",
            "",
            f"## 4. Tier 3 — 한국판 오타·따옴표 누락·조사(받침) 오류·오역 태그 (`{len(tier3_typos)}`건)",
            "",
            "| 파일 | `KO ID` (`JA ID`) | 오류 유형 | 교정 내역 | 일본판 원문 | 한국판 현행 |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    for t in tier3_typos:
        ja_s = (t["ja_text"] or "").replace("\n", "\\n").replace("|", "\\|")
        ko_s = t["ko_text"].replace("\n", "\\n").replace("|", "\\|")
        det = t["detail"].replace("|", "\\|")
        md_lines.append(
            f"| `{t['source']}` | `{t['ko_id']}` (`{t['ja_id']}`) | `{t['issue_type']}` | `{det}` | {ja_s} | {ko_s} |"
        )

    md_lines.extend(
        [
            "",
            "---",
            "",
            "## 5. 주요 고유명사·무기·행성·보스 용어 대조 요약 (발췌)",
            "",
            "전체 240개 색상 키워드 및 세이브데이터 지명 대조표는 [`config/glossary.json`](../../config/glossary.json)에 수록되어 있습니다.",
            "",
            "### 5.1 캐릭터 및 보스 명칭 (`ID 264..272, 6001..6005`)",
            "",
            "| ID | 일본판 (`UCJS10084`) | 한국판 (`UCKS45096`) |",
            "| ---: | --- | --- |",
        ]
    )
    for kw in keyword_entries:
        if kw["subkind"] == "playable_character":
            md_lines.append(f"| `{kw['id']}` | {kw['ja_term']} | {kw['ko_term']} |")
    for b in boss_names:
        md_lines.append(f"| `{b['id']}` | {b['ja_term']} | {b['ko_term']} |")

    md_lines.extend(
        [
            "",
            "### 5.2 무기 및 가젯 명칭 (`ID 63..116, 273..274` 중 주요 항목)",
            "",
            "| ID | 일본판 (`UCJS10084`) | 한국판 (`UCKS45096`) |",
            "| ---: | --- | --- |",
        ]
    )
    for kw in keyword_entries:
        if kw["subkind"] == "weapon_gadget_item":
            md_lines.append(f"| `{kw['id']}` | {kw['ja_term']} | {kw['ko_term']} |")

    md_path = ROOT / "workspace/analysis/translation_diff_report.md"
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text("\n".join(md_lines) + "\n", encoding="utf-8")

    print(
        json.dumps(
            {
                "status": "ok",
                "glossary_path": "config/glossary.json",
                "audit_json": "qa/reports/translation_diff_audit.json",
                "audit_markdown": "workspace/analysis/translation_diff_report.md",
                "counts": audit_data["counts"],
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

