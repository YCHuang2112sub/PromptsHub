import customtkinter as ctk
import sounddevice as sd
import numpy as np
import threading
import queue
from utils.diagnostic_helper import debug_log
from datetime import datetime

class AudioTab(ctk.CTkFrame):
    def __init__(self, parent, app_instance):
        super().__init__(parent)
        self.app = app_instance
        self.is_recording = False
        self.audio_queue = queue.Queue()
        self.recording_buffer = []
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # 🎤 Audio Header & Control
        header = ctk.CTkFrame(self)
        header.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        # Device Selection
        ctk.CTkLabel(header, text="🎤 Audio Studio", font=("Segoe UI", 16, "bold"), text_color="#ae78ff").pack(side="left", padx=15, pady=10)
        
        self.devices = self.get_audio_devices()
        self.device_var = ctk.StringVar(value=self.devices[0] if self.devices else "No Device")
        self.device_menu = ctk.CTkOptionMenu(header, values=self.devices, variable=self.device_var, width=200)
        self.device_menu.pack(side="left", padx=5)
        
        self.record_btn = ctk.CTkButton(header, text="🔴 Record", width=120, fg_color="#f14c4c", hover_color="#d32f2f", command=self.toggle_record)
        self.record_btn.pack(side="left", padx=5)
        
        self.send_btn = ctk.CTkButton(header, text="📤 Send to AI", width=120, state="disabled", command=self.send_audio)
        self.send_btn.pack(side="left", padx=5)
        
        # Language Selection
        self.langs = {
            "English": "en-US",
            "Chinese (Simplified)": "zh-CN",
            "Chinese (Traditional)": "zh-TW",
            "Japanese": "ja-JP",
            "Korean": "ko-KR",
            "French": "fr-FR",
            "German": "de-DE",
            "Spanish": "es-ES"
        }
        self.lang_var = ctk.StringVar(value="English")
        ctk.CTkLabel(header, text="Target Language:", font=("Segoe UI", 10)).pack(side="left", padx=(15, 5))
        self.lang_menu = ctk.CTkOptionMenu(header, values=list(self.langs.keys()), variable=self.lang_var, width=150)
        self.lang_menu.pack(side="left", padx=5)
        
        # 📊 Visualizer (Canvas)
        self.viz_canvas = ctk.CTkCanvas(header, width=200, height=40, bg="#1e1e1e", highlightthickness=0)
        self.viz_canvas.pack(side="right", padx=20)
        self.viz_bars = []
        for i in range(20):
            bar = self.viz_canvas.create_rectangle(i*10, 40, i*10+8, 40, fill="#ae78ff", outline="")
            self.viz_bars.append(bar)
            
        # 📜 Dual Column Content
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.content.grid_columnconfigure(0, weight=1) # Transcription
        self.content.grid_columnconfigure(1, weight=1) # Insight
        self.content.grid_rowconfigure(1, weight=1)
        
        # column 0: Transcription
        ctk.CTkLabel(self.content, text="TRANSCRIPTION", font=("Segoe UI", 10, "bold"), text_color="gray").grid(row=0, column=0, sticky="w", padx=5)
        self.trans_text = ctk.CTkTextbox(self.content, font=("Segoe UI", 12), border_width=1, border_color="#333")
        self.trans_text.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        # column 1: Insights
        ctk.CTkLabel(self.content, text="AUDIO ANALYSIS", font=("Segoe UI", 10, "bold"), text_color="gray").grid(row=0, column=1, sticky="w", padx=5)
        self.insight_text = ctk.CTkTextbox(self.content, font=("Segoe UI", 12), border_width=1, border_color="#333")
        self.insight_text.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)
        
        self.trans_text.insert("1.0", "--- Audio Workspace ---\nSelect source and click Record.\n")
        self.insight_text.insert("1.0", "--- AI Insights will appear here ---")

        # Start visualizer poller
        self.update_visualizer()

    def get_audio_devices(self):
        devices = sd.query_devices()
        input_devices = []
        for i, dev in enumerate(devices):
            if dev['max_input_channels'] > 0:
                input_devices.append(f"{i}: {dev['name']}")
        return input_devices

    def toggle_record(self):
        if self.is_recording:
            self.stop_recording()
        else:
            self.start_recording()

    def start_recording(self):
        try:
            device_id = int(self.device_var.get().split(":")[0])
            self.is_recording = True
            self.recording_buffer = []
            self.record_btn.configure(text="⏹ Stop", fg_color="gray")
            self.send_btn.configure(state="disabled")
            
            def audio_callback(indata, frames, time, status):
                if status:
                    debug_log(f"Audio Status: {status}", level="error")
                self.audio_queue.put(indata.copy())
                if self.is_recording:
                    self.recording_buffer.append(indata.copy())

            self.stream = sd.InputStream(device=device_id, channels=1, callback=audio_callback, blocksize=1024)
            self.stream.start()
            self.add_trans_log("🎤 Recording...")
        except Exception as e:
            debug_log(f"Audio Error: {e}", level="error")
            self.is_recording = False

    def stop_recording(self):
        self.is_recording = False
        if hasattr(self, 'stream'):
            self.stream.stop()
            self.stream.close()
        self.record_btn.configure(text="🔴 Record", fg_color="#f14c4c")
        self.send_btn.configure(state="normal")
        self.add_trans_log("⏹ Stopped. Ready to send.")

    def send_audio(self):
        if not self.recording_buffer: return
        self.add_trans_log("📤 Processing audio...")
        # For now, we'll simulate the transcription using SpeechRecognition 
        # or pass the buffer to a manager. In a real app, you'd save to WAV or use API.
        threading.Thread(target=self._process_buffer, daemon=True).start()

    def _process_buffer(self):
        # Flatten buffer
        combined = np.concatenate(self.recording_buffer)
        # We need to pass this to the app's audio manager or process locally
        # Since SpeechRecognition needs a file/source, we'd ideally use a newer API or Whisper
        # For this refactor, we'll use the existing SpeechRecognition flow by saving to temp
        import scipy.io.wavfile as wav
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tf:
            wav.write(tf.name, 44100, (combined * 32767).astype(np.int16))
            temp_name = tf.name
            
        try:
            import speech_recognition as sr
            r = sr.Recognizer()
            lang_code = self.langs.get(self.lang_var.get(), "en-US")
            with sr.AudioFile(temp_name) as source:
                audio = r.record(source)
                text = r.recognize_google(audio, language=lang_code)
                self.app.after(0, lambda: self.update_transcription(text))
                # Also auto-enchant if text is long enough? Or just wait for user
                self.app.after(0, lambda: self.app.start_llm_processing(text, target_pane="audio_insight"))
        except Exception as e:
            self.app.after(0, lambda: self.add_trans_log(f"❌ Error: {e}"))
        finally:
            try: os.remove(temp_name)
            except: pass

    def update_visualizer(self):
        try:
            # Low latency update
            data = None
            while not self.audio_queue.empty():
                data = self.audio_queue.get_nowait()
            
            if data is not None:
                # Perform FFT for "frequency components"
                fft_data = np.abs(np.fft.rfft(data.flatten()))
                # Map to 20 bars
                chunks = np.array_split(fft_data, 20)
                for i, chunk in enumerate(chunks):
                    val = np.mean(chunk) * 100 # scale factor
                    height = min(40, max(2, int(val)))
                    self.viz_canvas.coords(self.viz_bars[i], i*10, 40-height, i*10+8, 40)
            elif not self.is_recording:
                # Decay bars
                for bar in self.viz_bars:
                    coords = self.viz_canvas.coords(bar)
                    if coords[1] < 38:
                        self.viz_canvas.coords(bar, coords[0], coords[1]+2, coords[2], 40)

        except: pass
        self.after(50, self.update_visualizer)

    def add_trans_log(self, message):
        self.trans_text.insert("end", f"\n[{datetime.now().strftime('%H:%M:%S')}] {message}")
        self.trans_text.see("end")

    def update_transcription(self, text):
        self.trans_text.insert("end", f"\n\n--- Transcription ---\n{text}")
        self.trans_text.see("end")

    def update_insight(self, insight):
        self.insight_text.insert("end", f"\n\n--- Analysis at {datetime.now().strftime('%H:%M:%S')} ---\n{insight}")
        self.insight_text.see("end")

    def update_live_text(self, text, pane="live"):
        if pane == "audio_insight":
            self.update_insight(text)
        else:
            self.update_transcription(text)

    def set_captured_image(self, img): pass
