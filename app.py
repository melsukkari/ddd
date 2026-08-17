import gradio as gr
import os
import shutil
from core.video_pipeline import download_youtube_video, crop_to_vertical

def _finish(raw_path, title, progress):
    progress(0.6, desc="✂️ AI Cropping to Vertical (9:16)...")
    base, ext = os.path.splitext(raw_path)
    output_path = f"{base}_vertical.mp4"
    crop_to_vertical(raw_path, output_path)
    progress(1.0, desc="✅ Done!")
    return raw_path, output_path, f"🎉 Successfully processed: {title}"

def process_from_url(url, progress=gr.Progress()):
    if not url:
        return None, None, "⚠️ Please enter a valid YouTube URL."
    progress(0.2, desc="📥 Downloading Video...")
    try:
        raw_path, title = download_youtube_video(url)
    except Exception as e:
        return None, None, f"❌ Error downloading: {str(e)}"
    return _finish(raw_path, title, progress)

def process_from_file(file, progress=gr.Progress()):
    if file is None:
        return None, None, "⚠️ Please upload a video file."
    progress(0.2, desc="📥 Loading uploaded video...")
    os.makedirs("downloads", exist_ok=True)
    raw_path = os.path.join("downloads", os.path.basename(file.name))
    shutil.copy(file.name, raw_path)
    return _finish(raw_path, "Uploaded Video", progress)

with gr.Blocks(theme=gr.themes.Soft(), title="Shorts AI SaaS", css="footer {visibility: hidden}") as demo:
    gr.Markdown("# 🎬 YouTube-to-Shorts AI Engine")
    gr.Markdown("Paste a YouTube URL **or upload a video** to auto-crop to vertical 9:16.")

    with gr.Row():
        with gr.Column(scale=1):
            with gr.Tabs():
                with gr.TabItem("🔗 From YouTube"):
                    url_input = gr.Textbox(label="YouTube URL", placeholder="https://youtube.com/watch?v=...")
                    url_btn = gr.Button("✨ Generate Short", variant="primary")
                with gr.TabItem("📁 Upload File"):
                    file_input = gr.File(label="Upload MP4 video")
                    file_btn = gr.Button("✨ Generate Short from File", variant="primary")
            status_text = gr.Textbox(label="Status", interactive=False)

        with gr.Column(scale=2):
            with gr.Tabs():
                with gr.TabItem("Original Video"):
                    original_video = gr.Video(label="Source (16:9)")
                with gr.TabItem("AI Generated Short"):
                    short_video = gr.Video(label="Vertical Short (9:16)")

    url_btn.click(process_from_url, inputs=[url_input], outputs=[original_video, short_video, status_text])
    file_btn.click(process_from_file, inputs=[file_input], outputs=[original_video, short_video, status_text])

if __name__ == "__main__":
    demo.launch(share=True, server_name="0.0.0.0", server_port=7860)
