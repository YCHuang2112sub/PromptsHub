import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import pyperclip

class PromptLibraryTab(ctk.CTkFrame):
    def __init__(self, parent, app_instance):
        super().__init__(parent)
        self.app = app_instance
        self.db = app_instance.db
        
        # Layout: Paned-like structure using grid weights
        self.grid_columnconfigure(0, weight=1) # Categories
        self.grid_columnconfigure(1, weight=3) # Editor
        self.grid_rowconfigure(0, weight=1)
        
        self.create_categories_panel()
        self.create_editor_panel()
        
        # Initial State
        self.current_prompts = []
        self.selected_category = None
        self.load_categories()

    def create_categories_panel(self):
        # Panel Container
        panel = ctk.CTkFrame(self)
        panel.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        panel.grid_rowconfigure(1, weight=1)
        panel.grid_columnconfigure(0, weight=1)
        
        # Header Frame (Label + Buttons)
        header_frame = ctk.CTkFrame(panel, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        
        ctk.CTkLabel(header_frame, text="🗂️ Categories", font=("Segoe UI", 12, "bold")).pack(side="left")
        
        # Add/Remove Buttons
        ctk.CTkButton(header_frame, text="+", width=30, command=self.add_category_dialog).pack(side="right", padx=2)
        ctk.CTkButton(header_frame, text="-", width=30, fg_color="#555", command=self.remove_category_action).pack(side="right", padx=2)
        
        # Categories List (Scrollable)
        self.categories_scroll = ctk.CTkScrollableFrame(panel)
        self.categories_scroll.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        # Add "All" to start
        self.categories = ["All"]


    def create_editor_panel(self):
        # Panel Container
        panel = ctk.CTkFrame(self)
        panel.grid(row=0, column=1, sticky="nsew", padx=(0, 10), pady=10)
        panel.grid_rowconfigure(3, weight=1) # Editor expands (Row 3)
        panel.grid_columnconfigure(0, weight=1)
        
        # 1. Prompts List for Category
        list_frame = ctk.CTkFrame(panel, fg_color="transparent")
        list_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        
        ctk.CTkLabel(list_frame, text="Select Prompt:", font=("Segoe UI", 12, "bold")).pack(anchor="w")
        
        self.prompts_scroll = ctk.CTkScrollableFrame(list_frame, height=100)
        self.prompts_scroll.pack(fill="x", pady=5)
        
        # 2. Editor Fields
        fields_frame = ctk.CTkFrame(panel, fg_color="transparent")
        fields_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        
        ctk.CTkLabel(fields_frame, text="Name:").pack(anchor="w")
        self.name_entry = ctk.CTkEntry(fields_frame)
        self.name_entry.pack(fill="x", pady=(0, 5))
        
        ctk.CTkLabel(panel, text="Prompt Template:", font=("Segoe UI", 12, "bold")).grid(row=2, column=0, sticky="nw", padx=10)
        
        self.editor = ctk.CTkTextbox(panel, font=("Consolas", 12))
        self.editor.grid(row=3, column=0, sticky="nsew", padx=10, pady=(0, 10))
        
        # 3. Actions
        actions_frame = ctk.CTkFrame(panel, fg_color="transparent")
        actions_frame.grid(row=4, column=0, sticky="ew", padx=10, pady=(0, 20))
        
        ctk.CTkButton(actions_frame, text="💾 Save", width=80, command=self.save_prompt).pack(side="left", padx=(0, 5))
        ctk.CTkButton(actions_frame, text="🚀 Use", width=80, command=self.use_prompt).pack(side="left", padx=(0, 5))
        ctk.CTkButton(actions_frame, text="🗑️ Delete", width=80, fg_color="#f14c4c", hover_color="#d13a3a", command=self.delete_prompt).pack(side="left", padx=(0, 5))
        ctk.CTkButton(actions_frame, text="📋 Copy", width=80, command=self.copy_prompt).pack(side="right")

    # --- Logic ---

    def load_categories(self):
        # Fetch from DB
        db_cats = self.db.get_categories()
        self.categories = ["All"] + db_cats
        
        # Clear existing
        for widget in self.categories_scroll.winfo_children():
            widget.destroy()

        for cat in self.categories:
            btn = ctk.CTkButton(
                self.categories_scroll,
                text=cat,
                anchor="w",
                fg_color="transparent",
                text_color=("gray10", "gray90"),
                hover_color=("gray70", "gray30"),
                command=lambda c=cat: self.load_prompts_for_category(c)
            )
            btn.pack(fill="x", pady=1)

    def add_category_dialog(self):
        dialog = ctk.CTkInputDialog(text="Enter category name:", title="New Category")
        name = dialog.get_input()
        if name:
            # Add icon if missing
            if not any(char in name for char in ["📝", "💻", "🔍", "🎨", "🧠", "📊", "🎯", "📁"]):
                 name = f"📁 {name}"
                 
            if self.db.add_category(name):
                self.load_categories()
                self.app.status_var.set(f"✅ Category '{name}' added")
            else:
                messagebox.showerror("Error", "Category already exists!")

    def remove_category_action(self):
        if not self.selected_category or self.selected_category == "All":
            messagebox.showwarning("Selection", "Please select a specific category to remove.")
            return
            
        if messagebox.askyesno("Confirm", f"Delete category '{self.selected_category}'? Prompts will remain but lose this category."):
            self.db.delete_category(self.selected_category)
            self.selected_category = None
            self.load_categories()
            self.app.status_var.set("✅ Category removed")

    def load_prompts_for_category(self, category):
        self.selected_category = category
        # Clean category name (remove emoji for DB query)
        db_cat = category
        if category == "All":
            db_cat = None
            
        self.current_prompts = self.db.get_prompts(db_cat)
        
        # Clear list
        for widget in self.prompts_scroll.winfo_children():
            widget.destroy()
            
        # Populate list
        for prompt in self.current_prompts:
            btn = ctk.CTkButton(
                self.prompts_scroll,
                text=f"{prompt['name']}",
                anchor="w",
                fg_color="transparent",
                border_width=1,
                border_color="#3e3e42",
                command=lambda p=prompt: self.load_prompt_to_editor(p)
            )
            btn.pack(fill="x", pady=2)

    def load_prompt_to_editor(self, prompt):
        self.selected_prompt = prompt
        self.name_entry.delete(0, "end")
        self.name_entry.insert(0, prompt['name'])
        self.editor.delete("1.0", "end")
        self.editor.insert("1.0", prompt['content'])

    def save_prompt(self):
        name = self.name_entry.get().strip()
        content = self.editor.get("1.0", "end-1c").strip()
        
        if not name or not content:
            self.app.status_var.set("❌ Name and content required")
            return
            
        # Determine category
        cat = "Custom"
        if self.selected_category and self.selected_category != "All":
            cat = self.selected_category
            
        try:
            self.db.add_prompt(name, content, cat)
            self.app.status_var.set(f"✅ Saved prompt: {name}")
            # Refresh list if category matches
            if self.selected_category:
                self.load_prompts_for_category(self.selected_category)
        except Exception as e:
            print(f"Error saving: {e}")

    def delete_prompt(self):
        if hasattr(self, 'selected_prompt'):
            if messagebox.askyesno("Confirm", "Delete prompt?"):
                self.db.delete_prompt(self.selected_prompt['id'])
                # Refresh
                if self.selected_category:
                    self.load_prompts_for_category(self.selected_category)
                # Clear editor
                self.name_entry.delete(0, "end")
                self.editor.delete("1.0", "end")

    def use_prompt(self):
        content = self.editor.get("1.0", "end-1c").strip()
        if content:
            self.app.use_prompt_template(content)

    def copy_prompt(self):
        content = self.editor.get("1.0", "end-1c").strip()
        if content:
            pyperclip.copy(content)
            self.app.status_var.set("✅ Copied prompt")
