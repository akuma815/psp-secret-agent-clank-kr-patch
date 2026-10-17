"""Generate 100% genuine side-by-side comparison images for Secret Agent Clank."""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import shutil

BASE = Path("g:/Downloads/Korean Traslate Project/Games/Clank  Ratchet - Maruhi Mission Ignition")
IMG_DIR = BASE / "img"
QA_DIR = BASE / "qa"

# Copy verified real captures to img dir
shutil.copy2(QA_DIR / "real_original_sac_clank_dialogue.png", IMG_DIR / "original_sac_clank.png")
shutil.copy2(QA_DIR / "real_patched_sac_clank_dialogue.png", IMG_DIR / "patched_sac_clank.png")
shutil.copy2(QA_DIR / "real_original_sac_news_ratchet.png", IMG_DIR / "original_sac_news.png")
shutil.copy2(QA_DIR / "real_patched_sac_news_ratchet.png", IMG_DIR / "patched_sac_news.png")

FONT_BOLD = ImageFont.truetype("C:/Windows/Fonts/malgunbd.ttf", 16)
FONT_TITLE = ImageFont.truetype("C:/Windows/Fonts/malgunbd.ttf", 20)
FONT_SUB = ImageFont.truetype("C:/Windows/Fonts/malgun.ttf", 14)

def create_clank_dialogue_comparison():
    orig_path = IMG_DIR / "original_sac_clank.png"
    patch_path = IMG_DIR / "patched_sac_clank.png"
    img_orig = Image.open(orig_path).convert("RGBA")
    img_patch = Image.open(patch_path).convert("RGBA")
    w, h = img_orig.size  # 480, 272

    # Canvas
    canvas_w = w * 2 + 40
    canvas_h = h + 130
    canvas = Image.new("RGBA", (canvas_w, canvas_h), (24, 28, 36, 255))
    draw = ImageDraw.Draw(canvas)

    # Title Header
    title = "시크릿 에이전트 클랭크 - 프롤로그 컷씬 클랭크 대사 교정 비교 (실제 게임 캡처)"
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
    exp_orig = "• 공식 정발판: 사령부 질문(\"눈은 확보했나?\")의 맥락을 벗어난 어색한 직역투 (\"아니요. 그런데 아주 이상한 장면을...\")"
    exp_patch = "• 한글 패치본: 클랭크의 신사적 경어체 및 완벽한 임무 상황 보고 복원 (\"아니요, 지키기는커녕 생각지도 못한 방해자가...\")"
    draw.text((x_left + 10, y_top + h + 15), exp_orig, font=FONT_SUB, fill=(240, 160, 160))
    draw.text((x_left + 10, y_top + h + 38), exp_patch, font=FONT_SUB, fill=(160, 240, 160))

    out_file = IMG_DIR / "comparison_01_clank_dialogue.png"
    canvas.save(out_file)
    print(f"[+] Saved: {out_file}")

def create_news_ratchet_comparison():
    orig_path = IMG_DIR / "original_sac_news.png"
    patch_path = IMG_DIR / "patched_sac_news.png"
    img_orig = Image.open(orig_path).convert("RGBA")
    img_patch = Image.open(patch_path).convert("RGBA")
    w, h = img_orig.size  # 480, 272

    # Canvas
    canvas_w = w * 2 + 40
    canvas_h = h + 130
    canvas = Image.new("RGBA", (canvas_w, canvas_h), (24, 28, 36, 255))
    draw = ImageDraw.Draw(canvas)

    # Title Header
    title = "시크릿 에이전트 클랭크 - 속보 뉴스 라쳇 체포 보도 교정 비교 (실제 게임 캡처)"
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
    exp_orig = "• 공식 정발판: 긴급 뉴스 특종 보도임에도 단순 현장 목격으로 밋밋하게 서술 (\"...현장에는 영웅인 라쳇이 있었습니다.\")"
    exp_patch = "• 한글 패치본: 긴급 속보 앵커 톤 및 현행범 체포 보도 맥락 완벽 복원 (\"...유명 영웅 라쳇이 현행범으로 체포되었습니다.\")"
    draw.text((x_left + 10, y_top + h + 15), exp_orig, font=FONT_SUB, fill=(240, 160, 160))
    draw.text((x_left + 10, y_top + h + 38), exp_patch, font=FONT_SUB, fill=(160, 240, 160))

    out_file = IMG_DIR / "comparison_02_highlight_collision.png"
    # Also save as comparison_02_news_ratchet.png for clear naming
    canvas.save(out_file)
    canvas.save(IMG_DIR / "comparison_02_news_ratchet.png")
    print(f"[+] Saved: {out_file}")

if __name__ == "__main__":
    create_clank_dialogue_comparison()
    create_news_ratchet_comparison()
