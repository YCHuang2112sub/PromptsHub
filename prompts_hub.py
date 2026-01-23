#!/usr/bin/env python3
"""
PromptHub - AlphaMind Edition (v2.0)
Refactored with CustomTkinter and Modular Architecture.
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import threading
import json
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
# Optional: Keyboard for advanced hotkeys if needed, but polling works for clipboard
try:
    import pyperclip
except ImportError:
    pyperclip = None


# Import Modular Tabs
# We need to add src to path if running from root
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
            
            # Categories table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    icon TEXT DEFAULT '📁'
                )
            """)
            
            # Prompts table
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
            
            # History table
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
            
            # Seed Categories
            cursor.execute("SELECT COUNT(*) FROM categories")
            if cursor.fetchone()[0] == 0:
                defaults = [
                    ("📝 Writing", "📝"), ("💻 Coding", "💻"), 
                    ("🔍 Analysis", "🔍"), ("🎨 Creative", "🎨"), 
                    ("🧠 Problem Solving", "🧠"), ("📊 Data", "📊"), 
                    ("🎯 Custom", "🎯")
                ]
                cursor.executemany("INSERT INTO categories (name, icon) VALUES (?, ?)", defaults)
                
            # Seed Prompts
            cursor.execute("SELECT COUNT(*) FROM prompts")
            if cursor.fetchone()[0] == 0:
                prompts = [
                    ("Code Review", "Review this code for bugs, performance issues, and readability:\n\n{text}", "💻 Coding"),
                    ("Summarize Text", "Summarize the following text in 3 bullet points:\n\n{text}", "📝 Writing"),
                    ("Explain Like I'm 5", "Explain the following concept simply:\n\n{text}", "🧠 Problem Solving"),
                    ("Fix Grammar", "Correct the grammar and improve the flow of this text:\n\n{text}", "📝 Writing"),
                    ("Generate Unit Tests", "Write Python unit tests for this function:\n\n{text}", "💻 Coding")
                ]
                cursor.executemany("INSERT INTO prompts (name, content, category) VALUES (?, ?, ?)", prompts)
            
            conn.commit()

    def add_category(self, name: str, icon: str = "📁") -> bool:
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
            cursor.execute(
                "INSERT INTO history (text, source) VALUES (?, ?)",
                (text, source)
            )
            return cursor.lastrowid

    def get_history(self, limit: int = 50, search_query: str = None) -> List[Dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if search_query:
                cursor.execute(
                    "SELECT * FROM history WHERE text LIKE ? ORDER BY timestamp DESC LIMIT ?",
                    (f"%{search_query}%", limit)
                )
            else:
                cursor.execute(
                    "SELECT * FROM history ORDER BY timestamp DESC LIMIT ?",
                    (limit,)
                )
                
            return [dict(row) for row in cursor.fetchall()]

    def delete_history_item(self, item_id: int):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM history WHERE id = ?", (item_id,))


class AlphaMindApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Window Setup
        self.title("PromptHub - AlphaMind")
        self.geometry("1100x700")
        
        # Database
        self.db = DatabaseManager()
        
        # State
        self.status_var = tk.StringVar(value="🚀 AlphaMind Ready")
        self.is_processing = False
        self.llm_prompt = "Refine the following text to be more professional, concise, and clear:\n\n{text}"
        
        # Setup Logic
        self.detect_llm_provider()
        self.setup_ui()
        
        # Start Clipboard Monitor (after UI setup)
        self.after(1000, self.start_clipboard_monitor)
        
        # Apply initial capture exclusion if set
        if self.live_capture_tab.exclude_var.get():
            self.after(500, lambda: self.set_capture_exclusion(True))
        
    def setup_ui(self):
        # 1. Header
        self.create_header()
        
        # 2. Main Content (Tabs)
        self.tab_view = ctk.CTkTabview(self)
        self.tab_view.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.tab_view.add("Live Capture")
        self.tab_view.add("Prompt Library")
        self.tab_view.add("LLM Playground")
        
        # Initialize Tabs
        self.live_capture_tab = LiveCaptureTab(self.tab_view.tab("Live Capture"), self)
        self.live_capture_tab.pack(fill="both", expand=True)
        
        self.prompt_library_tab = PromptLibraryTab(self.tab_view.tab("Prompt Library"), self)
        self.prompt_library_tab.pack(fill="both", expand=True)
        
        self.create_llm_playground(self.tab_view.tab("LLM Playground"))
        
        # 3. Footer
        self.create_footer()
        
    def create_header(self):
        header_frame = ctk.CTkFrame(self, height=50, corner_radius=0)
        header_frame.pack(fill="x", side="top")
        
        title_label = ctk.CTkLabel(header_frame, text="🧠 PromptHub", font=("Segoe UI", 20, "bold"))
        title_label.pack(side="left", padx=20, pady=10)
        
        subtitle_label = ctk.CTkLabel(header_frame, text="| AlphaMind Edition", font=("Segoe UI", 12))
        subtitle_label.pack(side="left", pady=10)

    def create_footer(self):
        footer_frame = ctk.CTkFrame(self, height=30, corner_radius=0)
        footer_frame.pack(fill="x", side="bottom")
        
        status_label = ctk.CTkLabel(footer_frame, textvariable=self.status_var, font=("Consolas", 10))
        status_label.pack(side="left", padx=10)
        
        provider_label = ctk.CTkLabel(footer_frame, text=f"Provider: {self.llm_provider.upper() if self.llm_provider else 'None'}", font=("Consolas", 10))
        provider_label.pack(side="right", padx=10)

    def create_llm_playground(self, parent):
        # Simple Chat Interface
        chat_frame = ctk.CTkFrame(parent)
        chat_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.chat_display = ctk.CTkTextbox(chat_frame, font=("Segoe UI", 12))
        self.chat_display.pack(fill="both", expand=True, pady=(0, 10))
        self.chat_display.insert("1.0", "🤖 Welcome to AlphaMind Chat. How can I help you?\n\n")
        self.chat_display.configure(state="disabled")
        
        input_frame = ctk.CTkFrame(chat_frame, fg_color="transparent")
        input_frame.pack(fill="x")
        
        self.chat_input = ctk.CTkEntry(input_frame, placeholder_text="Type your message...")
        self.chat_input.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.chat_input.bind('<Return>', lambda e: self.send_chat_message())
        
        send_btn = ctk.CTkButton(input_frame, text="Send", width=80, command=self.send_chat_message)
        send_btn.pack(side="right")

    # --- Shared Logic ---

    def detect_llm_provider(self):
        self.llm_provider = None
        self.llm_api_key = None
        
        if os.getenv("ANTHROPIC_API_KEY"):
            self.llm_provider = "claude"
            self.llm_api_key = os.getenv("ANTHROPIC_API_KEY")
        elif os.getenv("OPENAI_API_KEY"):
            self.llm_provider = "openai"
            self.llm_api_key = os.getenv("OPENAI_API_KEY")
        elif os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY"):
            self.llm_provider = "gemini"
            self.llm_api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

    def start_llm_processing(self, text, is_chat=False):
        if not self.llm_provider:
            self.status_var.set("❌ No API Key configured")
            return
            
        self.status_var.set("🤖 Processing...")
        # Use ThreadPoolExecutor or simple threading - keeping simple for now
        threading.Thread(target=self.process_llm_request, args=(text, is_chat), daemon=True).start()

    def process_llm_request(self, text, is_chat):
        # Determine prompt
        if is_chat:
            prompt = text
        else:
            prompt = self.llm_prompt.replace("{text}", text)
        
        try:
            response_text = ""
            if self.llm_provider == "gemini":
                # Basic Gemini Implementation
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={self.llm_api_key}"
                data = {"contents": [{"parts": [{"text": prompt}]}]}
                resp = requests.post(url, json=data)
                if resp.status_code == 200:
                    response_text = resp.json()['candidates'][0]['content']['parts'][0]['text']
                else:
                    response_text = f"Error: {resp.text}"
            elif self.llm_provider == "openai":
                # OpenAI Implementation
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.llm_api_key}"
                }
                data = {
                    "model": "gpt-4",
                    "messages": [{"role": "user", "content": prompt}]
                }
                resp = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
                if resp.status_code == 200:
                    response_text = resp.json()['choices'][0]['message']['content']
                else:
                     response_text = f"OpenAI Error: {resp.text}"
            elif self.llm_provider == "claude":
                # Claude Implementation (Simplified)
                headers = {
                     "x-api-key": self.llm_api_key,
                     "anthropic-version": "2023-06-01",
                     "content-type": "application/json"
                }
                data = {
                    "model": "claude-3-opus-20240229",
                    "max_tokens": 1024,
                    "messages": [{"role": "user", "content": prompt}]
                }
                resp = requests.post("https://api.anthropic.com/v1/messages", headers=headers, json=data)
                if resp.status_code == 200:
                     response_text = resp.json()['content'][0]['text']
                else:
                     response_text = f"Claude Error: {resp.text}"
             
            # Update UI
            self.after(0, lambda: self.finish_processing(response_text, is_chat))
            
        except Exception as e:
            self.after(0, lambda: self.finish_processing(f"Error: {str(e)}", is_chat))

    def finish_processing(self, response, is_chat):
        self.status_var.set("✅ Complete")
        if is_chat:
            self.chat_display.configure(state="normal")
            self.chat_display.insert("end", f"You: {self.chat_input.get()}\n")
            self.chat_display.insert("end", f"AI: {response}\n\n")
            self.chat_display.configure(state="disabled")
            self.chat_input.delete(0, "end")
        else:
            self.live_capture_tab.update_live_text(response)

    def send_chat_message(self):
        msg = self.chat_input.get().strip()
        if msg:
            self.start_llm_processing(msg, is_chat=True)

    def use_prompt_template(self, template):
        # Switch to Live Capture
        self.tab_view.set("Live Capture")
        
        # Apply Logic
        current = self.live_capture_tab.live_text.get("1.0", "end-1c").strip()
        if "{text}" in template:
            if current:
                new_text = template.replace("{text}", current)
                self.live_capture_tab.update_live_text(new_text)
                self.start_llm_processing(new_text, is_chat=False)
            else:
                self.live_capture_tab.update_live_text(template)
        else:
            self.live_capture_tab.update_live_text(template)

    # --- Feature: Clipboard Monitoring ---
    def start_clipboard_monitor(self):
        """Starts monitoring clipboard for changes"""
        if not pyperclip:
            self.status_var.set("⚠️ pyperclip not installed - clipboard sync disabled")
            return
            
        self.last_clipboard = pyperclip.paste()
        self.monitor_clipboard()
        
    def monitor_clipboard(self):
        """Polls clipboard every 1s"""
        try:
            current_clipboard = pyperclip.paste()
            if current_clipboard != self.last_clipboard:
                self.last_clipboard = current_clipboard
                # Update text area if Live Capture tab is open (or always)
                # We update it to make it 'live'
                self.live_capture_tab.update_live_text(current_clipboard)
                self.status_var.set("📋 Clipboard captured")
        except Exception:
            pass
        finally:
            self.after(1000, self.monitor_clipboard)

    # --- Feature: Screen Capture (Snipping Tool) ---
    def initiate_screen_capture(self, caller):
        """Launches the overlay for area selection"""
        self.withdraw() # Hide main app
        self.snipper = SnippingTool(self, caller)
        
    def screen_capture_complete(self, caller, img):
        """Callback when capture is done"""
        self.deiconify() # Show main app
        if img:
            caller.set_captured_image(img)
            self.status_var.set("📷 Screen area captured")
        else:
            self.status_var.set("❌ Capture cancelled")

    def extract_text_from_current_image(self, caller):
        # This is now generic Vision Processing
        if not hasattr(caller, 'current_image') or not caller.current_image:
            self.status_var.set("❌ No image captured")
            return
            
        self.status_var.set("🤖 Analyzing Image...")
        
        # Determine prompt
        user_prompt = "Extract all text from this image exactly as it appears."
        is_vision_chat = False
        
        # Check if Vision Chat Mode is active in LiveCaptureTab
        if hasattr(caller, 'vision_mode_var') and caller.vision_mode_var.get():
            user_text = caller.live_text.get("1.0", "end-1c").strip()
            # If user text is just the default placeholder, ignore it
            if "Vision Chat Active" not in user_text and user_text:
                user_prompt = user_text
                is_vision_chat = True
        
        # Run in thread
        threading.Thread(target=self.process_vision_request, args=(caller.current_image, user_prompt, is_vision_chat), daemon=True).start()
        
    def process_vision_request(self, image, prompt_text="Extract text", is_chat=False):
        try:
            # Convert image to base64
            import io
            import base64
            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            img_b64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
            
            text_result = "Vision Failed"
            
            print(f"\n[DIAGNOSTIC] Vision Request Started")
            print(f"[DIAGNOSTIC] Prompt: {prompt_text[:100]}...")
            
            if self.llm_provider == "gemini":
                 # Using the updated model name from chat implementation
                 url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={self.llm_api_key}"
                 data = {
                    "contents": [{
                        "parts": [
                            {"text": prompt_text},
                             {
                                "inline_data": {
                                    "mime_type": "image/png",
                                    "data": img_b64
                                }
                            }
                        ]
                    }]
                }
                 print(f"[DIAGNOSTIC] Calling Gemini API: {url.split('?')[0]}")
                 resp = requests.post(url, json=data)
                 print(f"[DIAGNOSTIC] Response Status: {resp.status_code}")
                 
                 if resp.status_code == 200:
                    try:
                        resp_json = resp.json()
                        text_result = resp_json['candidates'][0]['content']['parts'][0]['text']
                        print(f"[DIAGNOSTIC] Extraction Successful: {text_result[:50]}...")
                    except (KeyError, IndexError) as e:
                        print(f"[DIAGNOSTIC] JSON Parse Error: {e}")
                        print(f"[DIAGNOSTIC] Raw Response: {resp.text[:500]}")
                        text_result = "JSON Parse Error"
                 else:
                    print(f"[DIAGNOSTIC] API Error Body: {resp.text}")
                    text_result = f"Gemini Error: {resp.text}"
            
            # (Add other providers if needed)
            
            self.after(0, lambda: self.live_capture_tab.update_live_text(text_result))
            status_msg = "✅ Response Received" if is_chat else "✅ Text extracted"
            self.after(0, lambda: self.status_var.set(status_msg))
            
        except Exception as e:
            print(f"[DIAGNOSTIC] Unexpected Exception: {str(e)}")
            self.after(0, lambda: self.status_var.set(f"❌ Vision Error: {str(e)}"))

    def set_capture_exclusion(self, exclude: bool):
        """Set window display affinity to exclude from capture (Windows only)"""
        if platform.system() != "Windows":
            return
            
        try:
            hwnd = windll.user32.GetParent(self.winfo_id())
            if not hwnd:
                hwnd = self.winfo_id()
                
            # WDA_NONE = 0x00, WDA_MONITOR = 0x01, WDA_EXCLUDEFROMCAPTURE = 0x11
            # Note: WDA_EXCLUDEFROMCAPTURE requires Windows 10 Version 2004 or later
            WDA_EXCLUDEFROMCAPTURE = 0x11
            WDA_NONE = 0x00
            
            mode = WDA_EXCLUDEFROMCAPTURE if exclude else WDA_NONE
            windll.user32.SetWindowDisplayAffinity(hwnd, mode)
            
            if exclude:
                self.status_var.set("🔒 Window hidden from capture")
            else:
                self.status_var.set("🔓 Window visible to capture")
                
        except Exception as e:
            print(f"Exclusion Error: {e}")
            self.status_var.set("⚠️ Exclusion filed (Windows only)")



class SnippingTool(tk.Toplevel):
    def __init__(self, parent, caller):
        super().__init__(parent)
        self.parent = parent
        self.caller = caller
        self.attributes('-fullscreen', True)
        self.attributes('-alpha', 0.3)
        self.attributes('-topmost', True)
        self.configure(bg='black', cursor="cross")
        
        self.start_x = None
        self.start_y = None
        self.rect = None
        
        self.canvas = tk.Canvas(self, cursor="cross", bg="black", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.bind("<Escape>", self.cancel)

    def on_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline="red", width=2)

    def on_drag(self, event):
        self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)

    def on_release(self, event):
        if self.start_x is None:
            return
            
        x1, y1 = min(self.start_x, event.x), min(self.start_y, event.y)
        x2, y2 = max(self.start_x, event.x), max(self.start_y, event.y)
        
        # Ignore tiny selections
        if (x2 - x1) < 10 or (y2 - y1) < 10:
            self.cancel()
            return

        self.withdraw() # Hide overlay
        # Capture
        try:
            img = ImageGrab.grab(bbox=(x1, y1, x2, y2))
            self.parent.screen_capture_complete(self.caller, img)
        except Exception as e:
            print(e)
            self.parent.screen_capture_complete(self.caller, None)
            
        self.destroy()

    def cancel(self, event=None):
        self.parent.screen_capture_complete(self.caller, None)
        self.destroy()


if __name__ == "__main__":
    app = AlphaMindApp()
    app.mainloop()
