#!/usr/bin/env python3
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

# Import Modular Tabs and Utils
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from gui.tabs.live_capture import VisionStudioTab
from gui.tabs.monitor_tab import MonitorTab
from gui.tabs.audio_tab import AudioTab
from gui.tabs.text_tab import TextTab
from gui.tabs.prompt_library import PromptLibraryTab
from utils.diagnostic_helper import setup_diagnostics, debug_log

# Initialize Diagnostics correctly
setup_diagnostics()
debug_log("AlphaMind system starting...")

# Optional: Keyboard for advanced hotkeys if needed, but polling works for clipboard
try:
    import pyperclip
except ImportError:
    pyperclip = None

# Load environment variables
load_dotenv('.env.local')
debug_log("Environment variables loaded.")

# Setup CustomTkinter Theme
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class DatabaseManager:
    """Handles all SQLite database operations"""
    
    def __init__(self, db_path: str = "prompts_hub.db"):
        debug_log(f"Initializing DatabaseManager with {db_path}...")
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        """Initialize database tables"""
        debug_log("Checking/Creating database tables...")
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

class ScreenSelector(tk.Toplevel):
    def __init__(self, callback):
        super().__init__()
        self.callback = callback
        self.attributes('-alpha', 0.2)
        self.attributes('-fullscreen', True)
        self.attributes('-topmost', True)
        self.canvas = tk.Canvas(self, cursor="cross", bg="grey", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.start_x = self.start_y = self.rect = None
        self.bind("<ButtonPress-1>", self.on_press)
        self.bind("<B1-Motion>", self.on_drag)
        self.bind("<ButtonRelease-1>", self.on_release)
        self.bind("<Escape>", lambda e: self.destroy())

    def on_press(self, event):
        self.start_x, self.start_y = event.x, event.y
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, 1, 1, outline='cyan', width=2)
    def on_drag(self, event):
        self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)
    def on_release(self, event):
        x1, y1, x2, y2 = self.canvas.coords(self.rect)
        # Convert canvas coords to screen coords
        sx1, sy1 = self.winfo_rootx() + x1, self.winfo_rooty() + y1
        sx2, sy2 = self.winfo_rootx() + x2, self.winfo_rooty() + y2
        
        # Withdraw immediately to capture what's underneath
        self.withdraw()
        import time; time.sleep(0.2)
        
        # Calculate bbox
        bx1, by1, bx2, by2 = min(sx1, sx2), min(sy1, sy2), max(sx1, sx2), max(sy1, sy2)
        img = ImageGrab.grab(bbox=(bx1, by1, bx2, by2))
        
        # Return image and coordinates
        self.callback((img, (bx1, by1, bx2 - bx1, by2 - by1)))
        self.destroy()

class AlphaMindApp(ctk.CTk):
    def __init__(self):
        debug_log("Initializing AlphaMindApp...")
        super().__init__()
        self.title("PromptHub - AlphaMind")
        self.geometry("1100x700")
        self.db = DatabaseManager()
        self.status_var = tk.StringVar(value="AlphaMind Ready")
        self.vision_cooldown = 0
        self.is_processing = False
        self.llm_prompt = "Refine the following text to be more professional, concise, and clear:\n\n{text}"
        debug_log("Detecting LLM provider...")
        self.detect_llm_provider()
        debug_log("Setting up UI...")
        self.setup_ui()
        self.after(1000, self.start_clipboard_monitor)
        # Apply initial exclusion from the consolidated app-level switch
        self.after(500, lambda: self.set_capture_exclusion(True))

    def setup_ui(self):
        # 1. Initialize variables used by UI components
        self.privacy_var = ctk.BooleanVar(value=True)
        
        # 2. Create UI Shell
        self.create_header()
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=10, pady=10)
        self.sidebar_visible = False
        self.sidebar_frame = ctk.CTkFrame(self.main_container, width=300)
        self.sidebar_frame.pack_propagate(False)
        self.sidebar_frame.pack_forget() 
        
        self.tab_view = ctk.CTkTabview(self.main_container)
        self.tab_view.pack(side="right", fill="both", expand=True)
        self.tab_view.add("Vision Studio")
        self.tab_view.add("Text Workspace")
        self.tab_view.add("Region Monitor")
        self.tab_view.add("Audio Intelligence")
        
        self.vision_tab = VisionStudioTab(self.tab_view.tab("Vision Studio"), self)
        self.vision_tab.pack(fill="both", expand=True)
        
        self.text_tab = TextTab(self.tab_view.tab("Text Workspace"), self)
        self.text_tab.pack(fill="both", expand=True)
        
        self.monitor_tab = MonitorTab(self.tab_view.tab("Region Monitor"), self)
        self.monitor_tab.pack(fill="both", expand=True)
        
        self.audio_tab = AudioTab(self.tab_view.tab("Audio Intelligence"), self)
        self.audio_tab.pack(fill="both", expand=True)
        
        self.setup_sidebar()
        self.create_footer()
        
        # Apply initial exclusion
        self.set_capture_exclusion(True)

    def setup_sidebar(self):
        self.sidebar_label = ctk.CTkLabel(self.sidebar_frame, text="Library Sidebar", font=("Segoe UI", 12, "bold"))
        self.sidebar_label.pack(pady=10)
        self.sidebar_library = PromptLibraryTab(self.sidebar_frame, self)
        self.sidebar_library.pack(fill="both", expand=True, padx=5, pady=5)

    def toggle_sidebar(self):
        if self.sidebar_visible:
            self.sidebar_frame.pack_forget()
            self.sidebar_visible = False
            self.status_var.set("Library Sidebar hidden")
        else:
            # Pack it before the tab_view to ensure it stays on the left
            self.tab_view.pack_forget()
            self.sidebar_frame.pack(side="left", fill="y", padx=(0, 10))
            self.sidebar_frame.configure(width=300)
            self.sidebar_frame.pack_propagate(False)
            self.tab_view.pack(side="right", fill="both", expand=True)
            self.sidebar_visible = True
            self.status_var.set("Library Sidebar visible")

    def create_header(self):
        header_frame = ctk.CTkFrame(self, height=50, corner_radius=0)
        header_frame.pack(fill="x", side="top")
        self.sidebar_toggle_btn = ctk.CTkButton(header_frame, text="? Library", width=120, command=self.toggle_sidebar, fg_color="#3e3e42", hover_color="#555")
        self.sidebar_toggle_btn.pack(side="left", padx=10)
        title_label = ctk.CTkLabel(header_frame, text="PromptHub", font=("Segoe UI", 20, "bold"))
        title_label.pack(side="left", padx=10, pady=10)
        
        # Privacy Mode Toggle (Top-Right)
        self.privacy_switch = ctk.CTkSwitch(header_frame, text="Hide App", variable=self.privacy_var, command=self.update_privacy_mode)
        self.privacy_switch.pack(side="right", padx=20)
        ctk.CTkLabel(header_frame, text="Privacy Mode:", font=("Segoe UI", 10)).pack(side="right", padx=0)

    def create_footer(self):
        footer_frame = ctk.CTkFrame(self, height=30, corner_radius=0)
        footer_frame.pack(fill="x", side="bottom")
        ctk.CTkLabel(footer_frame, textvariable=self.status_var, font=("Consolas", 10)).pack(side="left", padx=10)
        ctk.CTkLabel(footer_frame, text=f"Provider: {self.llm_provider.upper() if self.llm_provider else 'None'}", font=("Consolas", 10)).pack(side="right", padx=10)

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
        if target_pane == "text_studio":
            self.text_tab.update_output(response)
        elif target_pane == "audio_insight":
            self.audio_tab.update_live_text(response, pane="audio_insight")
        elif target_pane == "monitor":
            self.monitor_tab.update_insight(response)
        else:
            self.vision_tab.update_live_text(response, pane=target_pane)

    def use_prompt_template(self, content):
        """Loads a prompt template into the Vision Studio for immediate use"""
        debug_log("Applying prompt template from Library")
        self.vision_tab.update_live_text(content, pane="live")
        self.tab_view.set("Vision Studio")
        self.status_var.set("?? Prompt template loaded")

    def start_clipboard_monitor(self):
        debug_log("Starting clipboard monitor thread...")
        threading.Thread(target=self._clipboard_loop, daemon=True).start()

    def _clipboard_loop(self):
        import time
        last_clipboard = ""
        while True:
            try:
                current = pyperclip.paste()
                if current != last_clipboard and current.strip():
                    last_clipboard = current
                    self.db.add_history(current)
                    self.after(0, lambda t=current: self.vision_tab.update_live_text(t))
                    self.after(0, lambda: self.status_var.set("Clipboard captured"))
            except Exception as e:
                debug_log(f"Clipboard error: {e}", level="error")
            time.sleep(1)

    def update_privacy_mode(self):
        # Callback for the header switch
        exclude = self.privacy_var.get()
        self.set_capture_exclusion(exclude)

    def set_capture_exclusion(self, exclude: bool):
        if platform.system() != "Windows": return
        try:
            hwnd = windll.user32.GetParent(self.winfo_id()) or self.winfo_id()
            windll.user32.SetWindowDisplayAffinity(hwnd, 0x11 if exclude else 0x00)
            self.status_var.set(f"Privacy Mode: {'ON' if exclude else 'OFF'}")
        except: pass

    def initiate_screen_capture(self, tab):
        debug_log("Initiating screen capture...")
        ScreenSelector(lambda img: self.screen_capture_complete(tab, img))

    def initiate_screen_capture_for_monitor(self):
        # Stop existing monitoring before selecting a new region
        self.stop_region_monitoring()
        # Explicitly clear old region so user must drag new one
        if hasattr(self, 'last_selected_region'):
            del self.last_selected_region
        self.monitor_tab.image_preview.configure(image=None, text="Drag to select region...")
        # Specific trigger for the monitor tab
        self.initiate_screen_capture(self.monitor_tab)

    def screen_capture_complete(self, tab, result):
        if isinstance(result, tuple):
            img, coords = result
            if tab == self.monitor_tab:
                self.last_selected_region = coords
            tab.set_captured_image(img)
        else:
            tab.set_captured_image(result)

    def extract_text_from_current_image(self, tab):
        if hasattr(tab, 'current_image') and tab.current_image:
            target_lang = tab.lang_var.get() if hasattr(tab, 'lang_var') else "Original"
            prompt = (
                "1. Extract all text from this image exactly as it appears.\n"
                "2. Provide a professional analysis or summary."
            )
            if target_lang != "Original":
                prompt += f"\n3. Translate the analysis/summary to {target_lang}."
            
            prompt += (
                "\n\nIMPORTANT: Format your response exactly as follows:\n"
                "[EXTRACTED_TEXT]\n(raw extracted text here)\n"
                "[ANALYSIS]\n(your analysis or translation here)"
            )
            
            # Pass the tab itself to route the result back
            self.process_vision_request(tab.current_image, tab=tab, prompt_text=prompt)

    def process_vision_request(self, image, tab=None, prompt_text="Extract text", is_chat=False):
        if hasattr(self, 'vision_cooldown') and self.vision_cooldown > 0:
            if tab == self.monitor_tab:
                self.monitor_tab.add_log(f"⏳ Throttled: API rate limit hit. Retrying in {self.vision_cooldown*2}s...")
                return

        try:
            import io, base64
            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            img_b64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
            if self.llm_provider == "gemini":
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={self.llm_api_key}"
                data = {"contents": [{"parts": [{"text": prompt_text}, {"inline_data": {"mime_type": "image/png", "data": img_b64}}]}]}
                resp = requests.post(url, json=data)
                
                if resp.status_code == 429:
                    self.vision_cooldown = 10 # 10 cycles (20 seconds)
                    if tab == self.monitor_tab:
                        self.monitor_tab.add_log("⚠️ API Rate Limit (429) - Pausing monitoring for 20s.")
                    return

                if resp.status_code == 200:
                    res = resp.json()['candidates'][0]['content']['parts'][0]['text']
                    
                    if "[EXTRACTED_TEXT]" in res and "[ANALYSIS]" in res:
                        try:
                            ocr_part = res.split("[EXTRACTED_TEXT]")[1].split("[ANALYSIS]")[0].strip()
                            ai_part = res.split("[ANALYSIS]")[1].strip()
                            self.after(0, lambda: tab.update_extracted_text(ocr_part) if hasattr(tab, 'update_extracted_text') else None)
                            self.after(0, lambda: tab.update_insight(ai_part) if hasattr(tab, 'update_insight') else None)
                        except:
                            self.after(0, lambda: tab.update_live_text(res, pane="after") if hasattr(tab, 'update_live_text') else None)
                    else:
                        # Route to the appropriate tab depending on where the request came from
                        self.after(0, lambda: tab.update_live_text(res, pane="after") if hasattr(tab, 'update_live_text') else None)
                        # If it's the monitor tab, use its specific update method
                        if hasattr(tab, 'update_insight'):
                            self.after(0, lambda: tab.update_insight(res))
        except Exception as e:
            debug_log(f"Vision Request Error: {e}")

    def start_region_monitoring(self):
        if not hasattr(self, 'last_selected_region') or not self.last_selected_region:
            messagebox.showwarning("No Region", "Please click 'Select Region' first to define a surveillance area.")
            return

        if not hasattr(self, 'region_monitor') or not self.region_monitor:
            self.region_monitor = RegionMonitorWindow(self)
            
            # Use the last dragged area if available
            if hasattr(self, 'last_selected_region'):
                x, y, w, h = self.last_selected_region
                self.region_monitor.geometry(f"{int(w)}x{int(h)}+{int(x)}+{int(y)}")
                self.monitor_tab.add_log(f"📍 Resuming region: {int(w)}x{int(h)} at {int(x)},{int(y)}")
            
            self.status_var.set("Region monitoring active")
            self.last_region_hash = None
            self.check_region_change()

    def stop_region_monitoring(self):
        if hasattr(self, 'region_monitor') and self.region_monitor:
            try: self.region_monitor.destroy()
            except: pass
            self.region_monitor = None
            self.status_var.set("Region monitoring stopped")

    def check_region_change(self):
        if hasattr(self, 'vision_cooldown') and self.vision_cooldown > 0:
            self.vision_cooldown -= 1

        if hasattr(self, 'region_monitor') and self.region_monitor:
            try:
                x, y, w, h = self.region_monitor.winfo_x(), self.region_monitor.winfo_y(), self.region_monitor.winfo_width(), self.region_monitor.winfo_height()
                self.region_monitor.attributes('-alpha', 0.0)
                self.update(); img = ImageGrab.grab(bbox=(x, y, x+w, y+h))
                self.region_monitor.attributes('-alpha', 0.5)
                hsh = hashlib.md5(img.tobytes()).hexdigest()
                if hsh != getattr(self, 'last_region_hash', None):
                    self.after(0, lambda: self.monitor_tab.add_log("?? Change detected. Processing..."))
                    self.screen_capture_complete(self.monitor_tab, img)
                    self.extract_text_from_current_image(self.monitor_tab)
                self.last_region_hash = hsh
            except: pass
            self.after(2000, self.check_region_change)


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
        new_x = int(self.winfo_x() + event.x - self.x)
        new_y = int(self.winfo_y() + event.y - self.y)
        self.geometry(f"+{new_x}+{new_y}")
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
                    # Use the new Audio Intelligence tab
                    self.app.after(0, lambda t=text: self.app.audio_tab.update_transcription(t))
                except: continue
    def stop_transcription(self):
        self.is_recording = False

if __name__ == "__main__":
    debug_log("Entry point reached.")
    app = AlphaMindApp()
    app.audio_manager = AudioTranscriptionManager(app)
    debug_log("Starting mainloop...")
    app.mainloop()
