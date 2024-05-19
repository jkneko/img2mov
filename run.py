import os
import tkinter as tk
from tkinterdnd2 import TkinterDnD, DND_FILES
from tkinter import messagebox
from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip
from moviepy.video.fx.all import fadein, fadeout, resize
from dotenv import load_dotenv
import uuid

# .envファイルの読み込み
load_dotenv()

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Drag and Drop Image Files")
        self.root.geometry("600x400")

        self.label = tk.Label(root, text="Drag and drop image files here", bg="lightgrey", width=80, height=20)
        self.label.pack(padx=10, pady=10, expand=True, fill=tk.BOTH)

        self.process_button = tk.Button(root, text="Create Video", command=self.create_video, state=tk.DISABLED)
        self.process_button.pack(pady=10)

        self.image_files = []
        self.bgm_file = os.path.expanduser(os.getenv("BGM_PATH", "./bgm.mp3"))

        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind('<<Drop>>', self.drop_files)

    def drop_files(self, event):
        self.image_files = self.root.tk.splitlist(event.data)
        self.label.config(text="\n".join(self.image_files))
        self.process_button.config(state=tk.NORMAL)

    def create_video(self):
        if not self.image_files:
            messagebox.showerror("Error", "Please select image files.")
            return

        if not os.path.exists(self.bgm_file):
            messagebox.showerror("Error", f"BGM file not found: {self.bgm_file}")
            return

        display_duration = int(os.getenv("DISPLAY_DURATION", 5))
        fade_duration = int(os.getenv("FADE_DURATION", 1))
        fps = int(os.getenv("FPS", 30))
        bitrate = os.getenv("BITRATE", "5000k")
        ffmpeg_preset = os.getenv("FFMPEG_PRESET", "slow")
        crf = int(os.getenv("CRF", 18))

        clips = []
        for i, image in enumerate(self.image_files):
            clip = ImageClip(image, duration=display_duration)
            
            # ズームイン効果を追加
            clip = resize(clip, lambda t: 1 + 0.05 * t)
            
            # 最初の画像にはフェードインを適用しない
            if i == 0:
                clip = fadeout(clip, fade_duration)
            else:
                clip = fadein(clip, fade_duration).fadeout(fade_duration)
            
            clips.append(clip)

        video = concatenate_videoclips(clips, method="compose")
        bgm = AudioFileClip(self.bgm_file)

        # 動画の長さがBGMの長さを超えないようにする
        if video.duration > bgm.duration:
            video = video.subclip(0, bgm.duration)
        
        bgm = bgm.subclip(0, video.duration)
        video = video.set_audio(bgm)

        # ランダムなUUIDを使用して一意のファイル名を生成
        output_filename = str(uuid.uuid4()) + ".mp4"

        # 画像の1枚目と同じパスに動画を保存
        output_path = os.path.join(os.path.dirname(self.image_files[0]), output_filename)
        video.write_videofile(output_path, codec="libx264", fps=fps, bitrate=bitrate, ffmpeg_params=["-preset", ffmpeg_preset, "-crf", str(crf)])
        messagebox.showinfo("Success", f"Video created successfully! Saved as {output_path}")

if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = App(root)
    root.mainloop()
