import subprocess
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

HOOK_WORDS = ["secret", "never", "best", "worst", "warning", "stop", "how to", "why",
              "truth", "mistake", "free", "proven", "nobody", "everyone", "imagine"]

def get_video_meta(video_path):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0",
                        "-show_entries", "stream=width,height", "-of", "csv=p=0", video_path],
                       capture_output=True, text=True)
    try:
        w, h = [int(x) for x in r.stdout.strip().split(",")]
    except Exception:
        w, h = 0, 0
    d = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1", video_path],
                       capture_output=True, text=True)
    try:
        dur = float(d.stdout.strip())
    except Exception:
        dur = 0.0
    return w, h, dur

def review_short(video_path, text=""):
    analyzer = SentimentIntensityAnalyzer()
    w, h, dur = get_video_meta(video_path)
    checks, score = [], 40

    if h > w:
        checks.append("✅ Vertical 9:16 format — perfect for Shorts/Reels/TikTok"); score += 15
    else:
        checks.append("⚠️ Not vertical — crop to 9:16 for maximum reach")

    if 15 <= dur <= 60:
        checks.append(f"✅ Duration {dur:.0f}s — inside the viral sweet spot (15–60s)"); score += 15
    elif dur < 15:
        checks.append(f"⚠️ Duration {dur:.0f}s — slightly short; 15–60s performs best"); score += 5
    else:
        checks.append(f"⚠️ Duration {dur:.0f}s — too long; trim under 60s for retention"); score += 5

    if text:
        lower = text.lower()
        hooks = [hw for hw in HOOK_WORDS if hw in lower]
        if hooks:
            checks.append(f"✅ Strong hook words detected: {', '.join(hooks[:4])}"); score += 10
        else:
            checks.append("⚠️ No hook words found — open with a bold claim or question")

        vs = analyzer.polarity_scores(text)
        if abs(vs["compound"]) >= 0.3:
            checks.append(f"✅ High-emotion tone ({vs['compound']:.2f}) — drives shares & comments"); score += 10
        else:
            checks.append("⚠️ Neutral tone — add emotion or controversy to boost engagement"); score += 3

        wpm = (len(text.split()) / max(dur, 1)) * 60
        if 120 <= wpm <= 180:
            checks.append(f"✅ Pacing {wpm:.0f} WPM — ideal speaking rhythm"); score += 10
        else:
            checks.append(f"⚠️ Pacing {wpm:.0f} WPM — aim for 120–180 WPM")
    else:
        checks.append("ℹ️ Provide script text to unlock hook & sentiment analysis")

    score = min(100, score)
    verdict = "🔥 Viral potential!" if score >= 75 else ("👍 Solid short" if score >= 55 else "🛠 Needs work")
    return f"## 📊 Automated AI Review — Virality Score: {score}/100 ({verdict})\n\n" + "\n".join(f"- {c}" for c in checks)
