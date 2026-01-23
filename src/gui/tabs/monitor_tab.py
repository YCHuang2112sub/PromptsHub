import customtkinter as ctk
from utils.diagnostic_helper import debug_log
from datetime import datetime
import tkinter as tk

class MonitorTab(ctk.CTkFrame):
    def __init__(self, parent, app_instance):
        super().__init__(parent)
        self.app = app_instance
        self.db = app_instance.db
        self.floating_window = None
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # 🟢 Control Header
        header = ctk.CTkFrame(self)
        header.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        ctk.CTkLabel(header, text="🔍 Monitor Studio", font=("Segoe UI", 16, "bold"), text_color="#4ec9b0").pack(side="left", padx=15, pady=10)
        
        ctk.CTkButton(header, text="➕ Select Region", width=120, command=self.app.initiate_screen_capture_for_monitor, fg_color="#ae78ff", hover_color="#9357e6").pack(side="left", padx=5)
        self.monitor_btn = ctk.CTkButton(header, text="Start Monitoring", width=120, command=self.toggle_monitoring)
        self.monitor_btn.pack(side="left", padx=5)
        
        self.popout_btn = ctk.CTkButton(header, text="🪟 Floating View", width=120, command=self.toggle_floating_view, fg_color="transparent", border_width=1)
        self.popout_btn.pack(side="left", padx=5)

        self.monitor_status = ctk.CTkLabel(header, text="Inactive", text_color="gray")
        self.monitor_status.pack(side="left", padx=15)
        
        # Language Selection for Translation
        self.langs = {
            "Original": None,
            "English": "en-US",
            "Chinese (Simplified)": "zh-CN",
            "Chinese (Traditional)": "zh-TW",
            "Japanese": "ja-JP",
            "Korean": "ko-KR",
            "French": "fr-FR",
            "German": "de-DE",
            "Spanish": "es-ES"
        }
        self.lang_var = ctk.StringVar(value="Original")
        ctk.CTkLabel(header, text="Target:", font=("Segoe UI", 10)).pack(side="left", padx=(15, 5))
        self.lang_menu = ctk.CTkOptionMenu(header, values=list(self.langs.keys()), variable=self.lang_var, width=130)
        self.lang_menu.pack(side="left", padx=5)
        
        # 📜 Triple Column Content
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.content.grid_columnconfigure(0, weight=1) # Log
        self.content.grid_columnconfigure(1, weight=1) # Extracted Text
        self.content.grid_columnconfigure(2, weight=1) # AI Insights
        self.content.grid_rowconfigure(1, weight=1)
        
        # column 0: Logs
        ctk.CTkLabel(self.content, text="ACTIVITY LOG", font=("Segoe UI", 10, "bold"), text_color="gray").grid(row=0, column=0, sticky="w", padx=5)
        self.log_text = ctk.CTkTextbox(self.content, font=("Consolas", 11), border_width=1, border_color="#333")
        self.log_text.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        # column 1: Live Preview (Visuals)
        ctk.CTkLabel(self.content, text="LIVE PREVIEW", font=("Segoe UI", 10, "bold"), text_color="gray").grid(row=0, column=1, sticky="w", padx=5)
        self.image_preview = ctk.CTkLabel(self.content, text="No Region Selected", fg_color="#1a1a1a")
        self.image_preview.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)

        # column 2: Intelligence (Extracted Text + Insights)
        right_panel = ctk.CTkFrame(self.content, fg_color="transparent")
        right_panel.grid(row=0, column=2, rowspan=2, sticky="nsew", padx=5)
        right_panel.grid_columnconfigure(0, weight=1)
        right_panel.grid_rowconfigure(1, weight=1) # OCR
        right_panel.grid_rowconfigure(3, weight=1) # Insight
        
        ctk.CTkLabel(right_panel, text="EXTRACTED TEXT", font=("Segoe UI", 10, "bold"), text_color="gray").grid(row=0, column=0, sticky="w", padx=5)
        self.extracted_text_pane = ctk.CTkTextbox(right_panel, font=("Segoe UI", 12), border_width=1, border_color="#333", height=150)
        self.extracted_text_pane.grid(row=1, column=0, sticky="nsew", padx=5, pady=(5, 10))
        
        ctk.CTkLabel(right_panel, text="LLM INSIGHTS", font=("Segoe UI", 10, "bold"), text_color="gray").grid(row=2, column=0, sticky="w", padx=5)
        self.insight_text = ctk.CTkTextbox(right_panel, font=("Segoe UI", 12), border_width=1, border_color="#333")
        self.insight_text.grid(row=3, column=0, sticky="nsew", padx=5, pady=5)
        
        self.log_text.insert("1.0", "--- Monitor Ready ---\n1. Select Region\n2. Start Monitoring\n")
        self.extracted_text_pane.insert("1.0", "--- Extracted text will appear here ---")
        self.insight_text.insert("1.0", "--- AI Analysis will appear here ---")
        
    def toggle_monitoring(self):
        if hasattr(self.app, 'region_monitor') and self.app.region_monitor:
            self.app.stop_region_monitoring()
            self.monitor_btn.configure(text="Start Monitoring", fg_color=["#3B8ED0", "#1F6AA5"])
            self.monitor_status.configure(text="Inactive", text_color="gray")
            self.add_log("🛑 Monitoring stopped.")
        else:
            self.app.start_region_monitoring()
            if hasattr(self.app, 'region_monitor') and self.app.region_monitor:
                self.monitor_btn.configure(text="Stop Monitoring", fg_color="#f14c4c")
                self.monitor_status.configure(text="● LIVE", text_color="#f14c4c")
                self.add_log("▶️ Monitoring started.")

    def toggle_floating_view(self):
        if self.floating_window and self.floating_window.winfo_exists():
            self.floating_window.destroy()
            self.floating_window = None
            self.popout_btn.configure(text="🪟 Floating View", fg_color="transparent")
        else:
            self.floating_window = FloatingMonitorView(self)
            self.popout_btn.configure(text="❌ Close Floating", fg_color="#f14c4c")

    def add_log(self, message):
        self.log_text.insert("end", f"\n[{datetime.now().strftime('%H:%M:%S')}] {message}")
        self.log_text.see("end")

    def update_insight(self, insight):
        # If the result contains both (Original and Translation), we might want to split it.
        # But for now, we'll just show the LLM result in Insight.
        self.insight_text.delete("1.0", "end")
        self.insight_text.insert("1.0", f"[{datetime.now().strftime('%H:%M:%S')}]\n{insight}")
        if self.floating_window:
            self.floating_window.update_insight(insight)

    def update_extracted_text(self, text):
        self.extracted_text_pane.delete("1.0", "end")
        self.extracted_text_pane.insert("1.0", text)
        if self.floating_window:
            self.floating_window.update_text(text)

    def set_captured_image(self, img):
        self.current_image = img
        self.add_log(f"📸 Snapshot: {img.width}x{img.height}")
        try:
            # Dynamically size the image to fit the center pane
            # We'll use a fixed request size for now or adaptive
            aspect = img.width / img.height
            p_width = 300
            p_height = int(p_width / aspect)
            # Max dimensions
            if p_width > 400: p_width = 400
            if p_height > 300: p_height = 300
            
            ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(p_width, p_height))
            self.current_preview_image = ctk_img # Keep reference!
            self.image_preview.configure(image=self.current_preview_image, text="")
        except Exception as e:
            debug_log(f"Preview Error: {e}")

    def update_live_text(self, text, pane="monitor"):
        if pane == "after": # Often OCR results
             self.update_extracted_text(text)
        else:
             self.update_insight(text)

class FloatingMonitorView(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("AlphaMind Floating Monitor")
        self.geometry("400x300")
        self.attributes('-topmost', True)
        self.attributes('-alpha', 0.9)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(3, weight=1)
        
        ctk.CTkLabel(self, text="OCR TEXT", font=("Segoe UI", 10, "bold"), text_color="#4ec9b0").grid(row=0, column=0, sticky="w", padx=10, pady=(10, 0))
        self.text_pane = ctk.CTkTextbox(self, font=("Segoe UI", 11), height=100)
        self.text_pane.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        
        ctk.CTkLabel(self, text="AI INSIGHT", font=("Segoe UI", 10, "bold"), text_color="#ae78ff").grid(row=2, column=0, sticky="w", padx=10)
        self.insight_pane = ctk.CTkTextbox(self, font=("Segoe UI", 11), height=100)
        self.insight_pane.grid(row=3, column=0, sticky="nsew", padx=10, pady=5)
        
        self.text_pane.insert("1.0", "Waiting for capture...")
        self.insight_pane.insert("1.0", "Waiting for AI...")

    def update_text(self, text):
        self.text_pane.delete("1.0", "end")
        self.text_pane.insert("1.0", text)

    def update_insight(self, insight):
        self.insight_pane.delete("1.0", "end")
        self.insight_pane.insert("1.0", insight)
