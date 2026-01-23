import os

path = 'prompts_hub.py'

content = r'''#!/usr/bin/env python3
"""
PromptHub - AlphaMind Edition (v3.0)
Refactored with CustomTkinter and Modular Architecture.
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import threading
import json
import queue
import os
import sys
import requests
from dotenv import load_dotenv
import sqlite3
from typing import Dict, List, Optional
from PIL import Image, ImageTk, ImageGrab
import platform
import ctypes
from ctypes import windll
import hashlib

# Optional: Keyboard for advanced hotkeys if needed, but polling works for clipboard
try:
    import pyperclip
except ImportError:
    pyperclip = None

# Import Modular Tabs
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from gui.tabs.live_capture import LiveCaptureTab
from gui.tabs.prompt_library import PromptLibraryTab

# Load environment variables
load_dotenv('.env.local')

# Setup CustomTkinter Theme
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class DatabaseManager:
    """Handles all SQLite database operations"""
    
    def __init__(self, db_path: str = "prompts_hub.db"):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        """Initialize database tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    icon TEXT DEFAULT ''
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS prompts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    content TEXT NOT NULL,
                    category TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    usage_count INTEGER DEFAULT 0
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    text TEXT NOT NULL,
                    source TEXT DEFAULT 'clipboard',
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_favorite BOOLEAN DEFAULT 0
                )
            """)
            conn.commit()
        self.seed_defaults()

    def seed_defaults(self):
        """Seed default categories and prompts if empty"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM categories")
            if cursor.fetchone()[0] == 0:
                defaults = [
                    ("Writing", ""), ("Coding", ""), 
                    ("Analysis", ""), ("Creative", ""), 
                    ("Problem Solving", ""), ("Data", ""), 
                    ("Custom", "")
                ]
                cursor.executemany("INSERT INTO categories (name, icon) VALUES (?, ?)", defaults)
                
            cursor.execute("SELECT COUNT(*) FROM prompts")
            if cursor.fetchone()[0] == 0:
                prompts = [
                    ("Code Review", "Review this code for bugs, performance issues, and readability:\n\n{text}", "Coding"),
                    ("Summarize Text", "Summarize the following text in 3 bullet points:\n\n{text}", "Writing"),
                    ("Explain Like I'm 5", "Explain the following concept simply:\n\n{text}", "Problem Solving"),
                    ("Fix Grammar", "Correct the grammar and improve the flow of this text:\n\n{text}", "Writing"),
                    ("Generate Unit Tests", "Write Python unit tests for this function:\n\n{text}", "Coding")
                ]
                cursor.executemany("INSERT INTO prompts (name, content, category) VALUES (?, ?, ?)", prompts)
            conn.commit()

    def add_category(self, name: str, icon: str = "") -> bool:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO categories (name, icon) VALUES (?, ?)", (name, icon))
                return True
        except sqlite3.IntegrityError:
            return False

    def get_categories(self) -> List[str]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM categories ORDER BY name")
            return [row[0] for row in cursor.fetchall()]

    def delete_category(self, name: str):
         with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM categories WHERE name = ?", (name,))

    def add_prompt(self, name: str, content: str, category: str) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO prompts (name, content, category) VALUES (?, ?, ?)",
                (name, content, category)
            )
            return cursor.lastrowid

    def get_prompts(self, category: str = None) -> List[Dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if category and category != "All":
                cursor.execute(
                    "SELECT * FROM prompts WHERE category = ? ORDER BY name",
                    (category,)
                )
            else:
                cursor.execute("SELECT * FROM prompts ORDER BY name")
            return [dict(row) for row in cursor.fetchall()]

    def delete_prompt(self, prompt_id: int):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM prompts WHERE id = ?", (prompt_id,))

    def add_history(self, text: str, source: str = "clipboard") -> int:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO history (text, source) VALUES (?, ?)", (text, source))
            return cursor.lastrowid

    def get_history(self, limit: int = 50, search_query: str = None) -> List[Dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            if search_query:
                cursor.execute("SELECT * FROM history WHERE text LIKE ? ORDER BY timestamp DESC LIMIT ?", (f"%{search_query}%", limit))
            else:
                cursor.execute("SELECT * FROM history ORDER BY timestamp DESC LIMIT ?", (limit,))
            return [dict(row) for row in cursor.fetchall()]

    def delete_history_item(self, item_id: int):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM history WHERE id = ?", (item_id,))

class AlphaMindApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("PromptHub - AlphaMind")
        self.geometry("1100x700")
        self.db = DatabaseManager()
        self.status_var = tk.StringVar(value="AlphaMind Ready")
        self.is_processing = False
        self.llm_prompt = "Refine the following text to be more professional, concise, and clear:\n\n{text}"
        self.detect_llm_provider()
        self.setup_ui()
        self.after(1000, self.start_clipboard_monitor)
        if hasattr(self, 'live_capture_tab') and self.live_capture_tab.exclude_var.get():
            self.after(500, lambda: self.set_capture_exclusion(True))

    def setup_ui(self):
        self.create_header()
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=10, pady=10)
        self.sidebar_visible = False
        self.sidebar_frame = ctk.CTkFrame(self.main_container, width=0)
        self.sidebar_frame.pack(side="left", fill="y", padx=0)
        self.tab_view = ctk.CTkTabview(self.main_container)
        self.tab_view.pack(side="right", fill="both", expand=True)
        self.tab_view.add("Live Capture")
        self.tab_view.add("Prompt Library")
        self.tab_view.add("LLM Playground")
        self.live_capture_tab = LiveCaptureTab(self.tab_view.tab("Live Capture"), self)
        self.live_capture_tab.pack(fill="both", expand=True)
        self.prompt_library_tab = PromptLibraryTab(self.tab_view.tab("Prompt Library"), self)
        self.prompt_library_tab.pack(fill="both", expand=True)
        self.setup_sidebar()
        self.create_llm_playground(self.tab_view.tab("LLM Playground"))
        self.create_footer()

    def setup_sidebar(self):
        self.sidebar_label = ctk.CTkLabel(self.sidebar_frame, text="Library Sidebar", font=("Segoe UI", 12, "bold"))
        self.sidebar_label.pack(pady=10)
        self.sidebar_library = PromptLibraryTab(self.sidebar_frame, self)
        self.sidebar_library.pack(fill="both", expand=True, padx=5, pady=5)

    def toggle_sidebar(self):
        if self.sidebar_visible:
            self.sidebar_frame.pack_forget()
            self.sidebar_visible = False
            self.status_var.set("Sidebar hidden")
        else:
            self.sidebar_frame.pack(side="left", fill="y", padx=(0, 10))
            self.sidebar_frame.configure(width=300)
            self.sidebar_visible = True
            self.status_var.set("Sidebar visible")

    def create_header(self):
        header_frame = ctk.CTkFrame(self, height=50, corner_radius=0)
        header_frame.pack(fill="x", side="top")
        self.sidebar_toggle_btn = ctk.CTkButton(header_frame, text="X", width=40, command=self.toggle_sidebar, fg_color="transparent", hover_color="#333")
        self.sidebar_toggle_btn.pack(side="left", padx=10)
        title_label = ctk.CTkLabel(header_frame, text="PromptHub", font=("Segoe UI", 20, "bold"))
        title_label.pack(side="left", padx=10, pady=10)

    def create_footer(self):
        footer_frame = ctk.CTkFrame(self, height=30, corner_radius=0)
        footer_frame.pack(fill="x", side="bottom")
        ctk.CTkLabel(footer_frame, textvariable=self.status_var, font=("Consolas", 10)).pack(side="left", padx=10)
        ctk.CTkLabel(footer_frame, text=f"Provider: {self.llm_provider.upper() if self.llm_provider else 'None'}", font=("Consolas", 10)).pack(side="right", padx=10)

    def create_llm_playground(self, parent):
        chat_frame = ctk.CTkFrame(parent)
        chat_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.chat_display = ctk.CTkTextbox(chat_frame, font=("Segoe UI", 12))
        self.chat_display.pack(fill="both", expand=True, pady=(0, 10))
        self.chat_display.insert("1.0", "Welcome to AlphaMind Chat.\n\n")
        self.chat_display.configure(state="disabled")
        input_frame = ctk.CTkFrame(chat_frame, fg_color="transparent")
        input_frame.pack(fill="x")
        self.chat_input = ctk.CTkEntry(input_frame, placeholder_text="Type your message...")
        self.chat_input.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.chat_input.bind('<Return>', lambda e: self.send_chat_message())
        ctk.CTkButton(input_frame, text="Send", width=80, command=self.send_chat_message).pack(side="right")

    def detect_llm_provider(self):
        self.llm_provider = None
        self.llm_api_key = None
        if os.getenv("ANTHROPIC_API_KEY"):
            self.llm_provider, self.llm_api_key = "claude", os.getenv("ANTHROPIC_API_KEY")
        elif os.getenv("OPENAI_API_KEY"):
            self.llm_provider, self.llm_api_key = "openai", os.getenv("OPENAI_API_KEY")
        elif os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY"):
            self.llm_provider, self.llm_api_key = "gemini", os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

    def start_llm_processing(self, text, is_chat=False, target_pane="live"):
        if not self.llm_provider:
            self.status_var.set("No API Key configured")
            return
        self.status_var.set("Processing...")
        threading.Thread(target=self.process_llm_request, args=(text, is_chat, target_pane), daemon=True).start()

    def process_llm_request(self, text, is_chat, target_pane):
        prompt = text if is_chat or "You are a Prompt Engineering expert" in text else self.llm_prompt.replace("{text}", text)
        try:
            response_text = ""
            if self.llm_provider == "gemini":
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={self.llm_api_key}"
                resp = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]})
                if resp.status_code == 200: response_text = resp.json()['candidates'][0]['content']['parts'][0]['text']
            elif self.llm_provider == "openai":
                resp = requests.post("https://api.openai.com/v1/chat/completions", headers={"Authorization": f"Bearer {self.llm_api_key}"}, json={"model": "gpt-4", "messages": [{"role": "user", "content": prompt}]})
                if resp.status_code == 200: response_text = resp.json()['choices'][0]['message']['content']
            elif self.llm_provider == "claude":
                resp = requests.post("https://api.anthropic.com/v1/messages", headers={"x-api-key": self.llm_api_key, "anthropic-version": "2023-06-01", "content-type": "application/json"}, json={"model": "claude-3-opus-20240229", "max_tokens": 1024, "messages": [{"role": "user", "content": prompt}]})
                if resp.status_code == 200: response_text = resp.json()['contents'][0]['text']
            self.after(0, lambda: self.finish_processing(response_text, is_chat, target_pane))
        except Exception as e:
            self.after(0, lambda: self.finish_processing(f"Error: {e}", is_chat, target_pane))

    def finish_processing(self, response, is_chat, target_pane):
        self.status_var.set("Complete")
        if is_chat:
            self.chat_display.configure(state="normal")
            self.chat_display.insert("end", f"AI: {response}\n\n")
            self.chat_display.configure(state="disabled")
            self.chat_input.delete(0, "end")
        else:
            self.live_capture_tab.update_live_text(response, pane=target_pane)

    def send_chat_message(self):
        msg = self.chat_input.get().strip()
        if msg:
            self.chat_display.configure(state="normal")
            self.chat_display.insert("end", f"You: {msg}\n")
            self.chat_display.configure(state="disabled")
            self.start_llm_processing(msg, is_chat=True)

    def start_clipboard_monitor(self):
        last_clipboard = ""
        while True:
            try:
                current = pyperclip.paste()
                if current != last_clipboard and current.strip():
                    last_clipboard = current
                    self.db.add_history(current)
                    self.after(0, lambda: self.live_capture_tab.update_live_text(current))
                    self.after(0, lambda: self.status_var.set("Clipboard captured"))
            except: pass
            import time
            time.sleep(1)

    def set_capture_exclusion(self, exclude: bool):
        if platform.system() != "Windows": return
        try:
            hwnd = windll.user32.GetParent(self.winfo_id()) or self.winfo_id()
            windll.user32.SetWindowDisplayAffinity(hwnd, 0x11 if exclude else 0x00)
            self.status_var.set("Window hidden from capture" if exclude else "Window visible")
        except: pass

    def screen_capture_complete(self, tab, img):
        tab.set_captured_image(img)

    def extract_text_from_current_image(self, tab):
        if hasattr(tab, 'current_image') and tab.current_image:
            self.process_vision_request(tab.current_image)

    def process_vision_request(self, image, prompt_text="Extract text", is_chat=False):
        try:
            import io, base64
            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            img_b64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
            if self.llm_provider == "gemini":
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={self.llm_api_key}"
                data = {"contents": [{"parts": [{"text": prompt_text}, {"inline_data": {"mime_type": "image/png", "data": img_b64}}]}]}
                resp = requests.post(url, json=data)
                if resp.status_code == 200:
                    res = resp.json()['candidates'][0]['content']['parts'][0]['text']
                    self.after(0, lambda: self.live_capture_tab.update_live_text(res))
        except: pass

class RegionMonitorWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Monitor")
        self.geometry("300x200+100+100")
        self.attributes('-alpha', 0.5, '-topmost', True)
        self.overrideredirect(True)
        self.bind("<ButtonPress-1>", self.start_move)
        self.bind("<B1-Motion>", self.do_move)
        self.canvas = tk.Canvas(self, highlightthickness=2, highlightbackground="#ae78ff")
        self.canvas.pack(fill="both", expand=True)
        tk.Button(self, text="X", command=self.close, bg='#f14c4c', fg='white').place(relx=1.0, rely=0.0, anchor="ne")

    def start_move(self, event):
        self.x, self.y = event.x, event.y
    def do_move(self, event):
        self.geometry(f"+{self.winfo_x() + event.x - self.x}+{self.winfo_y() + event.y - self.y}")
    def close(self):
        self.parent.stop_region_monitoring()
        self.destroy()

class AudioTranscriptionManager:
    def __init__(self, app):
        self.app = app
        self.is_recording = False
    def start_transcription(self):
        self.is_recording = True
        threading.Thread(target=self._recording_loop, daemon=True).start()
    def _recording_loop(self):
        import speech_recognition as sr
        r = sr.Recognizer()
        with sr.Microphone() as source:
            while self.is_recording:
                try:
                    audio = r.listen(source, timeout=5)
                    text = r.recognize_google(audio)
                    self.app.after(0, lambda t=text: self.app.live_capture_tab.update_live_text(f"[Audio] {t}\n", pane="after"))
                except: continue
    def stop_transcription(self):
        self.is_recording = False

if __name__ == "__main__":
    app = AlphaMindApp()
    app.region_monitor = None
    app.last_region_hash = None
    def check_region():
        if app.region_monitor:
            try:
                x, y, w, h = app.region_monitor.winfo_x(), app.region_monitor.winfo_y(), app.region_monitor.winfo_width(), app.region_monitor.winfo_height()
                app.region_monitor.attributes('-alpha', 0.0)
                app.update(); img = ImageGrab.grab(bbox=(x, y, x+w, y+h))
                app.region_monitor.attributes('-alpha', 0.5)
                hsh = hashlib.md5(img.tobytes()).hexdigest()
                if app.last_region_hash and hsh != app.last_region_hash:
                    app.screen_capture_complete(app.live_capture_tab, img)
                    app.extract_text_from_current_image(app.live_capture_tab)
                app.last_region_hash = hsh
            except: pass
            app.after(2000, check_region)
    app.check_region_change = check_region
    app.start_region_monitoring = lambda: (setattr(app, 'region_monitor', RegionMonitorWindow(app)), app.check_region_change())
    app.stop_region_monitoring = lambda: setattr(app, 'region_monitor', None)
    app.audio_manager = AudioTranscriptionManager(app)
    app.mainloop()
'''

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
