import os
import subprocess
import yt_dlp

# YouTube rotates its defenses; try multiple player clients until one works
PLAYER_CLIENTS = [None, ["android_vr"], ["ios"], ["mweb"], ["web_embedded"], ["tv"]]

def download_youtube_video(url, output_dir="downloads"):
    os.makedirs(output_dir, exist_ok=True)
    last_error = None

    for client in PLAYER_CLIENTS:
        ydl_opts = {
            "format": "bv*[height<=720]+ba/b[height<=720]/b",
            "merge_output_format": "mp4",
            "outtmpl": os.path.join(output_dir, "%(id)s.%(ext)s"),
            "quiet": True,
            "no_warnings": True,
            "noplaylist": True,
            "socket_timeout": 30,
            "retries": 3,
        }
        if client:
            ydl_opts["extractor_args"] = {"youtube": {"player_client": client}}

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = os.path.join(output_dir, f"{info['id']}.mp4")
                return filename, info.get("title", "Unknown Title")
        except Exception as e:
            last_error = e
            continue

    raise Exception(f"YouTube blocked the download from this IP. Last error: {last_error}")

def crop_to_vertical(input_path, output_path):
    cmd = [
        "ffmpeg", "-y", "-i", input_path,
        "-vf", "crop=ih*9/16:ih,scale=1080:1920:flags=lanczos",
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-c:a", "aac", "-b:a", "128k",
        output_path,
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return output_path
