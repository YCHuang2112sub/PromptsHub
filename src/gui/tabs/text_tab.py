import customtkinter as ctk
from utils.diagnostic_helper import debug_log
from datetime import datetime

class TextTab(ctk.CTkFrame):
    def __init__(self, parent, app_instance):
        super().__init__(parent)
        self.app = app_instance
        self.db = app_instance.db
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # 🟢 Control Header
        header = ctk.CTkFrame(self)
        header.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        ctk.CTkLabel(header, text="✍️ Text Studio", font=("Segoe UI", 16, "bold"), text_color="#ae78ff").pack(side="left", padx=15, pady=10)
        
        ctk.CTkButton(header, text="✨ Enchant", width=120, command=self.process_text).pack(side="left", padx=5)
        ctk.CTkButton(header, text="💾 Save to Lib", width=120, command=self.save_to_library).pack(side="left", padx=5)
        ctk.CTkButton(header, text="🗑 Clear All", width=100, fg_color="transparent", border_width=1, command=self.clear_all).pack(side="left", padx=5)
        
        # 📜 Triple Column Content
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.content.grid_columnconfigure(0, weight=1) # Raw Input
        self.content.grid_columnconfigure(1, weight=1) # Applied Prompt
        self.content.grid_columnconfigure(2, weight=1) # Output
        self.content.grid_rowconfigure(1, weight=1)
        
        # column 0: Raw Input
        ctk.CTkLabel(self.content, text="RAW INPUT", font=("Segoe UI", 10, "bold"), text_color="gray").grid(row=0, column=0, sticky="w", padx=5)
        self.raw_input = ctk.CTkTextbox(self.content, font=("Segoe UI", 12), border_width=1, border_color="#333")
        self.raw_input.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        # column 1: Applied Prompt
        ctk.CTkLabel(self.content, text="APPLIED PROMPT", font=("Segoe UI", 10, "bold"), text_color="gray").grid(row=0, column=1, sticky="w", padx=5)
        self.applied_prompt = ctk.CTkTextbox(self.content, font=("Segoe UI", 11), border_width=1, border_color="#333", fg_color="#1a1a1a")
        self.applied_prompt.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)
        
        # column 2: Output
        ctk.CTkLabel(self.content, text="LLM OUTPUT", font=("Segoe UI", 10, "bold"), text_color="gray").grid(row=0, column=2, sticky="w", padx=5)
        self.output_text = ctk.CTkTextbox(self.content, font=("Segoe UI", 12), border_width=1, border_color="#333")
        self.output_text.grid(row=1, column=2, sticky="nsew", padx=5, pady=5)
        
        self.raw_input.insert("1.0", "Enter your text or idea here...")
        self.applied_prompt.insert("1.0", "--- Template application will show here ---")
        self.output_text.insert("1.0", "--- Final AI results will appear here ---")

    def process_text(self):
        text = self.raw_input.get("1.0", "end-1c").strip()
        if not text: return
        
        # Populate Applied Prompt with the template logic
        full_prompt = self.app.llm_prompt.replace("{text}", text)
        self.applied_prompt.delete("1.0", "end")
        self.applied_prompt.insert("1.0", full_prompt)
        
        # Start processing
        self.app.start_llm_processing(text, target_pane="text_studio")

    def update_output(self, response):
        self.output_text.delete("1.0", "end")
        self.output_text.insert("1.0", response)

    def clear_all(self):
        self.raw_input.delete("1.0", "end")
        self.applied_prompt.delete("1.0", "end")
        self.output_text.delete("1.0", "end")

    def save_to_library(self):
        # We can reuse the dialog logic or just save raw input as a prompt
        from gui.tabs.live_capture import SaveToLibraryDialog
        prompt_text = self.raw_input.get("1.0", "end-1c").strip()
        output_text = self.output_text.get("1.0", "end-1c").strip()
        
        if not prompt_text and not output_text: return
        
        has_insight = bool(output_text and "---" not in output_text)
        dialog = SaveToLibraryDialog(self, self.db.get_categories(), has_insight=has_insight)
        self.wait_window(dialog)
        
        if dialog.result:
            name, category, source = dialog.result
            content = prompt_text if source == "prompt" else output_text
            self.db.add_prompt(name, content, category)
            self.app.status_var.set(f"✅ Saved to Library: {name}")

    def update_live_text(self, text, pane="input"):
        if pane == "live" or pane == "input":
            self.raw_input.delete("1.0", "end")
            self.raw_input.insert("1.0", text)
        elif pane == "text_studio":
            self.update_output(text)
