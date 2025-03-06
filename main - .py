import os
import whisper
import tkinter as tk
from tkinter import filedialog, messagebox
from moviepy.editor import *
from PIL import ImageFont  # ✅ PIL (Pillow) इम्पोर्ट किया

# ❌ ImageMagick को पूरी तरह से डिसेबल करें
if "IMAGEMAGICK_BINARY" in os.environ:
    del os.environ["IMAGEMAGICK_BINARY"]

# ✅ सही फ़ॉन्ट सेट करें
def get_valid_font():
    try:
        # 🎨 Bebas Neue फॉन्ट का पथ सेट करें
        font_path = "C:/Users/YourUsername/Fonts/BebasNeue-Regular.ttf"  # यहाँ फॉन्ट का सही पथ दें
        ImageFont.truetype(font_path, 80)
        return font_path
    except Exception as e:
        print(f"⚠️ Warning: {e}, Bebas Neue फॉन्ट नहीं मिला, डिफ़ॉल्ट फॉन्ट का उपयोग किया जा रहा है।")
        return "sans-serif"

def generate_caption(audio_path):
    """ 🎙️ ऑडियो से टेक्स्ट जेनरेट करें """
    try:
        model = whisper.load_model("small")
        result = model.transcribe(audio_path)
        print("Generated Caption:", result["text"])  # Debugging के लिए
        return result["text"]
    except Exception as e:
        print(f"Error in transcription: {e}")
        return ""

def split_text(text, max_length=50):
    """ 🔠 लंबे टेक्स्ट को छोटे-छोटे ब्लॉक्स में तोड़ें """
    words = text.split()
    lines = []
    line = ""

    for word in words:
        if len(line) + len(word) < max_length:
            line += " " + word
        else:
            lines.append(line.strip())
            line = word
    lines.append(line.strip())
    return lines

def create_captions(video, captions):
    """ 📝 वीडियो पर स्टाइलिश कैप्शन जोड़ें """
    w, h = video.size
    duration_per_caption = video.duration / len(captions)
    font_used = get_valid_font()

    text_clips = []
    start_time = 0

    for i, caption in enumerate(captions):
        text_color = "yellow" if i % 2 == 0 else "white"

        # ✅ अब यह केवल PIL (Pillow) से टेक्स्ट रेंडर करेगा
        text_clip = TextClip(
            caption, fontsize=80, color=text_color, stroke_color="black",
            stroke_width=5, font=font_used, method="caption", size=(w - 100, None)
        ).set_position(("center", h - 200)).set_duration(duration_per_caption)

        # ⏳ कैप्शन को fade-in effect दें (smooth entry effect)
        text_clip = text_clip.crossfadein(0.5)
        text_clips.append(text_clip.set_start(start_time))
        start_time += duration_per_caption

    return CompositeVideoClip([video] + text_clips)

def add_captions(input_path, output_path):
    file_extension = os.path.splitext(input_path)[1].lower()

    if file_extension == ".mp3":
        print("Processing MP3 file...")
        audio_clip = AudioFileClip(input_path)
        captions = generate_caption(input_path)
        captions_list = split_text(captions)

        # ✅ ग्रीन बैकग्राउंड वीडियो (1080x1920) बनाएं
        video = ColorClip(size=(1080, 1920), color=(0, 255, 0), duration=audio_clip.duration)  # 🟩 ग्रीन स्क्रीन
        video = video.set_audio(audio_clip)
    elif file_extension in [".mp4", ".mov", ".avi"]:
        print("Processing Video file...")
        video = VideoFileClip(input_path)
        audio_clip = video.audio  # 🔹 MP4 के लिए ऑडियो सेट करो
        captions = generate_caption(input_path)
        captions_list = split_text(captions)
    else:
        messagebox.showerror("Error", "Unsupported file format! Only MP3 and MP4 are supported.")
        return

    final_clip = create_captions(video, captions_list)

    try:
        final_clip.write_videofile(output_path, fps=60, codec="libx264", bitrate="8000k")
        messagebox.showinfo("Success", "Video with captions saved successfully!")
    except Exception as e:
        print(f"Error saving video: {e}")

def browse_file(entry):
    file_path = filedialog.askopenfilename(filetypes=[("MP4 & MP3 Files", "*.mp4;*.mp3")])
    entry.delete(0, tk.END)
    entry.insert(0, file_path)

def process_file():
    input_path = file_entry.get()
    output_path = filedialog.asksaveasfilename(defaultextension=".mp4", filetypes=[("MP4 Files", "*.mp4")])
    
    if input_path and output_path:
        add_captions(input_path, output_path)

# 🎨 GUI (User Interface)
root = tk.Tk()
root.title("Zeemo Alternative - Green Screen Captions")

tk.Label(root, text="Select MP4 or MP3 File:").pack()
file_entry = tk.Entry(root, width=50)
file_entry.pack()
tk.Button(root, text="Browse", command=lambda: browse_file(file_entry)).pack()

tk.Button(root, text="Generate Captions", command=process_file).pack()

root.mainloop()
