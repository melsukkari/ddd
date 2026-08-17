import os
import subprocess
import yt_dlp

# YouTube rotates its defenses; try multiple player clients until one works
PLAYER_CLIENTS = [None, ["android_vr"], ["ios"], ["mweb"], ["web_embedded"], ["tv"]]

def download_youtube_video(url, output_dir="downloads"):
    print(f"📥 Starting download for URL: {url}")
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
            print(f"🔄 Trying player client: {client if client else 'default'}")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = os.path.join(output_dir, f"{info['id']}.mp4")
                print(f"✅ Download successful: {filename}")
                return filename, info.get("title", "Unknown Title")
        except Exception as e:
            last_error = e
            print(f"⚠️ Player client {client} failed: {str(e)}")
            continue

    raise Exception(f"YouTube blocked the download from this IP. Last error: {last_error}")

def crop_to_vertical(input_path, output_path):
    print(f"✂️ Starting crop operation:")
    print(f"   Input: {input_path}")
    print(f"   Output: {output_path}")
    
    cmd = [
        "ffmpeg", "-y", "-i", input_path,
        "-vf", "crop=ih*9/16:ih,scale=1080:1920:flags=lanczos",
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "23",
        "-c:a", "aac", "-b:a", "128k",
        output_path,
    ]
    
    print(f"🎬 Running FFmpeg command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ FFmpeg crop failed with error:\n{result.stderr}")
            print("🔄 Fallback: Copying original file instead of cropping...")
            import shutil
            shutil.copy2(input_path, output_path)
            print(f"✅ Fallback copy successful: {output_path}")
            return output_path
        else:
            print(f"✅ Crop successful: {output_path}")
            print(result.stdout)
            return output_path
    except Exception as e:
        print(f"❌ Critical error during crop: {str(e)}")
        print("🔄 Fallback: Copying original file instead of cropping...")
        import shutil
        shutil.copy2(input_path, output_path)
        print(f"✅ Fallback copy successful: {output_path}")
        return output_path
