"""Builds the 'games' showcase video from REAL in-app screenshots (marketing/games-shots/*.jpg).
Run: python3 marketing/generate_games_video.py   (needs Pillow + ffmpeg; Inter font)"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import subprocess

ROOT = Path(__file__).resolve().parents[1]
SHOTS = ROOT / "marketing" / "games-shots"
OUT = ROOT / "marketing" / "games-video-frames"
OUT.mkdir(parents=True, exist_ok=True)
W, H = 1080, 1920
DARK, DARK2 = "#0a342b", "#061b17"
GOLD, WHITE, MUTED = "#e6b662", "#fffdf8", "#c4dbd1"
INTER = "/usr/share/fonts/opentype/inter/Inter-%s.otf"

def font(size, w="Bold"):
    return ImageFont.truetype(INTER % w, size)

def gradient():
    a, b = Image.new("RGB", (W, H), DARK), Image.new("RGB", (W, H), DARK2)
    return Image.composite(b, a, Image.linear_gradient("L").resize((W, H))).convert("RGBA")

def chip(d, text, y, fill):
    f = font(30, "Bold"); box = d.textbbox((0, 0), text.upper(), font=f); tw = box[2] - box[0]
    d.rounded_rectangle((W//2 - tw//2 - 30, y - 16, W//2 + tw//2 + 30, y + 54), 36, fill=fill)
    d.text((W//2, y), text.upper(), font=f, fill=DARK, anchor="ma")

def dots(d, i, n=6):
    d.rounded_rectangle((W//2 - 140, 1858, W//2 + 140, 1900), 21, fill="#061b17")
    for k in range(n):
        x = W//2 - (n-1)*18 + k*36
        d.ellipse((x-7, 1872, x+7, 1886), fill=GOLD if k == i else "#4f7a6b")

def phone(im, shot, top=430, width=900):
    sc = Image.open(SHOTS / shot).convert("RGBA")
    sw = width - 36; sh = round(sw * sc.height / sc.width)
    sc = sc.resize((sw, sh), Image.Resampling.LANCZOS)
    m = Image.new("L", sc.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, sw, sh), 70, fill=255); sc.putalpha(m)
    fw, fh = width, sh + 36
    x, y = (W - fw)//2, top
    sh_ = Image.new("RGBA", (fw + 160, fh + 160), (0, 0, 0, 0))
    ImageDraw.Draw(sh_).rounded_rectangle((80, 100, fw + 80, fh + 100), 76, fill=(0, 0, 0, 130))
    im.alpha_composite(sh_.filter(ImageFilter.GaussianBlur(28)), (x - 80, y - 80))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((x, y, x + fw, y + fh), 88, fill="#0b0f0e", outline="#2c4a40", width=3)
    im.alpha_composite(sc, (x + 18, y + 18))

def save(im, n):
    im.convert("RGB").save(OUT / f"slide-{n}.jpg", quality=94, subsampling=0)

def scene(n, idx, label, title, sub, shot, accent):
    im = gradient(); d = ImageDraw.Draw(im)
    d.ellipse((-260, -220, 520, 560), fill="#123f35")
    chip(d, label, 100, accent)
    d.text((W//2, 185), title, font=font(84), fill=WHITE, anchor="ma")
    d.multiline_text((W//2, 300), sub, font=font(35, "Medium"), fill=MUTED, anchor="ma", align="center", spacing=12)
    phone(im, shot, top=430); dots(d, idx); save(im, n)

# 0 — opening
im = gradient(); d = ImageDraw.Draw(im)
d.ellipse((-220, -140, 560, 640), fill="#174f40"); d.ellipse((650, 1300, 1260, 1980), fill="#123f35")
logo = Image.open(ROOT / "uploads" / "logo.png").convert("RGBA"); logo.thumbnail((300, 300))
lm = Image.new("L", logo.size, 0); ImageDraw.Draw(lm).rounded_rectangle((0, 0, logo.width, logo.height), 64, fill=255); logo.putalpha(lm)
im.alpha_composite(logo, ((W - logo.width)//2, 300))
chip(d, "QariAI Games", 700, GOLD)
d.multiline_text((W//2, 820), "Learn. Play.\nGrow.", font=font(124), fill=WHITE, anchor="ma", align="center", spacing=6)
d.multiline_text((W//2, 1170), "Six ways to build lasting\nQur’an learning skills.", font=font(44, "Medium"), fill=MUTED, anchor="ma", align="center", spacing=14)
d.text((W//2, 1650), "Tajweed  •  Arabic  •  Qur’anic vocabulary", font=font(28), fill="#9fc0b2", anchor="ma")
save(im, 0)

scene(1, 0, "1 of 6", "Qur’an Quest", "Travel through worlds and earn stars\nas you learn Surahs and verses.", "quran-quest.jpg", "#8edbb8")
scene(2, 1, "2 of 6", "Tajweed Quest", "Meet HudHud and friends and learn\nthe rules in guided battles.", "tajweed-quest.jpg", "#f1c76c")
scene(3, 2, "3 of 6", "Harf Writer", "Trace each Arabic letter with\nclear, stroke-by-stroke guidance.", "harf-writer.jpg", "#d9b7ed")
scene(4, 3, "4 of 6", "Connect", "Solve clues from Qur’anic vocabulary\nand fill the letter grid.", "connect.jpg", "#8bc9ee")
scene(5, 4, "5 of 6", "Wasl", "Join letters to find Qur’anic words\nacross scenic worlds.", "wasl.jpg", "#8edbb8")
scene(6, 5, "6 of 6", "Quranic Cryptogram", "Decode a verse by discovering which\nletter each symbol hides.", "cryptogram.jpg", "#cbd5e1")

N = 7
inputs = []
for n in range(N):
    inputs += ["-loop", "1", "-framerate", "30", "-t", "2.7", "-i", str(OUT / f"slide-{n}.jpg")]
filters = [f"[{n}:v]scale=1080:1920,fps=30,format=yuv420p,setpts=PTS-STARTPTS[v{n}]" for n in range(N)]
last = "v0"
for n in range(1, N):
    filters.append(f"[{last}][v{n}]xfade=transition={'slideleft' if n % 2 else 'fadefast'}:duration=0.35:offset={2.35*n:.2f}[x{n}]")
    last = f"x{n}"
video = ROOT / "marketing" / "qariai-games-vertical-24s.mp4"
subprocess.run(["ffmpeg", "-y", *inputs, "-filter_complex", ";".join(filters), "-map", f"[{last}]", "-r", "30", "-t", "16.8",
                "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(video)], check=True)
Image.open(OUT / "slide-1.jpg").save(ROOT / "marketing" / "qariai-games-video-poster.jpg", quality=88, optimize=True)
print(video)
