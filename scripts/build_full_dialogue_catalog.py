# -*- coding: utf-8 -*-
"""
build_full_dialogue_catalog.py
Analyzes cutscenes (6501..6942) and dialogues (7000..7450)
Outputs an extensive side-by-side text analysis.
"""
import json

def main():
    with open("workspace/translation/localdat_ja_ko_aligned.jsonl", "r", encoding="utf-8") as f:
        entries = [json.loads(line) for line in f if line.strip()]

    by_id = {e["ko_id"]: e for e in entries}

    out_file = "workspace/analysis/dialogue_full_comparison.txt"
    with open(out_file, "w", encoding="utf-8") as f:
        f.write("=== FULL DIALOGUE & CUTSCENE COMPARISON (6501..6942 & 7000..7450) ===\n\n")
        
        # 1. Cutscenes
        f.write("--- PART 1: CUTSCENES (6501..6942) ---\n\n")
        for kid in range(6501, 6943):
            if kid in by_id:
                e = by_id[kid]
                f.write(f"ID: {kid}\n")
                f.write(f"JA: {e['ja_text']}\n")
                f.write(f"KO: {e['ko_text']}\n")
                f.write("-" * 50 + "\n")
                
        # 2. In-game Dialogues & Profiles
        f.write("\n--- PART 2: IN-GAME PROFILES & DIALOGUES (7000..7450) ---\n\n")
        for kid in range(7000, 7451):
            if kid in by_id:
                e = by_id[kid]
                f.write(f"ID: {kid}\n")
                f.write(f"JA: {e['ja_text']}\n")
                f.write(f"KO: {e['ko_text']}\n")
                f.write("-" * 50 + "\n")

    print(f"Comparison written to {out_file}")

if __name__ == "__main__":
    main()

