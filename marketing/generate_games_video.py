from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import subprocess

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "marketing" / "games-video-frames"
OUT.mkdir(parents=True, exist_ok=True)

W, H = 1080, 1920
GREEN = "#0f6e56"
DARK = "#092d26"
CREAM = "#f7f0df"
GOLD = "#d6a23e"
INK = "#102a22"
MUTED = "#627168"
WHITE = "#fffdf8"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

def font(size, bold=False):
    return ImageFont.truetype(BOLD if bold else FONT, size)

def cover(path, size):
    im = Image.open(path).convert("RGBA")
    ratio = max(size[0] / im.width, size[1] / im.height)
    im = im.resize((round(im.width * ratio), round(im.height * ratio)), Image.Resampling.LANCZOS)
    left = (im.width - size[0]) // 2
    top = (im.height - size[1]) // 2
    return im.crop((left, top, left + size[0], top + size[1]))

def contain(path, size):
    im = Image.open(path).convert("RGBA")
    im.thumbnail(size, Image.Resampling.LANCZOS)
    return im

def gradient(top, bottom):
    a = Image.new("RGB", (W, H), top)
    b = Image.new("RGB", (W, H), bottom)
    mask = Image.linear_gradient("L").resize((W, H))
    return Image.composite(b, a, mask).convert("RGBA")

def label(draw, text, y, fill=GOLD):
    f = font(31, True)
    box = draw.textbbox((0, 0), text.upper(), font=f)
    tw = box[2] - box[0]
    draw.rounded_rectangle((W//2-tw//2-28, y-14, W//2+tw//2+28, y+52), 30, fill=fill)
    draw.text((W//2, y), text.upper(), font=f, fill=DARK, anchor="ma")

def title(draw, text, y, fill=WHITE, size=92):
    draw.text((W//2, y), text, font=font(size, True), fill=fill, anchor="ma", align="center")

def subtitle(draw, text, y, fill="#d9e7e0", size=38):
    draw.multiline_text((W//2, y), text, font=font(size), fill=fill, anchor="ma", align="center", spacing=14)

def footer(draw, number):
    for i in range(5):
        x = W//2 - 72 + i*36
        color = GOLD if i == number else "#79978b"
        draw.ellipse((x-7, 1785, x+7, 1799), fill=color)

def save(im, n):
    im.convert("RGB").save(OUT / f"slide-{n}.jpg", quality=94, subsampling=0)

# 1 — opening
im = gradient("#0a342b", "#061b17")
d = ImageDraw.Draw(im)
d.ellipse((-220, -140, 560, 640), fill="#174f40")
d.ellipse((650, 1300, 1260, 1980), fill="#123f35")
bird = contain(ROOT / "quran-games" / "hudhud.png", (520, 520))
im.alpha_composite(bird, ((W-bird.width)//2, 170))
label(d, "QariAI Games", 735)
title(d, "Learn. Play.\nGrow.", 855, size=112)
subtitle(d, "Five ways to build lasting\nQur’an learning skills.", 1145, size=42)
d.text((W//2, 1650), "Tajweed  •  Arabic  •  Qur’anic vocabulary", font=font(27, True), fill="#9fc0b2", anchor="ma")
save(im, 0)

# 2 — Tajweed Quest
im = gradient("#f9f2df", "#e8f3e9")
d = ImageDraw.Draw(im)
label(d, "1 of 5", 120, fill="#83d2ad")
title(d, "Tajweed Quest", 235, fill=INK, size=82)
subtitle(d, "Learn the rules through guided\nchallenges with HudHud.", 365, fill=MUTED)
characters = contain(ROOT / "uploads" / "tajweed-quest-characters.webp", (900, 720))
im.alpha_composite(characters, ((W-characters.width)//2, 610))
d.rounded_rectangle((110, 1410, 970, 1595), 44, fill=WHITE, outline="#d7e5dc", width=4)
d.text((W//2, 1465), "RULE → PRACTISE → PROGRESS", font=font(34, True), fill=GREEN, anchor="ma")
d.text((W//2, 1530), "A clear path through every skill", font=font(27), fill=MUTED, anchor="ma")
footer(d, 0); save(im, 1)

# 3 — Harf Writer
im = gradient("#f4e8fb", "#f9f3e5")
d = ImageDraw.Draw(im)
label(d, "2 of 5", 120, fill="#d9b7ed")
title(d, "Harf Writer", 235, fill=INK, size=82)
subtitle(d, "Trace Arabic letters with clear,\nguided visual practice.", 365, fill=MUTED)
d.rounded_rectangle((145, 590, 935, 1400), 76, fill=WHITE, outline="#decbe8", width=5)
d.text((W//2, 620), "ع", font=font(470, True), fill="#8155a3", anchor="ma")
d.line((325, 1235, 755, 805), fill=GOLD, width=25)
d.polygon([(755,805),(702,827),(735,860)], fill=GOLD)
d.text((W//2, 1485), "TRACE • REPEAT • REMEMBER", font=font(31, True), fill="#8155a3", anchor="ma")
footer(d, 1); save(im, 2)

# 4 — Word Builder
im = gradient("#fff2d8", "#f3eadb")
d = ImageDraw.Draw(im)
label(d, "3 of 5", 120, fill="#f1c76c")
title(d, "Word Builder", 235, fill=INK, size=82)
subtitle(d, "Assemble letters and marks into\ncomplete Qur’anic words.", 365, fill=MUTED)
tiles = [("ش", "#65b893"), ("دّ", "#8f70bd"), ("ة", "#ef9a58"), ("َ", "#59a5ca")]
for i, (letter, color) in enumerate(tiles):
    x = 130 + i*220
    y = 770 + (45 if i % 2 else 0)
    d.rounded_rectangle((x, y, x+180, y+180), 34, fill=color)
    d.text((x+90, y+72), letter, font=font(76, True), fill=WHITE, anchor="mm")
d.line((210, 1115, 870, 1115), fill="#d4b267", width=6)
d.text((W//2, 1240), "Letters become words.", font=font(47, True), fill=INK, anchor="ma")
d.text((W//2, 1320), "Words become understanding.", font=font(36), fill=MUTED, anchor="ma")
footer(d, 2); save(im, 3)

# 5 — Connect
im = gradient("#dcecff", "#e8e3fa")
d = ImageDraw.Draw(im)
label(d, "4 of 5", 105, fill="#8bc9ee")
title(d, "Connect", 215, fill=INK, size=88)
subtitle(d, "Complete colourful chains of\nQur’anic vocabulary.", 345, fill=MUTED)
shot = contain(ROOT / "uploads" / "quran-combo-game.jpg", (700, 1320))
mask = Image.new("L", shot.size, 0)
ImageDraw.Draw(mask).rounded_rectangle((0, 0, shot.width, shot.height), 56, fill=255)
shot.putalpha(mask)
shadow = Image.new("RGBA", (shot.width+60, shot.height+60), (0,0,0,0))
ImageDraw.Draw(shadow).rounded_rectangle((30,30,shot.width+30,shot.height+30), 60, fill=(31,57,87,70))
shadow = shadow.filter(ImageFilter.GaussianBlur(20))
im.alpha_composite(shadow, ((W-shadow.width)//2, 520))
im.alpha_composite(shot, ((W-shot.width)//2, 490))
footer(d, 3); save(im, 4)

# 6 — Wasl
im = cover(ROOT / "quran-games" / "wasl-sunrise-oasis.png", (W, H))
shade = Image.new("RGBA", (W, H), (0,0,0,0))
sd = ImageDraw.Draw(shade)
sd.rectangle((0,0,W,520), fill=(4,32,27,180))
sd.rectangle((0,1390,W,H), fill=(4,32,27,190))
im = Image.alpha_composite(im, shade)
d = ImageDraw.Draw(im)
label(d, "5 of 5", 100, fill="#8edbb8")
title(d, "Wasl", 220, size=96)
subtitle(d, "Find Qur’anic words across\nbeautiful scenic worlds.", 350, fill=WHITE)
d.rounded_rectangle((155, 1430, 925, 1640), 44, fill=(7,46,38,225), outline="#83d2ad", width=4)
d.text((W//2, 1485), "CONNECT LETTERS", font=font(34, True), fill=GOLD, anchor="ma")
d.text((W//2, 1550), "Unlock worlds • Rise in difficulty", font=font(28), fill=WHITE, anchor="ma")
footer(d, 4); save(im, 5)

# 7 — close
im = gradient("#0f6e56", "#082b24")
d = ImageDraw.Draw(im)
bird = contain(ROOT / "quran-games" / "hudhud.png", (470, 470))
im.alpha_composite(bird, ((W-bird.width)//2, 155))
label(d, "Available now", 680)
title(d, "Five games.\nOne learning journey.", 800, size=82)
subtitle(d, "Study Tajweed. Build vocabulary.\nStay sharp with the Holy Qur’an.", 1060, fill="#d8ebe2", size=38)
d.rounded_rectangle((190, 1375, 890, 1500), 62, fill=WHITE)
d.text((W//2, 1410), "PLAY FREE IN QARIAI", font=font(34, True), fill=GREEN, anchor="ma")
d.text((W//2, 1635), "qariai.app", font=font(34, True), fill="#9fcbb8", anchor="ma")
save(im, 6)

inputs = []
for n in range(7):
    inputs += ["-loop", "1", "-t", "3.5", "-i", str(OUT / f"slide-{n}.jpg")]

filters = []
for n in range(7):
    filters.append(f"[{n}:v]scale=1080:1920,zoompan=z='min(zoom+0.00045,1.045)':d=105:s=1080x1920:fps=30,format=yuv420p,setpts=PTS-STARTPTS[v{n}]")

last = "v0"
for n in range(1, 7):
    out = f"x{n}"
    offset = 2.95 * n
    filters.append(f"[{last}][v{n}]xfade=transition=fade:duration=0.55:offset={offset:.2f}[{out}]")
    last = out

video = ROOT / "marketing" / "qariai-games-vertical-24s.mp4"
cmd = ["ffmpeg", "-y", *inputs, "-filter_complex", ";".join(filters), "-map", f"[{last}]", "-t", "21.2", "-r", "30", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(video)]
subprocess.run(cmd, check=True)
print(video)
