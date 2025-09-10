#!/usr/bin/env python3
"""
Unified Clipboard & OCR Manager
A clean, minimal tool for clipboard monitoring, screen OCR, and LLM text processing.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import os
import sys
import threading
import time
import base64
import io
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Import env utilities
sys.path.append(str(Path(__file__).parent / "src"))
try:
    from lib.env_utils.env_utils import load_env_file, set_env_vars
    ENV_UTILS_AVAILABLE = True
except ImportError:
    ENV_UTILS_AVAILABLE = False
    print("Warning: env_utils not available. Using direct environment variable access.")

# Required imports with availability checks
try:
    import keyboard
    KEYBOARD_AVAILABLE = True
except ImportError:
    KEYBOARD_AVAILABLE = False
    print("Warning: keyboard library not available. Install with: pip install keyboard")

try:
    import pyperclip
    PYPERCLIP_AVAILABLE = True
except ImportError:
    PYPERCLIP_AVAILABLE = False
    print("Warning: pyperclip not available. Install with: pip install pyperclip")

try:
    from PIL import Image, ImageGrab, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("Warning: PIL not available. Install with: pip install Pillow")

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("Warning: requests not available. Install with: pip install requests")

try:
    import ctypes
    from ctypes import wintypes
    CTYPES_AVAILABLE = True
except ImportError:
    CTYPES_AVAILABLE = False
    print("Warning: ctypes not available for Windows screen capture protection")


class ClipboardOCRManager:
    def __init__(self):
        # Load environment variables first
        self.load_environment()
        
        self.root = tk.Tk()
        self.root.title("📋 Clipboard & OCR Manager")
        self.root.geometry("900x600")
        self.root.attributes('-topmost', True)
        
        # Storage setup
        self.storage_dir = Path.home() / ".clipboard_manager"
        self.storage_dir.mkdir(exist_ok=True)
        self.items_dir = self.storage_dir / "items"
        self.items_dir.mkdir(exist_ok=True)
        self.settings_file = self.storage_dir / "settings.json"
        self.index_file = self.storage_dir / "index.json"
        
        # Data
        self.stored_items = []
        self.current_image = None
        self.clipboard_monitoring = False
        self.last_clipboard = ""
        
        # OCR panel state
        self.ocr_expanded = False
        
        # Default LLM prompt
        self.llm_prompt = """Explain this text clearly and concisely:
- What does it do/mean?
- Key points to understand
- Any important warnings or notes

Text to explain:
{text}"""
        
        # LLM provider detection
        self.detect_llm_provider()
        
        # Setup
        self.load_settings()
        self.load_items()
        self.setup_ui()
        
        # Apply Windows screen capture protection if available
        if CTYPES_AVAILABLE and sys.platform == 'win32':
            self.apply_screen_capture_protection()
        
        # Start monitoring
        self.start_clipboard_monitoring()
        
    def load_environment(self):
        """Load environment variables from .env file"""
        if ENV_UTILS_AVAILABLE:
            try:
                # Try to load .env file
                env_vars = load_env_file(".env")
                set_env_vars(env_vars)
                print(f"Loaded {len(env_vars)} environment variables from .env file")
            except FileNotFoundError:
                print("No .env file found. Using system environment variables.")
                print("Tip: Copy .env.template to .env and add your API keys")
            except Exception as e:
                print(f"Error loading .env file: {e}")
        else:
            print("Using system environment variables only")
        
    def detect_llm_provider(self):
        """Auto-detect available LLM provider"""
        self.llm_provider = None
        self.llm_api_key = None
        
        # Check for Claude (Anthropic)
        claude_key = os.getenv("ANTHROPIC_API_KEY") or os.getenv("CLAUDE_API_KEY")
        if claude_key:
            self.llm_provider = "claude"
            self.llm_api_key = claude_key
            self.llm_model = "claude-3-5-sonnet-20241022"
            return
            
        # Check for OpenAI
        openai_key = os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_KEY")
        if openai_key:
            self.llm_provider = "openai"
            self.llm_api_key = openai_key
            self.llm_model = "gpt-4-vision-preview"
            return
            
        # Check for Gemini
        gemini_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if gemini_key:
            self.llm_provider = "gemini"
            self.llm_api_key = gemini_key
            self.llm_model = "gemini-pro-vision"
            return
            
        print("No LLM API keys found in environment variables")
    
    def setup_ui(self):
        """Setup the main user interface"""
        # OCR Panel (collapsible)
        self.setup_ocr_panel()
        
        # Main content area
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Left panel - Live Capture
        self.setup_capture_panel(main_frame)
        
        # Right panel - Stored Items
        self.setup_storage_panel(main_frame)
    
    def setup_ocr_panel(self):
        """Collapsible OCR panel at top"""
        # Toggle button
        self.ocr_toggle = ttk.Button(self.root, 
                                     text="▼ Screen OCR", 
                                     command=self.toggle_ocr_panel)
        self.ocr_toggle.pack(fill='x', padx=5, pady=2)
        
        # Collapsible frame (initially hidden)
        self.ocr_frame = ttk.LabelFrame(self.root, text="Screen OCR")
        
        # OCR content
        content = ttk.Frame(self.ocr_frame)
        content.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Image preview
        self.image_label = tk.Label(content, text="[No image captured]", 
                                    relief='solid', width=25, height=8,
                                    background='white', anchor='center')
        self.image_label.pack(side='left', padx=5)
        
        # Control buttons
        btn_frame = ttk.Frame(content)
        btn_frame.pack(side='left', padx=10, fill='y')
        
        ttk.Button(btn_frame, text="📷 Crop Screen", 
                  command=self.crop_screen).pack(pady=2)
        ttk.Button(btn_frame, text="🤖 Extract to Capture", 
                  command=self.extract_to_capture).pack(pady=2)
        
        # Status
        self.ocr_status = ttk.Label(content, text="Ready", foreground="green")
        self.ocr_status.pack(side='left', padx=5)
    
    def setup_capture_panel(self, parent):
        """Left panel - Live Capture"""
        left_frame = ttk.LabelFrame(parent, text="Live Capture")
        left_frame.pack(side='left', fill='both', expand=True, padx=5)
        
        # Status
        status_frame = ttk.Frame(left_frame)
        status_frame.pack(fill='x', padx=5, pady=2)
        
        self.monitor_status = ttk.Label(status_frame, text="● Monitoring Ctrl+C", 
                                       foreground="green")
        self.monitor_status.pack(side='left')
        
        # Capture text area
        self.capture_text = scrolledtext.ScrolledText(left_frame, height=20, wrap='word')
        self.capture_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Action buttons
        btn_frame = ttk.Frame(left_frame)
        btn_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(btn_frame, text="Store →", 
                  command=self.store_current).pack(side='left', padx=2)
        ttk.Button(btn_frame, text="🤖 Process by LLM", 
                  command=self.process_by_llm).pack(side='left', padx=2)
        ttk.Button(btn_frame, text="⚙️", 
                  command=self.edit_prompt,
                  width=3).pack(side='left', padx=2)
    
    def setup_storage_panel(self, parent):
        """Right panel - Stored Items"""
        right_frame = ttk.LabelFrame(parent, text="Stored Items")
        right_frame.pack(side='right', fill='both', expand=True, padx=5)
        
        # Search bar
        search_frame = ttk.Frame(right_frame)
        search_frame.pack(fill='x', padx=5, pady=2)
        
        ttk.Label(search_frame, text="🔍").pack(side='left')
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.on_search_change)
        
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side='left', fill='x', expand=True, padx=2)
        
        # Items list with scrollbar
        list_frame = ttk.Frame(right_frame)
        list_frame.pack(fill='both', expand=True, padx=5)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side='right', fill='y')
        
        # Listbox
        self.stored_listbox = tk.Listbox(list_frame, 
                                         yscrollcommand=scrollbar.set,
                                         font=('Courier', 9))
        self.stored_listbox.pack(fill='both', expand=True)
        scrollbar.config(command=self.stored_listbox.yview)
        
        # Bind double-click to copy
        self.stored_listbox.bind('<Double-1>', lambda e: self.copy_selected())
        
        # Storage info
        self.storage_info = ttk.Label(right_frame, text="Storage: ~/.clipboard_manager/")
        self.storage_info.pack(padx=5, pady=2)
        
        # Action buttons
        btn_frame = ttk.Frame(right_frame)
        btn_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(btn_frame, text="📋 Copy", 
                  command=self.copy_selected).pack(side='left', padx=2)
        ttk.Button(btn_frame, text="🗑️ Delete", 
                  command=self.delete_selected).pack(side='left', padx=2)
        ttk.Button(btn_frame, text="📤 Export", 
                  command=self.export_items).pack(side='left', padx=2)
        
        # Load items
        self.refresh_stored_list()
    
    def toggle_ocr_panel(self):
        """Toggle OCR panel visibility"""
        if self.ocr_expanded:
            # Collapse
            self.ocr_frame.pack_forget()
            self.ocr_toggle.config(text="▼ Screen OCR")
            self.ocr_expanded = False
        else:
            # Expand
            self.ocr_frame.pack(after=self.ocr_toggle, fill='x', padx=5, pady=2)
            self.ocr_toggle.config(text="▲ Screen OCR")
            self.ocr_expanded = True
    
    def start_clipboard_monitoring(self):
        """Start monitoring clipboard changes"""
        if not KEYBOARD_AVAILABLE or not PYPERCLIP_AVAILABLE:
            self.monitor_status.config(text="● Missing libraries", foreground="red")
            messagebox.showerror("Missing Dependencies", 
                               "Please install: pip install keyboard pyperclip")
            return
        
        try:
            self.last_clipboard = pyperclip.paste()
            
            def on_ctrl_c():
                time.sleep(0.1)  # Let clipboard update
                text = pyperclip.paste()
                if text != self.last_clipboard and text.strip():
                    self.last_clipboard = text
                    self.root.after(0, lambda: self.update_live_capture(text))
            
            keyboard.add_hotkey('ctrl+c', on_ctrl_c)
            self.clipboard_monitoring = True
            self.monitor_status.config(text="● Monitoring Ctrl+C", foreground="green")
            
        except Exception as e:
            self.monitor_status.config(text="● Monitor failed", foreground="red")
            print(f"Clipboard monitoring error: {e}")
    
    def update_live_capture(self, text):
        """Update live capture area - universal entry point"""
        self.capture_text.delete(1.0, tk.END)
        self.capture_text.insert(1.0, text)
        
        # Flash highlight
        self.capture_text.config(bg='#ffffcc')
        self.root.after(300, lambda: self.capture_text.config(bg='white'))
    
    def crop_screen(self):
        """Interactive screen cropping"""
        if not PIL_AVAILABLE:
            messagebox.showerror("Missing PIL", "Please install: pip install Pillow")
            return
        
        self.ocr_status.config(text="Select screen region...", foreground="blue")
        self.root.withdraw()
        
        try:
            # Create fullscreen selection overlay
            overlay = tk.Toplevel()
            overlay.attributes('-fullscreen', True)
            overlay.attributes('-alpha', 0.3)
            overlay.attributes('-topmost', True)
            overlay.configure(bg='black')
            
            # Canvas for selection
            canvas = tk.Canvas(overlay, highlightthickness=0, bg='black')
            canvas.pack(fill='both', expand=True)
            
            # Selection state
            start_x = start_y = None
            rect = None
            
            def on_mouse_down(event):
                nonlocal start_x, start_y
                start_x, start_y = event.x, event.y
                
            def on_mouse_drag(event):
                nonlocal rect
                if rect:
                    canvas.delete(rect)
                rect = canvas.create_rectangle(
                    start_x, start_y, event.x, event.y,
                    outline='red', width=2
                )
                
            def on_mouse_up(event):
                nonlocal start_x, start_y
                overlay.destroy()
                
                if start_x and start_y:
                    # Calculate region
                    x1, y1 = min(start_x, event.x), min(start_y, event.y)
                    x2, y2 = max(start_x, event.x), max(start_y, event.y)
                    
                    if abs(x2 - x1) > 10 and abs(y2 - y1) > 10:
                        # Capture region
                        self.current_image = ImageGrab.grab(bbox=(x1, y1, x2, y2))
                        self.show_image_preview()
                        self.ocr_status.config(text="✓ Image captured", foreground="green")
                    else:
                        self.ocr_status.config(text="Selection too small", foreground="orange")
                
                self.root.deiconify()
            
            def on_escape(event):
                overlay.destroy()
                self.root.deiconify()
                self.ocr_status.config(text="Selection cancelled", foreground="orange")
            
            canvas.bind('<Button-1>', on_mouse_down)
            canvas.bind('<B1-Motion>', on_mouse_drag)
            canvas.bind('<ButtonRelease-1>', on_mouse_up)
            overlay.bind('<Escape>', on_escape)
            canvas.focus_set()
            
        except Exception as e:
            self.root.deiconify()
            self.ocr_status.config(text=f"Crop failed: {e}", foreground="red")
    
    def show_image_preview(self):
        """Show cropped image preview"""
        if self.current_image:
            # Resize for preview
            img = self.current_image.copy()
            img.thumbnail((200, 150), Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage
            self.preview_image = ImageTk.PhotoImage(img)
            self.image_label.config(image=self.preview_image, text="")
    
    def extract_to_capture(self):
        """Extract text from image and send to Live Capture"""
        if not self.current_image:
            self.ocr_status.config(text="❌ No image", foreground="red")
            return
        
        if not REQUESTS_AVAILABLE:
            messagebox.showerror("Missing requests", "Please install: pip install requests")
            return
        
        if not self.llm_api_key:
            messagebox.showwarning("No API Key", 
                                 "Please set an environment variable:\n" +
                                 "ANTHROPIC_API_KEY, OPENAI_API_KEY, or GOOGLE_API_KEY")
            return
        
        self.ocr_status.config(text="⏳ Extracting...", foreground="blue")
        
        # Run extraction in background
        threading.Thread(
            target=self.extract_text_thread,
            daemon=True
        ).start()
    
    def extract_text_thread(self):
        """Extract text using LLM in background thread"""
        try:
            # Convert image to base64
            buffer = io.BytesIO()
            self.current_image.save(buffer, format='PNG')
            img_b64 = base64.b64encode(buffer.getvalue()).decode()
            
            # Call appropriate LLM
            if self.llm_provider == "claude":
                text = self.claude_vision(img_b64)
            elif self.llm_provider == "openai":
                text = self.openai_vision(img_b64)
            elif self.llm_provider == "gemini":
                text = self.gemini_vision(img_b64)
            else:
                text = "No LLM provider configured"
            
            # Update UI
            self.root.after(0, lambda: self.update_live_capture(text))
            self.root.after(0, lambda: self.ocr_status.config(
                text="✓ Text extracted", foreground="green"))
            
        except Exception as e:
            self.root.after(0, lambda: self.ocr_status.config(
                text=f"❌ {str(e)}", foreground="red"))
    
    def claude_vision(self, img_b64):
        """Claude vision API call"""
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": self.llm_api_key,
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01"
            },
            json={
                "model": "claude-3-5-sonnet-20241022",
                "max_tokens": 1000,
                "messages": [{
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": img_b64
                            }
                        },
                        {
                            "type": "text",
                            "text": "Extract all text from this image. Return only the text content."
                        }
                    ]
                }]
            }
        )
        
        if response.status_code == 200:
            return response.json()['content'][0]['text']
        else:
            raise Exception(f"Claude API error: {response.status_code}")
    
    def openai_vision(self, img_b64):
        """OpenAI vision API call"""
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {self.llm_api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "gpt-4-vision-preview",
                "messages": [{
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Extract all text from this image. Return only the text content."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{img_b64}"
                            }
                        }
                    ]
                }],
                "max_tokens": 1000
            }
        )
        
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            raise Exception(f"OpenAI API error: {response.status_code}")
    
    def gemini_vision(self, img_b64):
        """Gemini vision API call"""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro-vision:generateContent?key={self.llm_api_key}"
        
        response = requests.post(url, json={
            "contents": [{
                "parts": [
                    {
                        "text": "Extract all text from this image. Return only the text content."
                    },
                    {
                        "inline_data": {
                            "mime_type": "image/png",
                            "data": img_b64
                        }
                    }
                ]
            }],
            "generationConfig": {
                "maxOutputTokens": 1000
            }
        })
        
        if response.status_code == 200:
            result = response.json()
            return result['candidates'][0]['content']['parts'][0]['text']
        else:
            raise Exception(f"Gemini API error: {response.status_code}")
    
    def process_by_llm(self):
        """Process text in Live Capture using LLM"""
        text = self.capture_text.get(1.0, tk.END).strip()
        if not text:
            return
        
        if not self.llm_api_key:
            messagebox.showwarning("No API Key", 
                                 "Please set an environment variable:\n" +
                                 "ANTHROPIC_API_KEY, OPENAI_API_KEY, or GOOGLE_API_KEY")
            return
        
        # Show processing
        original_text = text
        self.capture_text.delete(1.0, tk.END)
        self.capture_text.insert(1.0, "🤖 Processing with LLM...")
        
        # Process in background
        threading.Thread(
            target=self.process_text_thread,
            args=(original_text,),
            daemon=True
        ).start()
    
    def process_text_thread(self, text):
        """Process text with LLM in background"""
        try:
            prompt = self.llm_prompt.replace("{text}", text)
            
            if self.llm_provider == "claude":
                response = self.claude_text(prompt)
            elif self.llm_provider == "openai":
                response = self.openai_text(prompt)
            elif self.llm_provider == "gemini":
                response = self.gemini_text(prompt)
            else:
                response = "No LLM provider configured"
            
            # Format result
            result = f"ORIGINAL:\n{text}\n\n{'='*50}\nPROCESSED:\n{response}"
            
            self.root.after(0, lambda: self.capture_text.delete(1.0, tk.END))
            self.root.after(0, lambda: self.capture_text.insert(1.0, result))
            
        except Exception as e:
            self.root.after(0, lambda: self.capture_text.delete(1.0, tk.END))
            self.root.after(0, lambda: self.capture_text.insert(1.0, f"❌ Processing failed: {e}"))
    
    def claude_text(self, prompt):
        """Claude text API call"""
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": self.llm_api_key,
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01"
            },
            json={
                "model": "claude-3-5-sonnet-20241022",
                "max_tokens": 1000,
                "messages": [{
                    "role": "user",
                    "content": prompt
                }]
            }
        )
        
        if response.status_code == 200:
            return response.json()['content'][0]['text']
        else:
            raise Exception(f"Claude API error: {response.status_code}")
    
    def openai_text(self, prompt):
        """OpenAI text API call"""
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {self.llm_api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "gpt-3.5-turbo",
                "messages": [{
                    "role": "user",
                    "content": prompt
                }],
                "max_tokens": 1000
            }
        )
        
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            raise Exception(f"OpenAI API error: {response.status_code}")
    
    def gemini_text(self, prompt):
        """Gemini text API call"""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={self.llm_api_key}"
        
        response = requests.post(url, json={
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }],
            "generationConfig": {
                "maxOutputTokens": 1000
            }
        })
        
        if response.status_code == 200:
            result = response.json()
            return result['candidates'][0]['content']['parts'][0]['text']
        else:
            raise Exception(f"Gemini API error: {response.status_code}")
    
    def edit_prompt(self):
        """Edit LLM prompt"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit LLM Prompt")
        dialog.geometry("600x400")
        dialog.attributes('-topmost', True)
        
        ttk.Label(dialog, text="LLM Prompt (use {text} as placeholder):").pack(pady=5)
        
        prompt_text = scrolledtext.ScrolledText(dialog, wrap='word')
        prompt_text.pack(fill='both', expand=True, padx=10, pady=5)
        prompt_text.insert(1.0, self.llm_prompt)
        
        # Buttons
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(fill='x', padx=10, pady=5)
        
        def save_prompt():
            self.llm_prompt = prompt_text.get(1.0, tk.END).strip()
            self.save_settings()
            dialog.destroy()
        
        ttk.Button(btn_frame, text="Save", command=save_prompt).pack(side='right', padx=2)
        ttk.Button(btn_frame, text="Cancel", command=dialog.destroy).pack(side='right', padx=2)
        
        # Presets
        preset_frame = ttk.Frame(dialog)
        preset_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(preset_frame, text="Presets:").pack(side='left')
        
        presets = {
            "Explain": "Explain this clearly:\n{text}",
            "Code": "Analyze this code:\n- What it does\n- How it works\n- Issues/improvements\n\n{text}",
            "Translate": "Translate to Chinese:\n{text}",
            "Summarize": "Summarize key points:\n{text}",
            "Fix": "Fix any errors:\n{text}"
        }
        
        for name, preset in presets.items():
            ttk.Button(preset_frame, text=name,
                      command=lambda p=preset: (
                          prompt_text.delete(1.0, tk.END),
                          prompt_text.insert(1.0, p)
                      )).pack(side='left', padx=2)
    
    def store_current(self):
        """Store current text to persistent storage"""
        text = self.capture_text.get(1.0, tk.END).strip()
        if not text:
            return
        
        # Create item
        item_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        timestamp = datetime.now().isoformat()
        
        item = {
            'id': item_id,
            'timestamp': timestamp,
            'text': text[:100],  # Preview
            'type': self.detect_type(text),
            'length': len(text),
            'source': 'manual'
        }
        
        # Save full text
        item_file = self.items_dir / f"{item_id}.txt"
        item_file.write_text(text, encoding='utf-8')
        
        # Update index
        self.stored_items.insert(0, item)
        self.update_index()
        self.refresh_stored_list()
        
        print(f"✓ Stored item: {item_id}")
    
    def detect_type(self, text):
        """Detect if text is a command or regular text"""
        # Simple heuristics
        cmd_patterns = ['git ', 'npm ', 'docker ', 'cd ', 'ls ', 'sudo ', 'python ', 'pip ']
        shell_chars = ['|', '&&', '>', '<', ';']
        
        text_lower = text.lower().strip()
        
        # Check for command patterns
        if any(text_lower.startswith(p) for p in cmd_patterns):
            return 'cmd'
        
        # Check for shell characters
        if any(c in text for c in shell_chars):
            return 'cmd'
        
        return 'text'
    
    def refresh_stored_list(self):
        """Refresh the stored items list"""
        self.stored_listbox.delete(0, tk.END)
        
        items_to_show = self.stored_items
        if hasattr(self, 'search_results'):
            items_to_show = self.search_results
        
        for item in items_to_show:
            # Format display
            try:
                dt = datetime.fromisoformat(item['timestamp'])
                time_str = dt.strftime("%H:%M")
            except:
                time_str = "??:??"
            
            type_icon = "📋" if item['type'] == 'cmd' else "📝"
            preview = item['text'][:50]
            if len(item['text']) > 50:
                preview += "..."
            
            display = f"[{time_str}] {type_icon} {preview}"
            self.stored_listbox.insert(tk.END, display)
        
        # Update storage info
        total_items = len(self.stored_items)
        total_size = sum(len(self.get_item_text(item['id'])) for item in self.stored_items[:10])  # Sample
        self.storage_info.config(text=f"Storage: {total_items} items (~{total_size//1024}KB)")
    
    def on_search_change(self, *args):
        """Handle search input changes"""
        query = self.search_var.get().lower().strip()
        
        if query:
            # Search through items
            self.search_results = []
            for item in self.stored_items:
                # Search preview text
                if query in item['text'].lower():
                    self.search_results.append(item)
                    continue
                
                # Search full text (limited to avoid slowdown)
                if len(self.search_results) < 100:  # Limit results
                    full_text = self.get_item_text(item['id'])
                    if full_text and query in full_text.lower():
                        self.search_results.append(item)
        else:
            # Clear search
            if hasattr(self, 'search_results'):
                delattr(self, 'search_results')
        
        self.refresh_stored_list()
    
    def copy_selected(self):
        """Copy selected item to clipboard"""
        selection = self.stored_listbox.curselection()
        if not selection:
            return
        
        # Get item
        items_to_use = getattr(self, 'search_results', self.stored_items)
        item = items_to_use[selection[0]]
        full_text = self.get_item_text(item['id'])
        
        # Copy to clipboard
        if PYPERCLIP_AVAILABLE:
            pyperclip.copy(full_text)
        
        # Show in capture area
        self.update_live_capture(full_text)
    
    def delete_selected(self):
        """Delete selected item"""
        selection = self.stored_listbox.curselection()
        if not selection:
            return
        
        items_to_use = getattr(self, 'search_results', self.stored_items)
        item = items_to_use[selection[0]]
        
        if messagebox.askyesno("Confirm Delete", f"Delete item from {item['timestamp'][:10]}?"):
            # Delete file
            item_file = self.items_dir / f"{item['id']}.txt"
            if item_file.exists():
                item_file.unlink()
            
            # Remove from list
            if item in self.stored_items:
                self.stored_items.remove(item)
            
            self.update_index()
            self.refresh_stored_list()
    
    def export_items(self):
        """Export all items to file"""
        if not self.stored_items:
            messagebox.showinfo("Nothing to Export", "No items stored yet.")
            return
        
        export_file = self.storage_dir / f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        try:
            with open(export_file, 'w', encoding='utf-8') as f:
                f.write(f"Clipboard Manager Export\n")
                f.write(f"Generated: {datetime.now()}\n")
                f.write(f"Total Items: {len(self.stored_items)}\n")
                f.write("=" * 80 + "\n\n")
                
                for i, item in enumerate(self.stored_items, 1):
                    f.write(f"Item {i}:\n")
                    f.write(f"  Timestamp: {item['timestamp']}\n")
                    f.write(f"  Type: {item['type']}\n")
                    f.write(f"  Length: {item['length']} chars\n")
                    f.write(f"  Content:\n")
                    f.write("-" * 40 + "\n")
                    f.write(self.get_item_text(item['id']))
                    f.write("\n" + "=" * 80 + "\n\n")
            
            messagebox.showinfo("Export Complete", f"Exported to:\n{export_file}")
            
        except Exception as e:
            messagebox.showerror("Export Failed", f"Error: {e}")
    
    def get_item_text(self, item_id):
        """Load full text for an item"""
        item_file = self.items_dir / f"{item_id}.txt"
        if item_file.exists():
            try:
                return item_file.read_text(encoding='utf-8')
            except:
                return "[Error reading file]"
        return "[File not found]"
    
    def update_index(self):
        """Update the index file"""
        try:
            # Keep only recent items in memory
            self.stored_items = self.stored_items[:1000]
            
            with open(self.index_file, 'w', encoding='utf-8') as f:
                json.dump(self.stored_items, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error updating index: {e}")
    
    def load_items(self):
        """Load items from storage"""
        if self.index_file.exists():
            try:
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    self.stored_items = json.load(f)
                print(f"Loaded {len(self.stored_items)} items")
            except Exception as e:
                print(f"Error loading items: {e}")
                self.stored_items = []
        else:
            self.stored_items = []
    
    def load_settings(self):
        """Load settings"""
        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    self.llm_prompt = settings.get('llm_prompt', self.llm_prompt)
                    self.ocr_expanded = settings.get('ocr_expanded', False)
            except Exception as e:
                print(f"Error loading settings: {e}")
    
    def save_settings(self):
        """Save settings"""
        try:
            settings = {
                'llm_prompt': self.llm_prompt,
                'ocr_expanded': self.ocr_expanded,
                'window_geometry': self.root.geometry(),
                'last_saved': datetime.now().isoformat()
            }
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def on_closing(self):
        """Handle window closing"""
        try:
            # Stop monitoring
            if self.clipboard_monitoring and KEYBOARD_AVAILABLE:
                keyboard.remove_all_hotkeys()
            
            # Save settings
            self.save_settings()
            
        except Exception as e:
            print(f"Error during shutdown: {e}")
        
        self.root.destroy()
    
    def run(self):
        """Start the application"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Show startup info
        if self.llm_provider:
            provider_info = f"Using {self.llm_provider.upper()} API"
        else:
            provider_info = "No LLM API key found"
        
        print(f"Clipboard & OCR Manager started")
        print(f"Storage: {self.storage_dir}")
        print(f"Items loaded: {len(self.stored_items)}")
        print(f"LLM: {provider_info}")
        
        self.root.mainloop()

    def apply_screen_capture_protection(self):
        """Apply Windows-specific protection against screen capture"""
        try:
            # Ensure window is rendered before getting handle (IMPORTANT!)
            self.root.update()
            
            # Get the window handle using the improved method from example
            tkinter_id = self.root.winfo_id()
            window_handle = ctypes.windll.user32.GetParent(tkinter_id)
            print(f"Tkinter ID: {tkinter_id}")
            print(f"Window handle (HWND): {window_handle}")
            print(f"Window title: {self.root.title()}")
            
            # Define constants
            WDA_EXCLUDEFROMCAPTURE = 0x00000011
            print(f"WDA_EXCLUDEFROMCAPTURE constant: {WDA_EXCLUDEFROMCAPTURE}")
            
            # Apply the screen capture protection with proper type conversion
            success = ctypes.windll.user32.SetWindowDisplayAffinity(
                wintypes.HWND(window_handle),
                wintypes.DWORD(WDA_EXCLUDEFROMCAPTURE)
            )
            
            if success:
                print("✓ Screen capture protection applied successfully")
            else:
                # Enhanced error reporting from example
                error_code = ctypes.windll.kernel32.GetLastError()
                print(f"⚠ Warning: Could not apply screen capture protection")
                print(f"Windows Error Code: {error_code}")
                
        except Exception as e:
            print(f"Error applying screen capture protection: {e}")


if __name__ == "__main__":
    print("Starting Clipboard & OCR Manager...")
    
    # Check critical dependencies
    missing_deps = []
    if not KEYBOARD_AVAILABLE:
        missing_deps.append("keyboard")
    if not PYPERCLIP_AVAILABLE:
        missing_deps.append("pyperclip")
    if not PIL_AVAILABLE:
        missing_deps.append("Pillow")
    if not REQUESTS_AVAILABLE:
        missing_deps.append("requests")
    
    if missing_deps:
        print(f"\nWarning: Missing dependencies: {', '.join(missing_deps)}")
        print(f"Install with: pip install {' '.join(missing_deps)}")
        print("Some features may not work properly.\n")
    
    app = ClipboardOCRManager()
    app.run()