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
    for i in range(6):
        x = W//2 - 90 + i*36
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
subtitle(d, "Six ways to build lasting\nQur’an learning skills.", 1145, size=42)
d.text((W//2, 1650), "Tajweed  •  Arabic  •  Qur’anic vocabulary", font=font(27, True), fill="#9fc0b2", anchor="ma")
save(im, 0)

# 2 — Tajweed Quest
im = gradient("#f9f2df", "#e8f3e9")
d = ImageDraw.Draw(im)
label(d, "1 of 6", 120, fill="#83d2ad")
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
label(d, "2 of 6", 120, fill="#d9b7ed")
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
label(d, "3 of 6", 120, fill="#f1c76c")
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
label(d, "4 of 6", 105, fill="#8bc9ee")
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
label(d, "5 of 6", 100, fill="#8edbb8")
title(d, "Wasl", 220, size=96)
subtitle(d, "Find Qur’anic words across\nbeautiful scenic worlds.", 350, fill=WHITE)
footer(d, 4); save(im, 5)

# Animated Wasl gameplay — the joining gesture is drawn progressively.
wasl_base = im.copy()
wheel_center = (W // 2, 1260)
nodes = [(315, 1285), (535, 1035), (770, 1285), (535, 1515)]
letters = ["ن", "و", "ر", "ب"]
route = nodes[:3]
motion_frames = OUT / "wasl-motion"
motion_frames.mkdir(exist_ok=True)
for frame in range(81):
    canvas = wasl_base.copy()
    fd = ImageDraw.Draw(canvas, "RGBA")
    fd.ellipse((245, 970, 835, 1560), fill=(255,253,248,235), outline=(255,255,255,210), width=10)
    progress = max(0, min(1, (frame - 8) / 48))
    segments = len(route) - 1
    scaled = progress * segments
    for seg in range(segments):
        amount = max(0, min(1, scaled - seg))
        if amount <= 0: continue
        a, b = route[seg], route[seg + 1]
        end = (a[0] + (b[0]-a[0])*amount, a[1] + (b[1]-a[1])*amount)
        fd.line((a, end), fill=(15,110,86,230), width=24)
    for i, ((x, y), letter) in enumerate(zip(nodes, letters)):
        active = progress * segments >= max(0, i-1) and i < 3
        fill = GREEN if active else "#ece5d5"
        fd.ellipse((x-68, y-68, x+68, y+68), fill=fill, outline="#ffffff", width=7)
        fd.text((x, y-7), letter, font=font(61, True), fill=WHITE if active else "#5f6c65", anchor="mm")
    fd.rounded_rectangle((260, 1640, 820, 1715), 35, fill=(7,46,38,225))
    fd.text((W//2, 1661), "JOIN THE LETTERS", font=font(29, True), fill=WHITE, anchor="ma")
    canvas.convert("RGB").save(motion_frames / f"frame-{frame:03d}.jpg", quality=91)

wasl_motion = OUT / "wasl-motion.mp4"
subprocess.run([
    "ffmpeg", "-y", "-framerate", "30", "-i", str(motion_frames / "frame-%03d.jpg"),
    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "30", str(wasl_motion)
], check=True)

# 7 — Quranic Cryptogram
im = gradient("#e2e8f0", "#f8fafc")
d = ImageDraw.Draw(im)
label(d, "6 of 6", 105, fill="#cbd5e1")
title(d, "Quranic Cryptogram", 215, fill=INK, size=72)
subtitle(d, "Discover which Arabic letter\neach symbol is hiding.", 345, fill=MUTED)
symbols = [("◇", "ن"), ("△", "و"), ("○", "ر")]
for i, (symbol, letter) in enumerate(symbols):
    y = 650 + i*260
    d.rounded_rectangle((150, y, 430, y+190), 40, fill=WHITE, outline="#cbd5e1", width=5)
    d.text((290, y+70), symbol, font=font(86, True), fill="#475569", anchor="mm")
    d.text((540, y+70), "→", font=font(62, True), fill=GOLD, anchor="mm")
    d.rounded_rectangle((650, y, 930, y+190), 40, fill="#475569")
    d.text((790, y+70), letter, font=font(82, True), fill=WHITE, anchor="mm")
d.text((W//2, 1535), "DECODE THE VERSE", font=font(35, True), fill="#475569", anchor="ma")
footer(d, 5); save(im, 6)

# 8 — close
im = gradient("#0f6e56", "#082b24")
d = ImageDraw.Draw(im)
bird = contain(ROOT / "quran-games" / "hudhud.png", (470, 470))
im.alpha_composite(bird, ((W-bird.width)//2, 155))
label(d, "Available now", 680)
title(d, "Six games.\nOne learning journey.", 800, size=82)
subtitle(d, "Study Tajweed. Build vocabulary.\nStay sharp with the Holy Qur’an.", 1060, fill="#d8ebe2", size=38)
d.rounded_rectangle((190, 1375, 890, 1500), 62, fill=WHITE)
d.text((W//2, 1410), "PLAY FREE IN QARIAI", font=font(34, True), fill=GREEN, anchor="ma")
d.text((W//2, 1635), "qariai.app", font=font(34, True), fill="#9fcbb8", anchor="ma")
save(im, 7)

inputs = []
for n in range(8):
    if n == 5:
        inputs += ["-i", str(wasl_motion)]
    else:
        inputs += ["-loop", "1", "-t", "2.7", "-i", str(OUT / f"slide-{n}.jpg")]

filters = []
for n in range(8):
    if n == 5:
        filters.append(f"[{n}:v]scale=1080:1920,fps=30,format=yuv420p,setpts=PTS-STARTPTS[v{n}]")
    else:
        filters.append(f"[{n}:v]scale=1080:1920,zoompan=z='min(zoom+0.0007,1.05)':d=81:s=1080x1920:fps=30,format=yuv420p,setpts=PTS-STARTPTS[v{n}]")

last = "v0"
for n in range(1, 8):
    out = f"x{n}"
    offset = 2.35 * n
    transition = "slideleft" if n % 2 else "fadefast"
    filters.append(f"[{last}][v{n}]xfade=transition={transition}:duration=0.35:offset={offset:.2f}[{out}]")
    last = out

video = ROOT / "marketing" / "qariai-games-vertical-24s.mp4"
cmd = ["ffmpeg", "-y", *inputs, "-filter_complex", ";".join(filters), "-map", f"[{last}]", "-t", "19.15", "-r", "30", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(video)]
subprocess.run(cmd, check=True)
print(video)
