import gradio as gr
import os, shutil
from core.video_pipeline import download_youtube_video, crop_to_vertical
from core.script_to_video import synthesize_video_from_script
from core.auto_review import review_short

def _finish(raw_path, title, text_for_review, progress):
    progress(0.6, desc="✂️ AI Cropping to Vertical (9:16)...")
    base, _ = os.path.splitext(raw_path)
    output_path = f"{base}_vertical.mp4"
    crop_to_vertical(raw_path, output_path)
    progress(0.85, desc="📊 Running Automated AI Review...")
    review = review_short(output_path, text_for_review)
    progress(1.0, desc="✅ Done!")
    return raw_path, output_path, f"🎉 Successfully processed: {title}", review, output_path

def process_from_url(url, progress=gr.Progress()):
    if not url: return None, None, "⚠️ Please enter a valid YouTube URL.", "", None
    progress(0.2, desc="📥 Downloading Video...")
    try:
        raw_path, title = download_youtube_video(url)
    except Exception as e:
        return None, None, f"❌ Error downloading: {str(e)}", "", None
    return _finish(raw_path, title, title, progress)

def process_from_file(file, progress=gr.Progress()):
    if file is None: return None, None, "⚠️ Please upload a video file.", "", None
    progress(0.2, desc="📥 Loading uploaded video...")
    os.makedirs("downloads", exist_ok=True)
    raw_path = os.path.join("downloads", os.path.basename(file.name))
    shutil.copy(file.name, raw_path)
    return _finish(raw_path, "Uploaded Video", "", progress)

def process_from_script(script, progress=gr.Progress()):
    if not script or not script.strip(): return None, None, "⚠️ Please write a script first.", "", None
    progress(0.2, desc="🧠 Synthesizing AI voice & scenes...")
    try:
        out = synthesize_video_from_script(script)
    except Exception as e:
        return None, None, f"❌ {str(e)}", "", None
    progress(0.85, desc="📊 Running Automated AI Review...")
    review = review_short(out, script)
    progress(1.0, desc="✅ Done!")
    return None, out, "🎉 Synthesized a vertical Short from your script!", review, out

with gr.Blocks(theme=gr.themes.Soft(), title="Shorts AI SaaS", css="footer {visibility: hidden}") as demo:
    gr.Markdown("# 🎬 YouTube-to-Shorts AI Engine")
    gr.Markdown("Clip, synthesize, **auto-review**, and download vertical Shorts — 100% free & open-source.")

    with gr.Row():
        with gr.Column(scale=1):
            with gr.Tabs():
                with gr.TabItem("🔗 From YouTube"):
                    url_input = gr.Textbox(label="YouTube URL", placeholder="https://youtube.com/watch?v=...")
                    url_btn = gr.Button("✨ Generate Short", variant="primary")
                with gr.TabItem("📁 Upload File"):
                    file_input = gr.File(label="Upload MP4 video")
                    file_btn = gr.Button("✨ Generate Short from File", variant="primary")
                with gr.TabItem("📝 Script to Video"):
                    script_input = gr.Textbox(label="Your Script", lines=6,
                        placeholder="Each sentence becomes a scene with AI voiceover & captions...")
                    script_btn = gr.Button("🎙️ Synthesize Video", variant="primary")
            status_text = gr.Textbox(label="Status", interactive=False)
            download_file = gr.File(label="⬇️ Download your Short")

        with gr.Column(scale=2):
            with gr.Tabs():
                with gr.TabItem("Original Video"):
                    original_video = gr.Video(label="Source (16:9)")
                with gr.TabItem("AI Generated Short"):
                    short_video = gr.Video(label="Vertical Short (9:16)")
            review_output = gr.Markdown(label="AI Review")

    OUT = [original_video, short_video, status_text, review_output, download_file]
    url_btn.click(process_from_url, inputs=[url_input], outputs=OUT)
    file_btn.click(process_from_file, inputs=[file_input], outputs=OUT)
    script_btn.click(process_from_script, inputs=[script_input], outputs=OUT)

if __name__ == "__main__":
    demo.launch(share=True, server_name="0.0.0.0", server_port=7860)
