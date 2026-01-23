import customtkinter as ctk
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, simpledialog
from tkinter import messagebox
from datetime import datetime
import pyperclip
import threading
import os
from PIL import Image, ImageTk, ImageGrab

class LiveCaptureTab(ctk.CTkFrame):
    def __init__(self, parent, app_instance):
        super().__init__(parent)
        self.app = app_instance
        self.db = app_instance.db
        
        # Grid configuration
        self.grid_columnconfigure(0, weight=3) # Left panel (Capture)
        self.grid_columnconfigure(1, weight=2) # Right panel (History)
        self.grid_rowconfigure(0, weight=1)
        
        self.create_ocr_section()
        self.create_left_panel()
        self.create_right_panel()
        
        # Initial load
        self.load_items_to_ui()

    def create_ocr_section(self):
        # OCR Panel (Top)
        self.ocr_frame = ctk.CTkFrame(self)
        self.ocr_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=(10, 0))
        
        # Title
        ctk.CTkLabel(self.ocr_frame, text="📷 Screen OCR", font=("Segoe UI", 12, "bold")).pack(side="left", padx=10, pady=5)
        
        # Controls
        ctk.CTkButton(self.ocr_frame, text="Crop Screen", width=100, command=self.crop_screen).pack(side="left", padx=5, pady=5)
        ctk.CTkButton(self.ocr_frame, text="Extract Text", width=100, command=self.extract_text_from_image).pack(side="left", padx=5, pady=5)
        
        # Status
        self.ocr_status = ctk.CTkLabel(self.ocr_frame, text="Ready", text_color="gray")
        self.ocr_status.pack(side="left", padx=10)
        
        # Image Preview Label (Hidden initially)
        self.image_preview = ctk.CTkLabel(self.ocr_frame, text="", width=0)
        self.image_preview.pack(side="right", padx=10)
        
        # New Vision Controls
        vision_controls = ctk.CTkFrame(self.ocr_frame, fg_color="transparent")
        vision_controls.pack(side="left", padx=5)
        
        ctk.CTkButton(vision_controls, text="📂 Upload", width=80, command=self.upload_image).pack(side="left", padx=2)
        ctk.CTkButton(vision_controls, text="🖥️ Full Screen", width=100, command=self.full_screenshot).pack(side="left", padx=2)
        
        # Exclusion Checkbox
        self.exclude_var = ctk.BooleanVar(value=True)
        self.exclude_chk = ctk.CTkCheckBox(
            self.ocr_frame, 
            text="Hide App", 
            variable=self.exclude_var,
            width=80,
            command=self.toggle_exclusion
        )
        self.exclude_chk.pack(side="left", padx=10)


    def create_left_panel(self):
        # Left Panel Container
        left_panel = ctk.CTkFrame(self)
        left_panel.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        left_panel.grid_rowconfigure(1, weight=1)
        left_panel.grid_columnconfigure(0, weight=1)
        
        # Header
        header = ctk.CTkFrame(left_panel, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        
        ctk.CTkLabel(header, text="🎯 Live Capture Area", font=("Segoe UI", 14, "bold")).pack(side="left")
        
        # Vision Mode Toggle
        self.vision_mode_var = ctk.BooleanVar(value=False)
        ctk.CTkSwitch(header, text="Vision Chat Mode", variable=self.vision_mode_var, command=self.toggle_vision_mode).pack(side="left", padx=20)

        
        # Monitoring Status
        self.monitor_label = ctk.CTkLabel(header, text="● Monitoring Ctrl+C", text_color="#4ec9b0")
        self.monitor_label.pack(side="right")
        
        # Text Area
        self.live_text = ctk.CTkTextbox(left_panel, font=("Consolas", 12))
        self.live_text.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        
        # Action Buttons
        actions_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        actions_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))
        
        ctk.CTkButton(actions_frame, text="💾 Store", width=80, command=self.store_current).pack(side="left", padx=(0, 5))
        ctk.CTkButton(actions_frame, text="📚 Save to Lib", width=100, command=self.save_to_library_dialog).pack(side="left", padx=(0, 5))
        ctk.CTkButton(actions_frame, text="🤖 Enchant", width=80, command=self.process_with_llm).pack(side="left", padx=(0, 5))
        ctk.CTkButton(actions_frame, text="🔄 Clear", width=80, command=self.clear_live).pack(side="left", padx=(0, 5))

    def create_right_panel(self):
        # Right Panel Container
        right_panel = ctk.CTkFrame(self)
        right_panel.grid(row=1, column=1, sticky="nsew", padx=(0, 10), pady=10)
        right_panel.grid_rowconfigure(2, weight=1)
        right_panel.grid_columnconfigure(0, weight=1)
        
        # Header
        ctk.CTkLabel(right_panel, text="📚 History", font=("Segoe UI", 14, "bold")).grid(row=0, column=0, sticky="w", padx=10, pady=5)
        
        # Search
        self.search_entry = ctk.CTkEntry(right_panel, placeholder_text="🔍 Search history...")
        self.search_entry.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 5))
        self.search_entry.bind('<KeyRelease>', self.on_search)
        
        # Scrollable Frame for Items
        self.history_scroll = ctk.CTkScrollableFrame(right_panel)
        self.history_scroll.grid(row=2, column=0, sticky="nsew", padx=10, pady=(0, 10))
        
        # Actions
        actions_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        actions_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=(0, 10))
        
        ctk.CTkButton(actions_frame, text="📋 Copy", width=80, command=self.copy_selected).pack(side="left", padx=(0, 5))
        ctk.CTkButton(actions_frame, text="🗑️ Delete", width=80, fg_color="#f14c4c", hover_color="#d13a3a", command=self.delete_selected).pack(side="right")

    # --- Logic Methods -- (Adapted from original prompts_hub.py)

    def store_current(self):
        text = self.live_text.get("1.0", "end-1c").strip()
        if not text:
            return
        try:
            self.db.add_history(text)
            self.load_items_to_ui()
            # Visual feedback
            original_bg = self.live_text.cget("text_color") # Just a flash
            # complex flash omitted for brevity, logic works
        except Exception as e:
            print(f"Error storing: {e}")

    def load_items_to_ui(self, search_query=None):
        # Clear existing buttons
        for widget in self.history_scroll.winfo_children():
            widget.destroy()
            
        history = self.db.get_history(search_query=search_query)
        self.current_history_widgets = {} # Map widget to item data
        
        for item in history:
            timestamp = datetime.fromisoformat(item['timestamp'])
            time_str = timestamp.strftime("%H:%M")
            snippet = item['text'][:40].replace('\n', ' ') + "..."
            
            # Create a button for each item (clickable list)
            btn_text = f"[{time_str}] {snippet}"
            btn = ctk.CTkButton(
                self.history_scroll, 
                text=btn_text, 
                anchor="w", 
                fg_color="transparent", 
                border_width=1,
                border_color="#3e3e42",
                hover_color="#3e3e42",
                command=lambda i=item: self.select_history_item(i)
            )
            btn.pack(fill="x", pady=2)
            self.current_history_widgets[btn] = item
            
        self.selected_item = None

    def select_history_item(self, item):
        self.selected_item = item
        # Could add visual selection logic here (highlight button)

    def on_search(self, event):
        query = self.search_entry.get().strip()
        self.load_items_to_ui(query if query else None)

    def copy_selected(self):
        if self.selected_item:
            pyperclip.copy(self.selected_item['text'])
            self.app.status_var.set("✅ Copied to clipboard")

    def delete_selected(self):
        if self.selected_item:
            self.db.delete_history_item(self.selected_item['id'])
            self.load_items_to_ui()
            self.selected_item = None

    def clear_live(self):
        self.live_text.delete("1.0", "end")

    def process_with_llm(self):
        # Delegate back to main app for LLM processing
        text = self.live_text.get("1.0", "end-1c").strip()
        if text:
            self.app.start_llm_processing(text, is_chat=False)

    def crop_screen(self):
        # Delegate to main app for screen capture logic (requires Toplevel)
        self.app.initiate_screen_capture(self)

    def extract_text_from_image(self):
        # Delegate to main app
        self.app.extract_text_from_current_image(self)

    def update_live_text(self, text):
        self.live_text.delete("1.0", "end")
        self.live_text.insert("1.0", text)
        
    def set_captured_image(self, img):
        """Updates the UI with the captured image thumbnail"""
        self.current_image = img
        
        # Create thumbnail
        thumbnail = img.copy()
        thumbnail.thumbnail((150, 50)) # Small preview
        try:
             photo = ctk.CTkImage(light_image=thumbnail, dark_image=thumbnail, size=(thumbnail.width, thumbnail.height))
             self.image_preview.configure(image=photo, width=thumbnail.width)
             self.ocr_status.configure(text=f"Captured {img.width}x{img.height}", text_color="#4ec9b0")
        except Exception as e:
             self.ocr_status.configure(text="Preview Error", text_color="orange")
             print(f"Preview error: {e}")

    def toggle_vision_mode(self):
        mode = "Vision Chat" if self.vision_mode_var.get() else "Live Capture"
        self.monitor_label.configure(text=f"● {mode} Mode")
        if self.vision_mode_var.get():
            self.live_text.delete("1.0", "end")
            self.live_text.insert("1.0", "🖼️ Vision Chat Active\n\n1. Capture or Upload an Image\n2. Type your question here\n3. Click 'Enchant' (or Process) to ask.")

    def toggle_exclusion(self):
        # Delegate to main app
        self.app.set_capture_exclusion(self.exclude_var.get())

    def upload_image(self):
        path = filedialog.askopenfilename(filetypes=[("Images", "*.png;*.jpg;*.jpeg;*.bmp")])
        if path:
            try:
                img = Image.open(path)
                self.set_captured_image(img)
                self.app.status_var.set(f"📂 Loaded: {os.path.basename(path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load image: {e}")

    def full_screenshot(self):
        self.app.status_var.set("📸 Taking screenshot in 1s...")
        self.after(1000, self._perform_full_screenshot)
        
    def _perform_full_screenshot(self):
        try:
            # Hide if exclusion is on (already handled by window affinity, but good practice)
            if not self.exclude_var.get():
                self.app.withdraw()
                self.app.update()
                
            img = ImageGrab.grab()
            
            if not self.exclude_var.get():
                self.app.deiconify()
                
            self.set_captured_image(img)
            self.app.status_var.set("✅ Full screen captured")
        except Exception as e:
            self.app.status_var.set(f"❌ Error: {e}")

    def save_to_library_dialog(self):
        text = self.live_text.get("1.0", "end-1c").strip()
        if not text:
            messagebox.showwarning("Empty", "Nothing to save!")
            return
            
        dialog = SaveToLibraryDialog(self, self.db.get_categories())
        self.wait_window(dialog)
        
        if dialog.result:
            name, category = dialog.result
            try:
                self.db.add_prompt(name, text, category)
                self.app.status_var.set(f"✅ Saved to Library: {name}")
                # Refresh library tab if it's active or implementation generic
            except Exception as e:
                messagebox.showerror("Error", f"Save failed: {e}")


class SaveToLibraryDialog(ctk.CTkToplevel):
    def __init__(self, parent, categories):
        super().__init__(parent)
        self.title("Save to Library")
        self.geometry("400x250")
        self.result = None
        
        self.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(self, text="Name:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.name_entry = ctk.CTkEntry(self)
        self.name_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        ctk.CTkLabel(self, text="Category:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.category_var = ctk.StringVar(value=categories[0] if categories else "General")
        self.cat_menu = ctk.CTkOptionMenu(self, values=categories, variable=self.category_var)
        self.cat_menu.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        
        ctk.CTkButton(self, text="Save", command=self.save).grid(row=2, column=0, columnspan=2, pady=20)
        
    def save(self):
        name = self.name_entry.get().strip()
        if not name:
            return
        self.result = (name, self.category_var.get())
        self.destroy()


