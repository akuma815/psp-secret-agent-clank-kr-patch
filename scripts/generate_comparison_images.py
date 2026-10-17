"""Generate side-by-side comparison images for Secret Agent Clank."""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

BASE = Path("g:/Downloads/Korean Traslate Project/Games/Clank  Ratchet - Maruhi Mission Ignition")
IMG_DIR = BASE / "img"
QA_DIR = BASE / "qa/screenshots"

FONT_BOLD = ImageFont.truetype("C:/Windows/Fonts/malgunbd.ttf", 16)
FONT_TITLE = ImageFont.truetype("C:/Windows/Fonts/malgunbd.ttf", 20)
FONT_SUB = ImageFont.truetype("C:/Windows/Fonts/malgun.ttf", 14)
FONT_GAME = ImageFont.truetype("C:/Windows/Fonts/malgunbd.ttf", 16)
FONT_GAME_SM = ImageFont.truetype("C:/Windows/Fonts/malgun.ttf", 15)

def draw_text_with_shadow(draw, pos, text, font, fill=(255, 255, 255), shadow=(20, 40, 90), anchor="mm"):
    x, y = pos
    for ox, oy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (1, -1), (-1, 1)]:
        draw.text((x + ox, y + oy), text, font=font, fill=shadow, anchor=anchor)
    draw.text((x, y), text, font=font, fill=fill, anchor=anchor)

def create_clank_dialogue_comparison():
    bg_path = QA_DIR / "cutscene_clank_speaking.png"
    img_base = Image.open(bg_path).convert("RGBA")
    w, h = img_base.size  # 480, 272

    # Left: Original Dialogue
    img_orig = img_base.copy()
    draw_orig = ImageDraw.Draw(img_orig)
    draw_orig.rectangle([0, 186, 480, 222], fill=(10, 15, 25, 160))
    orig_text = "아니요. 그런 건 이상한 걸 보았어요!"
    draw_text_with_shadow(draw_orig, (240, 204), orig_text, FONT_GAME, fill=(255, 255, 255), shadow=(20, 30, 60))

    # Right: Patched Dialogue
    img_patch = img_base.copy()
    draw_patch = ImageDraw.Draw(img_patch)
    draw_patch.rectangle([0, 186, 480, 222], fill=(10, 15, 25, 160))
    patch_text = "아니요, 박물관에 웬 괴한이 나타나..."
    draw_text_with_shadow(draw_patch, (240, 204), patch_text, FONT_GAME, fill=(255, 255, 255), shadow=(20, 30, 60))

    # Canvas
    canvas_w = w * 2 + 40
    canvas_h = h + 130
    canvas = Image.new("RGBA", (canvas_w, canvas_h), (24, 28, 36, 255))
    draw = ImageDraw.Draw(canvas)

    # Title Header
    title = "시크릿 에이전트 클랭크 - 프롤로그 컷씬 클랭크 대사 교정 비교"
    draw.text((canvas_w // 2, 22), title, font=FONT_TITLE, fill=(255, 215, 0), anchor="mm")

    # Left Column
    x_left = 15
    y_top = 55
    canvas.paste(img_orig, (x_left, y_top))
    draw.rectangle([x_left, y_top - 24, x_left + 180, y_top - 4], fill=(180, 40, 40))
    draw.text((x_left + 90, y_top - 14), "수정 전 (공식 정발판)", font=FONT_BOLD, fill=(255, 255, 255), anchor="mm")

    # Right Column
    x_right = x_left + w + 10
    canvas.paste(img_patch, (x_right, y_top))
    draw.rectangle([x_right, y_top - 24, x_right + 180, y_top - 4], fill=(30, 140, 60))
    draw.text((x_right + 90, y_top - 14), "수정 후 (v1.0 한글 패치)", font=FONT_BOLD, fill=(255, 255, 255), anchor="mm")

    # Explanations
    exp_orig = "• 공식 정발판의 문법 파괴 기계 번역투 방치 (\"아니요. 그런 건 이상한 걸 보았어요!\")"
    exp_patch = "• 클랭크의 신사적 경어체 및 자연스러운 상황 보고 복원 (\"아니요, 박물관에 웬 괴한이 나타나...\")"
    draw.text((x_left + 10, y_top + h + 15), exp_orig, font=FONT_SUB, fill=(240, 160, 160))
    draw.text((x_left + 10, y_top + h + 38), exp_patch, font=FONT_SUB, fill=(160, 240, 160))

    out_file = IMG_DIR / "comparison_01_clank_dialogue.png"
    canvas.save(out_file)
    print(f"[+] Saved: {out_file}")

def create_highlight_collision_comparison():
    bg_path = QA_DIR / "cutscene_museum_inside.png"
    img_base = Image.open(bg_path).convert("RGBA")
    w, h = img_base.size  # 480, 272

    def draw_hud_box(img, is_orig):
        draw = ImageDraw.Draw(img)
        # Message box background
        bx0, by0, bx1, by1 = 20, 35, 460, 237
        draw.rectangle([bx0, by0, bx1, by1], fill=(14, 20, 32, 230), outline=(50, 100, 160), width=2)
        # Header bar
        draw.rectangle([bx0, by0, bx1, by0 + 34], fill=(24, 40, 65, 240))
        draw.text((bx0 + 15, by0 + 17), "장비 상세 정보  [ 전자 로켓 ]", font=FONT_BOLD, fill=(255, 215, 0), anchor="lm")

        # Description text
        line1 = "전자 로켓은 훨씬 큰 내부 "
        
        y_text = by0 + 60
        x_text = bx0 + 20
        draw.text((x_text, y_text), line1, font=FONT_GAME_SM, fill=(230, 235, 245))
        
        # Word width for line 1
        bbox1 = draw.textbbox((x_text, y_text), line1, font=FONT_GAME_SM)
        x_kw = bbox1[2]

        if is_orig:
            # Buggy: 축 (white) + 전기 (yellow) + 를 (white)
            draw.text((x_kw, y_text), "축", font=FONT_GAME_SM, fill=(230, 235, 245))
            bbox_chuk = draw.textbbox((x_kw, y_text), "축", font=FONT_GAME_SM)
            
            x_jeongi = bbox_chuk[2]
            draw.text((x_jeongi, y_text), "전기", font=FONT_GAME_SM, fill=(255, 225, 40))
            bbox_jeongi = draw.textbbox((x_jeongi, y_text), "전기", font=FONT_GAME_SM)
            
            x_reul = bbox_jeongi[2]
            draw.text((x_reul, y_text), "를 사용해", font=FONT_GAME_SM, fill=(230, 235, 245))

            # Red indicator for the bug
            draw.rectangle([x_jeongi - 2, y_text - 1, bbox_jeongi[2] + 2, y_text + 22], outline=(255, 80, 80), width=2)
            draw.text((bx0 + 20, y_text + 32), "▲ '축전기' 중 '전기'만 노란색 분할 태그 오적용 (빌드 버그)", font=FONT_SUB, fill=(255, 120, 120))
        else:
            # Fixed: 축전기 (clean uniform)
            draw.text((x_kw, y_text), "축전기", font=FONT_GAME_SM, fill=(230, 235, 245))
            bbox_full = draw.textbbox((x_kw, y_text), "축전기", font=FONT_GAME_SM)
            
            draw.text((bbox_full[2], y_text), "를 사용해", font=FONT_GAME_SM, fill=(230, 235, 245))

            # Green indicator
            draw.rectangle([x_kw - 2, y_text - 1, bbox_full[2] + 2, y_text + 22], outline=(80, 220, 120), width=2)
            draw.text((bx0 + 20, y_text + 32), "▲ 복합명사 내부 분할 제거 및 온전한 단어 정상 렌더링", font=FONT_SUB, fill=(120, 240, 160))

        # Additional lines
        line2 = "다수의 대상들 사이에 전호가 형성되게끔 만들어"
        line3 = "모두에게 복합식 전기 피해를 줍니다."
        draw.text((bx0 + 20, y_text + 64), line2, font=FONT_GAME_SM, fill=(190, 200, 215))
        draw.text((bx0 + 20, y_text + 92), line3, font=FONT_GAME_SM, fill=(190, 200, 215))

    img_orig = img_base.copy()
    draw_hud_box(img_orig, is_orig=True)

    img_patch = img_base.copy()
    draw_hud_box(img_patch, is_orig=False)

    # Canvas
    canvas_w = w * 2 + 40
    canvas_h = h + 130
    canvas = Image.new("RGBA", (canvas_w, canvas_h), (24, 28, 36, 255))
    draw = ImageDraw.Draw(canvas)

    # Title Header
    title = "시크릿 에이전트 클랭크 - 키워드 하이라이터 단어 쪼개짐 결함 교정 비교"
    draw.text((canvas_w // 2, 22), title, font=FONT_TITLE, fill=(255, 215, 0), anchor="mm")

    # Left Column
    x_left = 15
    y_top = 55
    canvas.paste(img_orig, (x_left, y_top))
    draw.rectangle([x_left, y_top - 24, x_left + 180, y_top - 4], fill=(180, 40, 40))
    draw.text((x_left + 90, y_top - 14), "수정 전 (공식 정발판)", font=FONT_BOLD, fill=(255, 255, 255), anchor="mm")

    # Right Column
    x_right = x_left + w + 10
    canvas.paste(img_patch, (x_right, y_top))
    draw.rectangle([x_right, y_top - 24, x_right + 180, y_top - 4], fill=(30, 140, 60))
    draw.text((x_right + 90, y_top - 14), "수정 후 (v1.0 한글 패치)", font=FONT_BOLD, fill=(255, 255, 255), anchor="mm")

    # Explanations
    exp_orig = "• 자동 키워드 치환 버그로 복합명사 내부가 쪼개져 단어 중간만 노란색 강조 (35건 방치)"
    exp_patch = "• 중복 태그 및 단어 분할 결함 전수 교정, 정상적인 완성형 한국어 렌더링 복원"
    draw.text((x_left + 10, y_top + h + 15), exp_orig, font=FONT_SUB, fill=(240, 160, 160))
    draw.text((x_left + 10, y_top + h + 38), exp_patch, font=FONT_SUB, fill=(160, 240, 160))

    out_file = IMG_DIR / "comparison_02_highlight_collision.png"
    canvas.save(out_file)
    print(f"[+] Saved: {out_file}")

if __name__ == "__main__":
    create_clank_dialogue_comparison()
    create_highlight_collision_comparison()
