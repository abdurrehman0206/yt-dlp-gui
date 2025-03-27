import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import yt_dlp
import threading
from typing import Dict, Any
import os
from datetime import datetime
import webbrowser
import sys
class ModernButton(ttk.Button):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.bind('<Enter>', self.on_enter)
        self.bind('<Leave>', self.on_leave)

    def on_enter(self, e):
        self['style'] = 'Accent.TButton'

    def on_leave(self, e):
        self['style'] = 'TButton'

class YTDLPGui(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("YT-DLP-GUI")
        self.geometry("500x600")
        self.resizable(False, False)
        # self.iconphoto(True, tk.PhotoImage(file="./assets/icon.png"))
        
        if getattr(sys, 'frozen', False):
        # If running as a bundled exe
            icon_path = os.path.join(sys._MEIPASS, 'assets', 'icon.png')
        else:
        # If running as a script
            icon_path = './assets/icon.png'

        # Load the icon
        self.iconphoto(True, tk.PhotoImage(file=icon_path))
        # Configure style
        self.style = ttk.Style()
        self.style.configure("TButton", padding=6, font=('Helvetica', 10))
        self.style.configure("Accent.TButton", padding=6, background='#2196f3')
        self.style.configure("TEntry", padding=6)
        
        self.style.layout('Horizontal.TProgressbar', 
             [('Horizontal.Progressbar.trough',
               {'children': [('Horizontal.Progressbar.pbar',
                            {'side': 'left', 'sticky': 'ns'})],
                'sticky': 'nswe'})])
        self.style.configure('Horizontal.TProgressbar', 
                           thickness=10,
                           troughcolor='#E0E0E0',
                           background='#2196f3')
        
        self.style.configure("TLabel", font=('Helvetica', 10))
        self.style.configure("Header.TLabel", font=('Helvetica', 16, 'bold'))
        self.style.configure("Footer.TLabel", font=('Helvetica', 9), foreground='#666666')

        self.main_container = ttk.Frame(self, padding="20")
        self.main_container.grid(row=0, column=0, sticky="nsew")
        
        self.create_widgets()
        
    def create_widgets(self):
        # Header
        header_frame = ttk.Frame(self.main_container)
        header_frame.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        ttk.Label(header_frame, text="YT-DLP-GUI", style="Header.TLabel").pack()
        
        # URL Entry Frame
        url_frame = ttk.LabelFrame(self.main_container, text="Video URL", padding="10")
        url_frame.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(0, 10))
        
        self.url_entry = ttk.Entry(url_frame, width=70)
        self.url_entry.pack(fill="x", expand=True)
        
        # Settings Frame
        settings_frame = ttk.LabelFrame(self.main_container, text="Download Settings", padding="10")
        settings_frame.grid(row=2, column=0, columnspan=3, sticky="ew", pady=(0, 10))
        
        # Quality Selection
        quality_frame = ttk.Frame(settings_frame)
        quality_frame.pack(fill="x", pady=5)
        
        ttk.Label(quality_frame, text="Quality:").pack(side="left")
        self.quality_var = tk.StringVar(value="1080p")
        qualities = ["2160p", "1440p", "1080p", "720p", "480p", "360p", "240p", "144p"]
        self.quality_combo = ttk.Combobox(quality_frame, textvariable=self.quality_var, values=qualities, state="readonly", width=15)
        self.quality_combo.pack(side="left", padx=(10, 0))
        
        # Format Selection
        format_frame = ttk.Frame(settings_frame)
        format_frame.pack(fill="x", pady=5)
        
        ttk.Label(format_frame, text="Format:").pack(side="left")
        self.format_var = tk.StringVar(value="mp4")
        formats = ["mp4", "webm", "mp3", "m4a", "wav", "flac"]
        self.format_combo = ttk.Combobox(format_frame, textvariable=self.format_var, values=formats, state="readonly", width=15)
        self.format_combo.pack(side="left", padx=(10, 0))
        
        # Custom Name Option
        name_frame = ttk.Frame(settings_frame)
        name_frame.pack(fill="x", pady=5)
        
        self.custom_name_var = tk.BooleanVar(value=False)
        self.custom_name_check = ttk.Checkbutton(name_frame, text="Custom filename", variable=self.custom_name_var, 
                                                command=self.toggle_custom_name)
        self.custom_name_check.pack(side="left")
        
        self.custom_name_entry = ttk.Entry(name_frame, state='disabled', width=40)
        self.custom_name_entry.pack(side="left", padx=(10, 0), fill="x", expand=True)
        
        # Output Directory
        output_frame = ttk.Frame(settings_frame)
        output_frame.pack(fill="x", pady=5)
        
        ttk.Label(output_frame, text="Save to:").pack(side="left")
        self.output_dir = ttk.Entry(output_frame)
        self.output_dir.insert(0, os.path.expanduser("~\Downloads"))
        self.output_dir.pack(side="left", padx=(10, 5), fill="x", expand=True)
        
        browse_btn = ModernButton(output_frame, text="Browse", command=self.browse_directory)
        browse_btn.pack(side="left")
        
        # Advanced Options Frame
        advanced_frame = ttk.LabelFrame(self.main_container, text="Advanced Options", padding="10")
        advanced_frame.grid(row=3, column=0, columnspan=3, sticky="ew", pady=(0, 10))
        
        left_options = ttk.Frame(advanced_frame)
        left_options.pack(side="left", fill="x", expand=True)
        
        right_options = ttk.Frame(advanced_frame)
        right_options.pack(side="left", fill="x", expand=True)
        
        self.subtitle_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(left_options, text="Download Subtitles", variable=self.subtitle_var).pack(anchor="w")
        
        self.thumbnail_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(left_options, text="Download Thumbnail", variable=self.thumbnail_var).pack(anchor="w")
        
        self.playlist_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(right_options, text="Download Playlist", variable=self.playlist_var).pack(anchor="w")
        
        self.audio_only_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(right_options, text="Audio Only", variable=self.audio_only_var).pack(anchor="w")
        
        # Progress Frame
        progress_frame = ttk.Frame(self.main_container)
        progress_frame.grid(row=4, column=0, columnspan=3, sticky="ew", pady=(0, 10))
        
        self.filename_label = ttk.Label(progress_frame, text="", anchor="w")
        self.filename_label.pack(fill="x", pady=(0, 5))
        
        self.progress = ttk.Progressbar(progress_frame, length=300, mode='determinate')
        self.progress.pack(fill="x", pady=(5, 0))
        
        self.status_label = ttk.Label(progress_frame, text="Ready", anchor="center")
        self.status_label.pack(fill="x", pady=(5, 0))
        
        # Download Button
        self.download_btn = ModernButton(self.main_container, text="Download", command=self.start_download)
        self.download_btn.grid(row=5, column=0, columnspan=3, pady=(0, 20))
        
        # Footer
        footer_frame = ttk.Frame(self.main_container)
        footer_frame.grid(row=6, column=0, columnspan=3, sticky="ew")
        
        footer_text = ttk.Label(
            footer_frame, 
            text="Made with ❤️ by Abdur Rehman", 
            style="Footer.TLabel",
            cursor="hand2"
        )
        footer_text.pack()
        footer_text.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/abdurrehman0206"))

    def toggle_custom_name(self):
        if self.custom_name_var.get():
            self.custom_name_entry.configure(state='normal')
        else:
            self.custom_name_entry.configure(state='disabled')
            
    def browse_directory(self):
        directory = filedialog.askdirectory(initialdir=self.output_dir.get())
        if directory:
            self.output_dir.delete(0, tk.END)
            self.output_dir.insert(0, directory)
            
    def update_progress(self, d: Dict[str, Any]) -> None:
        if d['status'] == 'downloading':
            try:
                # Update filename display
                if '_filename' in d:
                    filename = os.path.basename(d['_filename'])
                    self.filename_label['text'] = f"Downloading: {filename}"
                
                total = d.get('total_bytes', 0) or d.get('total_bytes_estimate', 0)
                downloaded = d.get('downloaded_bytes', 0)
                if total > 0:
                    percentage = (downloaded / total) * 100
                    self.progress['value'] = percentage
                    speed = d.get('speed', 0)
                    if speed:
                        speed_mb = speed / 1024 / 1024  # Convert to MB/s
                        self.status_label['text'] = f"Progress: {percentage:.1f}% ({speed_mb:.1f} MB/s)"
                    else:
                        self.status_label['text'] = f"Progress: {percentage:.1f}%"
                    self.update_idletasks()
            except Exception as e:
                print(f"Error updating progress: {e}")
                
    def start_download(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a YouTube URL")
            return
            
        if self.custom_name_var.get() and not self.custom_name_entry.get().strip():
            messagebox.showerror("Error", "Please enter a custom filename or uncheck the custom filename option")
            return
            
        self.download_btn['state'] = 'disabled'
        self.progress['value'] = 0
        self.filename_label['text'] = ""
        
        # Configure output template
        if self.custom_name_var.get():
            output_template = os.path.join(
                self.output_dir.get(),
                f"{self.custom_name_entry.get().strip()}.%(ext)s"
            )
        else:
            output_template = os.path.join(
                self.output_dir.get(),
                '%(title)s.%(ext)s'
            )
        
        # Configure format based on audio_only and format selection
        if self.audio_only_var.get():
            format_spec = 'bestaudio/best'
            postprocessors = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': self.format_var.get(),
                'preferredquality': '192',
            }]
        else:
            if self.format_var.get() in ['mp3', 'wav', 'flac', 'm4a']:
                format_spec = 'bestaudio/best'
                postprocessors = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': self.format_var.get(),
                    'preferredquality': '192',
                }]
            else:
                format_spec = f'bestvideo[height<={self.quality_var.get().replace("p", "")}][ext={self.format_var.get()}]+bestaudio/best[ext={self.format_var.get()}]/best'
                postprocessors = [{
                    'key': 'FFmpegVideoRemuxer',
                    'preferedformat': self.format_var.get(),
                }]
        
        # Configure yt-dlp options
        ydl_opts = {
            'format': format_spec,
            'postprocessors': postprocessors,
            'progress_hooks': [self.update_progress],
            'outtmpl': output_template,
        }
        
        if self.subtitle_var.get():
            ydl_opts.update({
                'writesubtitles': True,
                'subtitleslangs': ['en'],
            })
            
        if self.thumbnail_var.get():
            ydl_opts.update({
                'writethumbnail': True,
                'postprocessors': ydl_opts['postprocessors'] + [{
                    'key': 'FFmpegMetadata',
                    'add_metadata': True,
                }],
            })
            
        if self.playlist_var.get():
            ydl_opts['yes_playlist'] = True
        else:
            ydl_opts['noplaylist'] = True
            
        # Start download in a separate thread
        thread = threading.Thread(target=self.download_video, args=(url, ydl_opts))
        thread.daemon = True
        thread.start()
        
    def download_video(self, url: str, ydl_opts: Dict[str, Any]):
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            self.status_label['text'] = "Download Complete!"
            self.filename_label['text'] = ""
            messagebox.showinfo("Success", "Download completed successfully!")
        except Exception as e:
            self.status_label['text'] = f"Error: {str(e)}"
            self.filename_label['text'] = ""
            messagebox.showerror("Error", f"Download failed: {str(e)}")
        finally:
            self.download_btn['state'] = 'normal'
            self.progress['value'] = 0
            
if __name__ == "__main__":
    app = YTDLPGui()
    app.mainloop()
