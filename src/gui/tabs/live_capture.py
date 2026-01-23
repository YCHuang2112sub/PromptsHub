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
from utils.diagnostic_helper import debug_log

class VisionStudioTab(ctk.CTkFrame):
    def __init__(self, parent, app_instance):
        super().__init__(parent)
        debug_log("Initializing VisionStudioTab...")
        self.app = app_instance
        self.db = app_instance.db
        
        # Grid configuration
        # Row 0: Screen OCR controls (Manual)
        # Row 1: Workspace and History (Draggable)
        self.grid_columnconfigure(0, weight=1) 
        self.grid_rowconfigure(1, weight=1)
        
        # Top Toolbar (Manual Actions)
        self.create_ocr_section()
        
        # Main content area (Horizontal: Workspace + Dragger + History)
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.content_frame.grid_rowconfigure(0, weight=1)
        
        # Initial weight for workspace vs history
        self.left_col_weight = 4
        self.right_col_weight = 1
        self.content_frame.grid_columnconfigure(0, weight=self.left_col_weight) # Workspace
        self.content_frame.grid_columnconfigure(1, weight=0) # Dragger separator
        self.content_frame.grid_columnconfigure(2, weight=self.right_col_weight) # History
        
        self.create_left_panel()
        self.create_dragger()
        self.create_right_panel()
        
        # Initial load
        self.load_items_to_ui()

    def create_ocr_section(self):
        # Tools Panel (Top)
        self.ocr_frame = ctk.CTkFrame(self)
        self.ocr_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 10))
        
        # Title
        ctk.CTkLabel(self.ocr_frame, text="📸 Vision Studio Tools", font=("Segoe UI", 12, "bold")).pack(side="left", padx=10, pady=5)
        
        # Manual Capture Controls
        ctk.CTkButton(self.ocr_frame, text="Crop Screen", width=100, command=self.crop_screen).pack(side="left", padx=5, pady=5)
        ctk.CTkButton(self.ocr_frame, text="Extract Text", width=100, command=self.extract_text_from_image).pack(side="left", padx=5, pady=5)
        
        # Upload/Full Screen
        ctk.CTkButton(self.ocr_frame, text="📂 Upload Image", width=110, command=self.upload_image).pack(side="left", padx=5, pady=5)
        ctk.CTkButton(self.ocr_frame, text="🖥️ Full Screenshot", width=120, command=self.full_screenshot).pack(side="left", padx=5, pady=5)
        
        # Status
        self.ocr_status = ctk.CTkLabel(self.ocr_frame, text="Ready", text_color="gray")
        self.ocr_status.pack(side="right", padx=10)


    def create_left_panel(self):
        # Left Panel Container (Workspace)
        self.left_panel = ctk.CTkFrame(self.content_frame)
        self.left_panel.grid(row=0, column=0, sticky="nsew")
        self.left_panel.grid_rowconfigure(1, weight=1)
        self.left_panel.grid_columnconfigure(0, weight=1)
        
        # Header - Vision Studio Title
        header = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        
        ctk.CTkLabel(header, text="✨ Vision Studio Workspace", font=("Segoe UI", 14, "bold"), text_color="#ae78ff").pack(side="left")
        
        # Vision Mode Toggle
        self.vision_mode_var = ctk.BooleanVar(value=False)
        ctk.CTkSwitch(header, text="Vision Chat", variable=self.vision_mode_var, command=self.toggle_vision_mode).pack(side="left", padx=20)
        
        # Monitoring Status
        self.monitor_label = ctk.CTkLabel(header, text="● Monitoring Ctrl+C", text_color="#4ec9b0")
        self.monitor_label.pack(side="right")
        
        # Text Area / Vision Workspace (3 columns)
        # 3-Pane flow: [INPUT (Image)] -> [PROMPT (Studio)] -> [OUTPUT (Insight)]
        self.workspace_container = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        self.workspace_container.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.workspace_container.grid_columnconfigure(0, weight=1) # Input
        self.workspace_container.grid_columnconfigure(1, weight=1) # Prompt
        self.workspace_container.grid_columnconfigure(2, weight=1) # Output
        self.workspace_container.grid_rowconfigure(1, weight=1) # Content boxes

        # Labels for the flow
        ctk.CTkLabel(self.workspace_container, text="📸 INPUT", font=("Segoe UI", 10, "bold"), text_color="gray").grid(row=0, column=0, sticky="w", padx=5)
        ctk.CTkLabel(self.workspace_container, text="🖋️ PROMPT STUDIO", font=("Segoe UI", 10, "bold"), text_color="gray").grid(row=0, column=1, sticky="w", padx=5)
        ctk.CTkLabel(self.workspace_container, text="🧠 AI INSIGHT", font=("Segoe UI", 10, "bold"), text_color="gray").grid(row=0, column=2, sticky="w", padx=5)

        # Pane 1: Image Preview Workspace (INPUT)
        self.image_workspace = ctk.CTkFrame(self.workspace_container, fg_color="#1e1e1e", border_width=1, border_color="#333")
        self.image_workspace.grid(row=1, column=0, sticky="nsew", padx=(0, 5))
        
        self.image_label = ctk.CTkLabel(self.image_workspace, text="Drop Image Here", text_color="#555")
        self.image_label.pack(expand=True, fill="both", padx=5, pady=5)

        # Pane 2: Prompt / Original Text (PROMPT STUDIO)
        self.live_text = ctk.CTkTextbox(self.workspace_container, font=("Consolas", 12), border_width=1, border_color="#333")
        self.live_text.grid(row=1, column=1, sticky="nsew", padx=5)
        
        # Pane 3: Result Window (AI INSIGHT)
        self.after_text = ctk.CTkTextbox(self.workspace_container, font=("Consolas", 12), border_width=1, border_color="#333")
        self.after_text.grid(row=1, column=2, sticky="nsew", padx=(5, 0))
        self.after_text.insert("1.0", "--- Result Window ---")
        
        # Action Buttons
        actions_frame = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        actions_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))
        
        ctk.CTkButton(actions_frame, text="💾 Store to History", width=120, command=self.store_current).pack(side="left", padx=(0, 5))
        ctk.CTkButton(actions_frame, text="📚 Save Prompt To Lib.", width=140, command=self.save_to_library_dialog).pack(side="left", padx=(0, 5))
        ctk.CTkButton(actions_frame, text="✨ Extract Prompt", width=120, fg_color="#ae78ff", hover_color="#9357e6", command=self.extract_prompt_ai).pack(side="left", padx=(0, 5))
        ctk.CTkButton(actions_frame, text="🤖 Enchant", width=80, command=self.process_with_llm).pack(side="left", padx=(0, 5))
        ctk.CTkButton(actions_frame, text="🔄 Clear", width=80, command=self.clear_live).pack(side="left", padx=(0, 5))

    def create_dragger(self):
        # Vertical Dragger (A thin bar to resize history)
        self.dragger = ctk.CTkFrame(self.content_frame, width=4, cursor="sb_h_double_arrow", fg_color="#333")
        self.dragger.grid(row=0, column=1, sticky="ns", padx=2)
        
        self.dragger.bind("<ButtonPress-1>", self.on_dragger_press)
        self.dragger.bind("<B1-Motion>", self.on_dragger_move)

    def on_dragger_press(self, event):
        self.drag_start_x = event.x_root

    def on_dragger_move(self, event):
        delta_x = event.x_root - self.drag_start_x
        self.drag_start_x = event.x_root
        
        # Adjust weights or absolute width?
        # Grid weights are easier. We'll adjust the right_col_weight
        # Sensitivity factor
        sensitivity = 0.01 
        self.right_col_weight = max(0.5, min(3.0, self.right_col_weight - delta_x * sensitivity))
        self.content_frame.grid_columnconfigure(2, weight=self.right_col_weight)
        self.content_frame.grid_columnconfigure(0, weight=4) # Keep left weight stable

    def create_right_panel(self):
        # Right Panel Container (History)
        self.right_panel = ctk.CTkFrame(self.content_frame)
        self.right_panel.grid(row=0, column=2, sticky="nsew")
        self.right_panel.grid_rowconfigure(2, weight=1)
        self.right_panel.grid_columnconfigure(0, weight=1)
        
        # Header
        ctk.CTkLabel(self.right_panel, text="📚 History", font=("Segoe UI", 12, "bold"), text_color="gray").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        
        # Search
        self.search_entry = ctk.CTkEntry(self.right_panel, placeholder_text="🔍 Search history...")
        self.search_entry.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 5))
        self.search_entry.bind('<KeyRelease>', self.on_search)
        
        # Scrollable Frame for Items
        self.history_scroll = ctk.CTkScrollableFrame(self.right_panel)
        self.history_scroll.grid(row=2, column=0, sticky="nsew", padx=10, pady=(0, 10))
        
        # Actions
        actions_frame = ctk.CTkFrame(self.right_panel, fg_color="transparent")
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
        debug_log(f"History item selected: {item['id']}")
        
        # Update the live prompt pane with the exact text saved
        self.live_text.delete("1.0", "end")
        self.live_text.insert("1.0", item['text'])
        
        # Reset visual selection for all buttons
        for btn in self.current_history_widgets:
            btn.configure(fg_color="transparent", border_color="#3e3e42")
            
        # Highlight selected button (we need to find the widget linked to this item)
        for btn, widget_item in self.current_history_widgets.items():
            if widget_item['id'] == item['id']:
                btn.configure(fg_color="#3e3e42", border_color="#4ec9b0")
                break

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
            # We target the AI Insight pane (after)
            self.app.start_llm_processing(text, is_chat=False, target_pane="after")

    def crop_screen(self):
        # Delegate to main app for screen capture logic (requires Toplevel)
        self.app.initiate_screen_capture(self)

    def extract_text_from_image(self):
        # Delegate to main app
        self.app.extract_text_from_current_image(self)

    def extract_prompt_ai(self):
        """Asks the AI to reverse-engineer a prompt from the current text"""
        text = self.live_text.get("1.0", "end-1c").strip()
        if not text:
            return
            
        meta_prompt = (
            "You are a Prompt Engineering expert. Analyze the following text and generate a reusable prompt template "
            "that would result in this output. Use '[\"Input\"]' as a placeholder for where the user would provide the original data.\n"
            "Respond ONLY with the generated prompt, nothing else.\n\n"
            f"TEXT TO ANALYZE:\n{text}"
        )
        
        self.app.status_var.set("✨ Reverse-engineering prompt...")
        # We'll use a special flag or just handle it in update_live_text
        self.app.start_llm_processing(meta_prompt, is_chat=False, target_pane="after")

    def update_live_text(self, text, pane="live"):
        if pane == "live":
            self.live_text.delete("1.0", "end")
            self.live_text.insert("1.0", text)
        else:
            self.after_text.delete("1.0", "end")
            self.after_text.insert("1.0", text)
        
    def set_captured_image(self, img):
        """Updates the UI with the captured image thumbnail"""
        debug_log(f"Setting captured image: {img.width}x{img.height}")
        self.current_image = img
        
        # Create larger workspace preview
        w, h = img.size
        # Max dimensions for workspace preview
        max_w, max_h = 400, 300
        ratio = min(max_w/w, max_h/h)
        new_w, new_h = int(w * ratio), int(h * ratio)
        
        preview_img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        try:
             photo = ctk.CTkImage(light_image=preview_img, dark_image=preview_img, size=(new_w, new_h))
             self.image_label.configure(image=photo, text="")
             self.ocr_status.configure(text=f"Captured {w}x{h}", text_color="#4ec9b0")
             # Also update the small thumbnail if it exists (legacy UI compatibility)
             if hasattr(self, 'image_preview') and self.image_preview.winfo_exists():
                 thumb_w, thumb_h = (150, 50)
                 t_ratio = min(thumb_w/w, thumb_h/h)
                 tw, th = int(w * t_ratio), int(h * t_ratio)
                 thumb = img.resize((tw, th), Image.Resampling.LANCZOS)
                 t_photo = ctk.CTkImage(light_image=thumb, dark_image=thumb, size=(tw, th))
                 self.image_preview.configure(image=t_photo, width=tw)
        except Exception as e:
             debug_log(f"Preview update error: {e}", level="error")
             self.ocr_status.configure(text="Preview Error", text_color="orange")

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
            # Check global privacy mode from main app
            privacy_on = self.app.privacy_var.get()
            
            if not privacy_on:
                self.app.withdraw()
                self.app.update()
                
            img = ImageGrab.grab()
            
            if not privacy_on:
                self.app.deiconify()
                
            self.set_captured_image(img)
            self.app.status_var.set("✅ Full screen captured")
        except Exception as e:
            self.app.status_var.set(f"❌ Error: {e}")

    def save_to_library_dialog(self):
        prompt_text = self.live_text.get("1.0", "end-1c").strip()
        insight_text = self.after_text.get("1.0", "end-1c").strip()
        
        # We allow saving if either has content, but prompt is Usually the priority
        if not prompt_text and not insight_text:
            messagebox.showwarning("Empty", "Nothing to save!")
            return
            
        has_insight = bool(insight_text and "--- Result Window ---" not in insight_text)
        dialog = SaveToLibraryDialog(self, self.db.get_categories(), has_insight=has_insight)
        self.wait_window(dialog)
        
        if dialog.result:
            name, category, source = dialog.result
            content_to_save = prompt_text if source == "prompt" else insight_text
            
            if not content_to_save.strip():
                messagebox.showerror("Error", f"Selected source ({source}) is empty!")
                return

            try:
                self.db.add_prompt(name, content_to_save, category)
                self.app.status_var.set(f"✅ Saved to Library: {name}")
            except Exception as e:
                messagebox.showerror("Error", f"Save failed: {e}")


class SaveToLibraryDialog(ctk.CTkToplevel):
    def __init__(self, parent, categories, has_insight=False):
        super().__init__(parent)
        self.title("Save to Library")
        self.geometry("400x320")
        self.result = None
        self.after(100, self.lift) # Ensure it stays on top
        
        self.grid_columnconfigure(1, weight=1)
        
        # 1. Source Selection
        ctk.CTkLabel(self, text="Source:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.source_var = ctk.StringVar(value="prompt")
        source_frame = ctk.CTkFrame(self, fg_color="transparent")
        source_frame.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        ctk.CTkRadioButton(source_frame, text="Prompt", variable=self.source_var, value="prompt").pack(side="left", padx=5)
        self.insight_radio = ctk.CTkRadioButton(source_frame, text="AI Insight", variable=self.source_var, value="insight")
        self.insight_radio.pack(side="left", padx=5)
        if not has_insight:
            self.insight_radio.configure(state="disabled")

        # 2. Name
        ctk.CTkLabel(self, text="Name:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.name_entry = ctk.CTkEntry(self)
        self.name_entry.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        
        # 3. Category
        ctk.CTkLabel(self, text="Category:").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.category_var = ctk.StringVar(value=categories[0] if categories else "General")
        self.cat_menu = ctk.CTkOptionMenu(self, values=categories, variable=self.category_var)
        self.cat_menu.grid(row=2, column=1, padx=10, pady=10, sticky="ew")
        
        # 4. Save Button
        ctk.CTkButton(self, text="Save to Library", command=self.save, fg_color="#ae78ff", hover_color="#9357e6").grid(row=3, column=0, columnspan=2, pady=20)
        
    def save(self):
        name = self.name_entry.get().strip()
        if not name:
            return
        self.result = (name, self.category_var.get(), self.source_var.get())
        self.destroy()


