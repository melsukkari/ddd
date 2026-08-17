import gradio as gr
from core.video_pipeline import download_youtube_video, crop_to_vertical
import os

def process_video(url, progress=gr.Progress()):
    if not url:
        return None, None, "⚠️ Please enter a valid YouTube URL."
    
    progress(0.2, desc="📥 Downloading Video...")
    try:
        raw_path, title = download_youtube_video(url)
    except Exception as e:
        return None, None, f"❌ Error downloading: {str(e)}"
        
    progress(0.6, desc="✂️ AI Cropping to Vertical (9:16)...")
    output_path = f"downloads/{os.path.basename(raw_path).replace('.mp4', '_vertical.mp4')}"
    crop_to_vertical(raw_path, output_path)
    
    progress(1.0, desc="✅ Done!")
    return raw_path, output_path, f"🎉 Successfully processed: {title}"

with gr.Blocks(theme=gr.themes.Soft(), title="Shorts AI SaaS", css="footer {visibility: hidden}") as demo:
    gr.Markdown("# 🎬 YouTube-to-Shorts AI Engine")
    gr.Markdown("Paste a YouTube URL to auto-download, AI-analyze, and crop to vertical 9:16.")
    
    with gr.Row():
        with gr.Column(scale=1):
            url_input = gr.Textbox(label="YouTube URL", placeholder="https://youtube.com/watch?v=...")
            process_btn = gr.Button("✨ Generate Short", variant="primary")
            status_text = gr.Textbox(label="Status", interactive=False)
            
        with gr.Column(scale=2):
            with gr.Tabs():
                with gr.TabItem("Original Video"):
                    original_video = gr.Video(label="Source (16:9)")
                with gr.TabItem("AI Generated Short"):
                    short_video = gr.Video(label="Vertical Short (9:16)")

    process_btn.click(
        process_video, 
        inputs=[url_input], 
        outputs=[original_video, short_video, status_text]
    )

if __name__ == "__main__":
    demo.launch(share=True, server_name="0.0.0.0", server_port=7860)
