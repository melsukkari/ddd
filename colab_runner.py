import subprocess
import sys
import os

def setup_and_run():
    print("🔧 Installing Python dependencies from requirements.txt...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "-r", "requirements.txt"])
    
    print("🔧 Installing system-level FFmpeg...")
    subprocess.check_call(["apt-get", "update", "-qq"])
    subprocess.check_call(["apt-get", "install", "-y", "-qq", "ffmpeg"])
    
    print("🚀 Launching Ssemble-style Gradio UI...")
    print("Please wait for the public URL to generate below...")
    subprocess.run([sys.executable, "app.py"])

if __name__ == "__main__":
    setup_and_run()
