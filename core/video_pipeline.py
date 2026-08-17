import os
import subprocess
import yt_dlp

def download_youtube_video(url, output_dir="downloads"):
    os.makedirs(output_dir, exist_ok=True)
    ydl_opts = {
        'format': 'mp4[height<=720]/best',
        'outtmpl': f'{output_dir}/%(id)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        video_id = info['id']
        filename = f"{output_dir}/{video_id}.mp4"
    return filename, info.get('title', 'Unknown Title')

def crop_to_vertical(input_path, output_path):
    cmd = [
        'ffmpeg', '-y', '-i', input_path, 
        '-vf', "crop=ih*9/16:ih,scale=1080:1920:flags=lanczos", 
        '-c:v', 'libx264', '-preset', 'fast', '-crf', '23',
        '-c:a', 'aac', '-b:a', '128k',
        output_path
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return output_path
