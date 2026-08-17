import os
import re
import subprocess
import asyncio
import edge_tts
from PIL import Image, ImageDraw, ImageFont

VOICE = "en-US-AriaNeural"
W, H = 1080, 1920
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

def split_script(text):
    sentences = re.split(r'(?<=[.!?])\s+|\n+', text.strip())
    return [s.strip() for s in sentences if len(s.strip()) > 3][:8]

def _tts(text, out_path):
    asyncio.run(edge_tts.Communicate(text, VOICE).save(out_path))

def _duration(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1", path],
                       capture_output=True, text=True)
    return float(r.stdout.strip() or 0)

def _make_slide(text, out_path):
    img = Image.new("RGB", (W, H), (18, 18, 30))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 14], fill=(99, 102, 241))
    d.rectangle([0, H - 14, W, H], fill=(99, 102, 241))
    try:
        font = ImageFont.truetype(FONT_PATH, 72)
    except Exception:
        font = ImageFont.load_default()
    words, lines, cur = text.split(), [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if d.textlength(test, font=font) < W - 160:
            cur = test
        else:
            lines.append(cur); cur = w
    if cur: lines.append(cur)
    y = (H - len(lines[:8]) * 100) // 2
    for line in lines[:8]:
        d.text(((W - d.textlength(line, font=font)) / 2, y), line, font=font, fill=(255, 255, 255))
        y += 100
    img.save(out_path)

def synthesize_video_from_script(script, workdir="synth"):
    os.makedirs(workdir, exist_ok=True)
    scenes = split_script(script)
    if not scenes:
        raise Exception("Could not parse any sentences from the script.")
    segs = []
    for i, scene in enumerate(scenes):
        mp3 = os.path.join(workdir, f"scene_{i}.mp3")
        png = os.path.join(workdir, f"scene_{i}.png")
        seg = os.path.join(workdir, f"seg_{i}.mp4")
        _tts(scene, mp3)
        _make_slide(scene, png)
        subprocess.run(["ffmpeg", "-y", "-loop", "1", "-i", png, "-i", mp3,
                        "-c:v", "libx264", "-pix_fmt", "yuv420p",
                        "-c:a", "aac", "-b:a", "128k", "-shortest", seg],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        segs.append(seg)
    concat = os.path.join(workdir, "concat.txt")
    with open(concat, "w") as f:
        for s in segs:
            f.write(f"file '{s}'\n")
    out = os.path.join(workdir, "final_short.mp4")
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat, "-c", "copy", out],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return out
