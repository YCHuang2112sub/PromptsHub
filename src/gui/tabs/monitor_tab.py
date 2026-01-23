import customtkinter as ctk
from utils.diagnostic_helper import debug_log
from datetime import datetime

class MonitorTab(ctk.CTkFrame):
    def __init__(self, parent, app_instance):
        super().__init__(parent)
        self.app = app_instance
        self.db = app_instance.db
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # 🟢 Control Header
        header = ctk.CTkFrame(self)
        header.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        ctk.CTkLabel(header, text="🔍 Region Monitor Studio", font=("Segoe UI", 16, "bold"), text_color="#4ec9b0").pack(side="left", padx=15, pady=10)
        
        ctk.CTkButton(header, text="➕ Select Region", width=140, command=self.app.initiate_screen_capture_for_monitor, fg_color="#ae78ff", hover_color="#9357e6").pack(side="left", padx=5)
        self.monitor_btn = ctk.CTkButton(header, text="Start Monitoring", width=140, command=self.toggle_monitoring)
        self.monitor_btn.pack(side="left", padx=5)
        self.monitor_status = ctk.CTkLabel(header, text="Inactive", text_color="gray")
        self.monitor_status.pack(side="left", padx=15)
        
        # 📜 Dual Column Content
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.content.grid_columnconfigure(0, weight=1) # Log
        self.content.grid_columnconfigure(1, weight=1) # Insight
        self.content.grid_rowconfigure(1, weight=1)
        
        # column 0: Logs
        ctk.CTkLabel(self.content, text="ACTIVITY LOG", font=("Segoe UI", 10, "bold"), text_color="gray").grid(row=0, column=0, sticky="w", padx=5)
        self.log_text = ctk.CTkTextbox(self.content, font=("Consolas", 11), border_width=1, border_color="#333")
        self.log_text.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        # column 1: Insights
        ctk.CTkLabel(self.content, text="LLM INSIGHTS", font=("Segoe UI", 10, "bold"), text_color="gray").grid(row=0, column=1, sticky="w", padx=5)
        self.insight_text = ctk.CTkTextbox(self.content, font=("Segoe UI", 12), border_width=1, border_color="#333")
        self.insight_text.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)
        
        self.log_text.insert("1.0", "--- Monitor Ready ---\n1. Click 'Select Region' to target a screen area.\n2. Click 'Start Monitoring' for auto-capture.\n")
        self.insight_text.insert("1.0", "--- AI Analysis results will appear here ---")
        
    def toggle_monitoring(self):
        if hasattr(self.app, 'region_monitor') and self.app.region_monitor:
            self.app.stop_region_monitoring()
            self.monitor_btn.configure(text="Start Monitoring", fg_color=["#3B8ED0", "#1F6AA5"])
            self.monitor_status.configure(text="Inactive", text_color="gray")
            self.add_log("🛑 Monitoring stopped.")
        else:
            self.app.start_region_monitoring()
            self.monitor_btn.configure(text="Stop Monitoring", fg_color="#f14c4c")
            self.monitor_status.configure(text="● LIVE", text_color="#f14c4c")
            self.add_log("▶️ Monitoring started.")

    def add_log(self, message):
        self.log_text.insert("end", f"\n[{datetime.now().strftime('%H:%M:%S')}] {message}")
        self.log_text.see("end")

    def update_insight(self, insight):
        self.insight_text.insert("end", f"\n\n--- Analysis at {datetime.now().strftime('%H:%M:%S')} ---\n{insight}")
        self.insight_text.see("end")

    def set_captured_image(self, img):
        """Called when a region is selected for monitoring"""
        self.current_image = img
        self.add_log(f"📍 Region selected: {img.width}x{img.height}")

    def update_live_text(self, text, pane="live"):
        self.update_insight(text)
