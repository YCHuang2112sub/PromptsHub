#!/usr/bin/env python3
"""
PromptHub - AlphaMind Edition
A stylish, modern interface for intelligent prompt management and LLM interaction.
Codename: AlphaMind | Vision: Alicization
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, font
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
import subprocess
import requests

# Modern color scheme inspired by VS Code Dark and Discord
COLORS = {
    # Main theme colors
    'bg_primary': '#1e1e1e',      # Dark background
    'bg_secondary': '#252526',    # Slightly lighter
    'bg_tertiary': '#2d2d30',     # Input backgrounds
    'bg_accent': '#007acc',       # Blue accent
    'bg_success': '#4ec9b0',      # Teal success
    'bg_warning': '#ffcc02',      # Yellow warning
    'bg_error': '#f14c4c',        # Red error
    'bg_hover': '#3e3e42',        # Hover states
    'bg_purple': '#9d4edd',       # Purple option
    'bg_green': '#52b788',        # Green option
    'bg_orange': '#f77f00',       # Orange option
    
    # Text colors
    'text_primary': '#d4d4d4',    # Main text - softer than pure white
    'text_secondary': '#9d9d9d',  # Secondary text - lighter gray
    'text_accent': '#4fc1ff',     # Accent text
    'text_success': '#4ec9b0',    # Success text
    'text_warning': '#ffcc02',    # Warning text
    'text_error': '#f14c4c',      # Error text
    'text_white': '#e8e8e8',      # Softer white instead of pure white
    'text_button': '#1a1a1a',     # Dark text for buttons (good contrast on teal)
    
    # Border colors
    'border_primary': '#3e3e42',  # Main borders
    'border_accent': '#007acc',   # Accent borders
    'border_focus': '#4fc1ff',    # Focus borders
}

# Modern fonts
FONTS = {
    'heading_large': ('Segoe UI', 16, 'bold'),
    'heading_medium': ('Segoe UI', 14, 'bold'),
    'heading_small': ('Segoe UI', 12, 'bold'),
    'body_large': ('Segoe UI', 11),
    'body_medium': ('Segoe UI', 10),
    'body_small': ('Segoe UI', 9),
    'mono': ('Consolas', 10),
    'mono_small': ('Consolas', 9),
}

class ModernFrame(ttk.Frame):
    """Custom frame with modern styling"""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.configure(style='Modern.TFrame')

class ModernButton(ttk.Button):
    """Custom button with modern styling"""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.configure(style='Modern.TButton')

class ModernEntry(ttk.Entry):
    """Custom entry with modern styling"""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.configure(style='Modern.TEntry')

class PromptHubGUI:
    """Modern, stylish GUI for PromptHub - AlphaMind Edition"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        self.setup_styles()
        self.setup_variables()
        self.create_ui()
        self.apply_modern_theming()
        
    def setup_window(self):
        """Setup main window with modern styling"""
        self.root.title("🧠 AlphaMind - Intelligent Prompt Hub")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 600)
        self.root.configure(bg=COLORS['bg_primary'])
        
        # Make window look modern on Windows
        try:
            self.root.wm_attributes('-alpha', 0.98)  # Slight transparency
            # Remove window decorations for ultra-modern look (optional)
            # self.root.overrideredirect(True)
        except:
            pass
            
        # Center window on screen
        self.center_window()
        
    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (1200 // 2)
        y = (self.root.winfo_screenheight() // 2) - (800 // 2)
        self.root.geometry(f'1200x800+{x}+{y}')
        
    def setup_styles(self):
        """Setup modern ttk styles"""
        style = ttk.Style()
        
        # Configure modern frame styles
        style.configure('Modern.TFrame',
                       background=COLORS['bg_primary'],
                       borderwidth=0)
        
        style.configure('Card.TFrame',
                       background=COLORS['bg_secondary'],
                       relief='flat',
                       borderwidth=1)
        
        # Configure modern button styles
        style.configure('Modern.TButton',
                       background=COLORS['bg_success'],  # Changed from bg_accent to bg_success (teal)
                       foreground=COLORS['text_button'],  # Dark text for better contrast on teal background
                       borderwidth=0,
                       focuscolor='none',
                       font=FONTS['body_medium'])
        
        style.map('Modern.TButton',
                 background=[('active', COLORS['bg_accent']),  # Hover color
                           ('pressed', COLORS['bg_success'])])  # Pressed color
        
        # Configure accent button style for important actions
        style.configure('Accent.TButton',
                       background=COLORS['bg_accent'],
                       foreground=COLORS['text_button'],
                       borderwidth=0,
                       focuscolor='none',
                       font=FONTS['body_medium'])
        
        style.map('Accent.TButton',
                 background=[('active', COLORS['bg_success']),
                           ('pressed', COLORS['bg_accent'])])
        
        # Configure modern entry styles
        style.configure('Modern.TEntry',
                       fieldbackground=COLORS['bg_tertiary'],
                       foreground=COLORS['text_primary'],
                       borderwidth=1,
                       insertcolor=COLORS['text_accent'],
                       font=FONTS['body_medium'])
        
        style.map('Modern.TEntry',
                 focuscolor=[('focus', COLORS['border_focus'])])
        
        # Configure modern label styles
        style.configure('Modern.TLabel',
                       background=COLORS['bg_primary'],
                       foreground=COLORS['text_primary'],
                       font=FONTS['body_medium'])
        
        style.configure('Heading.TLabel',
                       background=COLORS['bg_primary'],
                       foreground=COLORS['text_primary'],  # Changed from text_white to text_primary
                       font=FONTS['heading_medium'])
        
        style.configure('Accent.TLabel',
                       background=COLORS['bg_primary'],
                       foreground=COLORS['text_accent'],
                       font=FONTS['body_medium'])
        
        # Configure modern notebook styles
        style.configure('Modern.TNotebook',
                       background=COLORS['bg_primary'],
                       borderwidth=0,
                       tabmargins=[0, 0, 0, 0])
        
        style.configure('Modern.TNotebook.Tab',
                       background=COLORS['bg_secondary'],
                       foreground=COLORS['text_secondary'],  # Much darker for unselected tabs
                       padding=[20, 10],
                       font=FONTS['body_medium'])
        
        style.map('Modern.TNotebook.Tab',
                 background=[('selected', COLORS['bg_accent']),
                           ('active', COLORS['bg_hover'])],
                 foreground=[('selected', COLORS['text_button']),  # Much darker text for selected tabs
                           ('active', COLORS['text_secondary'])])  # Darker for active/hover
    
    def setup_variables(self):
        """Setup tkinter variables"""
        self.status_var = tk.StringVar(value="🚀 AlphaMind Ready")
        self.current_prompt = tk.StringVar()
        self.llm_provider_var = tk.StringVar(value="Claude")
        self.monitoring_status = tk.StringVar(value="● Active")
        self.processing_status = tk.StringVar(value="")
        self.is_processing = False
        self.ocr_expanded = False
        self.current_image = None
        
        # LLM configuration (from original)
        self.llm_provider = None
        self.llm_api_key = None
        self.llm_model = None
        
        # Default LLM prompt
        self.llm_prompt = """Explain this text clearly and concisely:
- What does it do/mean?
- Key points to understand
- Any important warnings or notes

Text to explain:
{text}"""
        
        # Detect available LLM provider
        self.detect_llm_provider()
    
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
            self.llm_model = "gpt-4"
            return
            
        # Check for Gemini
        gemini_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if gemini_key:
            self.llm_provider = "gemini"
            self.llm_api_key = gemini_key
            self.llm_model = "gemini-pro"
            return
            
        print("No LLM API keys found in environment variables")
        
    def create_ui(self):
        """Create the main user interface"""
        # Main container
        self.main_container = ModernFrame(self.root)
        self.main_container.pack(fill='both', expand=True, padx=0, pady=0)
        
        # Create header
        self.create_header()
        
        # Create main content area
        self.create_main_content()
        
        # Create footer
        self.create_footer()
        
    def create_header(self):
        """Create modern header with branding"""
        header_frame = ModernFrame(self.main_container)
        header_frame.pack(fill='x', padx=20, pady=(20, 10))
        
        # Left side - Logo and title
        left_frame = ModernFrame(header_frame)
        left_frame.pack(side='left', fill='y')
        
        # Title with gradient effect (simulated with multiple labels)
        title_frame = ModernFrame(left_frame)
        title_frame.pack(side='left')
        
        title_main = tk.Label(title_frame, 
                             text="🧠 AlphaMind",
                             font=FONTS['heading_large'],
                             fg=COLORS['text_primary'],
                             bg=COLORS['bg_primary'])
        title_main.pack(side='left')
        
        subtitle = tk.Label(title_frame,
                           text=" Intelligent Prompt Hub",
                           font=FONTS['body_large'],
                           fg=COLORS['text_accent'],
                           bg=COLORS['bg_primary'])
        subtitle.pack(side='left', padx=(5, 0))
        
        # Right side - Status and controls
        right_frame = ModernFrame(header_frame)
        right_frame.pack(side='right', fill='y')
        
        # Status indicator
        status_frame = ModernFrame(right_frame)
        status_frame.pack(side='right', padx=(0, 20))
        
        status_label = tk.Label(status_frame,
                               textvariable=self.status_var,
                               font=FONTS['body_medium'],
                               fg=COLORS['text_success'],
                               bg=COLORS['bg_primary'])
        status_label.pack()
        
        # Quick action buttons
        actions_frame = ModernFrame(right_frame)
        actions_frame.pack(side='right')
        
        ModernButton(actions_frame, text="⚙️ Settings", 
                    command=self.show_settings).pack(side='right', padx=(5, 0))
        ModernButton(actions_frame, text="📝 Prompts", 
                    command=self.show_prompt_library).pack(side='right', padx=(5, 0))
        ModernButton(actions_frame, text="📊 Analytics", 
                    command=self.show_analytics).pack(side='right', padx=(5, 0))
        
    def create_main_content(self):
        """Create main content area with modern layout"""
        content_frame = ModernFrame(self.main_container)
        content_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Create notebook with modern tabs
        self.notebook = ttk.Notebook(content_frame, style='Modern.TNotebook')
        self.notebook.pack(fill='both', expand=True)
        
        # Create tabs
        self.create_live_capture_tab()
        self.create_llm_playground_tab()
        self.create_analytics_tab()
        
    def create_live_capture_tab(self):
        """Create live capture tab with modern design"""
        tab_frame = ModernFrame(self.notebook)
        self.notebook.add(tab_frame, text="📋 Live Capture")
        
        # Screen OCR section at the very top (always visible)
        self.create_screen_ocr_section(tab_frame)
        
        # Main layout - left and right panels
        main_paned = ttk.PanedWindow(tab_frame, orient='horizontal')
        main_paned.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Left panel - Live capture area
        left_panel = self.create_card_frame(main_paned, "🎯 Live Capture Area")
        main_paned.add(left_panel, weight=3)
        
        # Monitoring status
        monitor_frame = ModernFrame(left_panel)
        monitor_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        monitor_label = tk.Label(monitor_frame,
                                textvariable=self.monitoring_status,
                                font=FONTS['body_medium'],
                                fg=COLORS['text_success'],
                                bg=COLORS['bg_secondary'])
        monitor_label.pack(side='left')
        
        # Processing status indicator
        self.processing_label = tk.Label(monitor_frame,
                                        textvariable=self.processing_status,
                                        font=FONTS['body_medium'],
                                        fg=COLORS['text_warning'],
                                        bg=COLORS['bg_secondary'])
        self.processing_label.pack(side='right')
        
        # Live text area with modern styling
        self.live_text = scrolledtext.ScrolledText(
            left_panel,
            height=15,
            font=FONTS['mono'],
            bg=COLORS['bg_tertiary'],
            fg=COLORS['text_primary'],
            insertbackground=COLORS['text_accent'],
            selectbackground=COLORS['bg_accent'],
            selectforeground=COLORS['text_white'],
            borderwidth=0,
            relief='flat'
        )
        self.live_text.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        # Action buttons
        actions_frame = ModernFrame(left_panel)
        actions_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        ModernButton(actions_frame, text="💾 Store", 
                    command=self.store_current).pack(side='left', padx=(0, 5))
        ModernButton(actions_frame, text="🤖 Process with LLM", 
                    command=self.process_with_llm).pack(side='left', padx=(0, 5))
        ModernButton(actions_frame, text="⚙️ Edit Prompt", 
                    command=self.edit_prompt).pack(side='left', padx=(0, 5))
        ModernButton(actions_frame, text="🔄 Clear", 
                    command=self.clear_live).pack(side='left', padx=(0, 5))
        
        # Right panel - Stored items
        right_panel = self.create_card_frame(main_paned, "📚 Stored Items")
        main_paned.add(right_panel, weight=2)
        
        # Search bar
        search_frame = ModernFrame(right_panel)
        search_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        tk.Label(search_frame, text="🔍", 
                font=FONTS['body_medium'],
                fg=COLORS['text_secondary'],
                bg=COLORS['bg_secondary']).pack(side='left')
        
        self.search_entry = ModernEntry(search_frame)
        self.search_entry.pack(fill='x', padx=(5, 0))
        
        # Items list with modern styling
        list_frame = ModernFrame(right_panel)
        list_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        # Create custom listbox with modern styling
        self.items_listbox = tk.Listbox(
            list_frame,
            font=FONTS['body_medium'],
            bg=COLORS['bg_tertiary'],
            fg=COLORS['text_primary'],
            selectbackground=COLORS['bg_accent'],
            selectforeground=COLORS['text_white'],
            borderwidth=0,
            relief='flat',
            activestyle='none'
        )
        self.items_listbox.pack(fill='both', expand=True)
        
        # Items actions
        items_actions = ModernFrame(right_panel)
        items_actions.pack(fill='x', padx=10, pady=(0, 10))
        
        ModernButton(items_actions, text="📋 Copy", 
                    command=self.copy_selected).pack(side='left', padx=(0, 5))
        ModernButton(items_actions, text="🗑️ Delete", 
                    command=self.delete_selected).pack(side='left', padx=(0, 5))
        ModernButton(items_actions, text="📤 Export", 
                    command=self.export_items).pack(side='right')
        
    def create_prompt_library_tab(self):
        """Create prompt library tab for managing prompt patterns"""
        tab_frame = ModernFrame(self.notebook)
        self.notebook.add(tab_frame, text="📝 Prompt Library")
        
        # Split into categories and prompt editor
        paned = ttk.PanedWindow(tab_frame, orient='horizontal')
        paned.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Left - Categories
        categories_panel = self.create_card_frame(paned, "🗂️ Prompt Categories")
        paned.add(categories_panel, weight=1)
        
        # Categories list
        categories = ["📝 Writing", "💻 Coding", "🔍 Analysis", "🎨 Creative", "🧠 Problem Solving", "📊 Data", "🎯 Custom"]
        
        self.categories_listbox = tk.Listbox(
            categories_panel,
            font=FONTS['body_medium'],
            bg=COLORS['bg_tertiary'],
            fg=COLORS['text_primary'],
            selectbackground=COLORS['bg_accent'],
            selectforeground=COLORS['text_white'],
            borderwidth=0,
            relief='flat'
        )
        self.categories_listbox.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        for category in categories:
            self.categories_listbox.insert('end', category)
        
        # Right - Prompt editor
        editor_panel = self.create_card_frame(paned, "✨ Prompt Editor")
        paned.add(editor_panel, weight=2)
        
        # Prompt name
        name_frame = ModernFrame(editor_panel)
        name_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        tk.Label(name_frame, text="Prompt Name:",
                font=FONTS['body_medium'],
                fg=COLORS['text_primary'],
                bg=COLORS['bg_secondary']).pack(anchor='w')
        
        self.prompt_name_entry = ModernEntry(name_frame)
        self.prompt_name_entry.pack(fill='x', pady=(5, 0))
        
        # Prompt content
        content_frame = ModernFrame(editor_panel)
        content_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        tk.Label(content_frame, text="Prompt Template:",
                font=FONTS['body_medium'],
                fg=COLORS['text_primary'],
                bg=COLORS['bg_secondary']).pack(anchor='w')
        
        self.prompt_editor = scrolledtext.ScrolledText(
            content_frame,
            height=10,
            font=FONTS['mono'],
            bg=COLORS['bg_tertiary'],
            fg=COLORS['text_primary'],
            insertbackground=COLORS['text_accent'],
            borderwidth=0,
            relief='flat'
        )
        self.prompt_editor.pack(fill='both', expand=True, pady=(5, 0))
        
        # Prompt actions
        prompt_actions = ModernFrame(editor_panel)
        prompt_actions.pack(fill='x', padx=10, pady=(0, 10))
        
        ModernButton(prompt_actions, text="💾 Save Prompt", 
                    command=self.save_prompt).pack(side='left', padx=(0, 5))
        ModernButton(prompt_actions, text="🚀 Use Prompt", 
                    command=self.use_prompt).pack(side='left', padx=(0, 5))
        ModernButton(prompt_actions, text="📋 Copy Template", 
                    command=self.copy_prompt).pack(side='right')
        
    def create_llm_playground_tab(self):
        """Create LLM playground tab for interactive AI sessions"""
        tab_frame = ModernFrame(self.notebook)
        self.notebook.add(tab_frame, text="🤖 LLM Playground")
        
        # Provider selection
        provider_frame = ModernFrame(tab_frame)
        provider_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Label(provider_frame, text="🤖 AI Provider:",
                font=FONTS['body_medium'],
                fg=COLORS['text_primary'],
                bg=COLORS['bg_primary']).pack(side='left')
        
        provider_combo = ttk.Combobox(provider_frame, 
                                     textvariable=self.llm_provider_var,
                                     values=["Claude (Anthropic)", "GPT-4 (OpenAI)", "Gemini (Google)"],
                                     state="readonly")
        provider_combo.pack(side='left', padx=(10, 0))
        
        # Chat area
        chat_frame = self.create_card_frame(tab_frame, "💬 AI Conversation")
        chat_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        # Conversation display
        self.conversation_display = scrolledtext.ScrolledText(
            chat_frame,
            height=15,
            font=FONTS['mono_small'],
            bg=COLORS['bg_tertiary'],
            fg=COLORS['text_primary'],
            insertbackground=COLORS['text_accent'],
            state='disabled',
            borderwidth=0,
            relief='flat'
        )
        self.conversation_display.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        # Input area
        input_frame = ModernFrame(tab_frame)
        input_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        tk.Label(input_frame, text="💭 Your Message:",
                font=FONTS['body_medium'],
                fg=COLORS['text_primary'],
                bg=COLORS['bg_primary']).pack(anchor='w')
        
        self.message_entry = scrolledtext.ScrolledText(
            input_frame,
            height=4,
            font=FONTS['mono'],
            bg=COLORS['bg_tertiary'],
            fg=COLORS['text_primary'],
            insertbackground=COLORS['text_accent'],
            borderwidth=0,
            relief='flat'
        )
        self.message_entry.pack(fill='x', pady=(5, 10))
        
        # Send controls
        send_frame = ModernFrame(input_frame)
        send_frame.pack(fill='x')
        
        ModernButton(send_frame, text="🚀 Send Message", 
                    command=self.send_message).pack(side='right', padx=(5, 0))
        ModernButton(send_frame, text="🔄 Clear Chat", 
                    command=self.clear_chat).pack(side='right', padx=(5, 0))
        ModernButton(send_frame, text="📋 Use Clipboard", 
                    command=self.use_clipboard_in_chat).pack(side='left')
        
    def create_analytics_tab(self):
        """Create analytics tab for usage insights"""
        tab_frame = ModernFrame(self.notebook)
        self.notebook.add(tab_frame, text="📊 Analytics")
        
        # Analytics cards
        cards_frame = ModernFrame(tab_frame)
        cards_frame.pack(fill='x', padx=10, pady=10)
        
        # Usage stats cards
        stats_frame = ModernFrame(cards_frame)
        stats_frame.pack(fill='x', pady=(0, 10))
        
        # Create stat cards
        self.create_stat_card(stats_frame, "📋 Total Captures", "1,247", "left")
        self.create_stat_card(stats_frame, "🤖 LLM Queries", "89", "left", padx=(10, 0))
        self.create_stat_card(stats_frame, "💾 Stored Items", "156", "left", padx=(10, 0))
        self.create_stat_card(stats_frame, "⚡ Avg Response", "2.3s", "right")
        
        # Charts area (placeholder)
        charts_frame = self.create_card_frame(tab_frame, "📈 Usage Patterns")
        charts_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        # Placeholder for charts
        placeholder = tk.Label(charts_frame,
                              text="📊 Advanced analytics coming soon...\n\n• Usage patterns over time\n• Most used prompts\n• LLM performance metrics\n• Productivity insights",
                              font=FONTS['body_large'],
                              fg=COLORS['text_secondary'],
                              bg=COLORS['bg_secondary'],
                              justify='center')
        placeholder.pack(expand=True, fill='both', padx=20, pady=20)
        
    def create_card_frame(self, parent, title):
        """Create a modern card-style frame"""
        card = ttk.Frame(parent, style='Card.TFrame')
        
        # Card header
        header = ModernFrame(card)
        header.pack(fill='x', padx=1, pady=1)
        header.configure(style='Card.TFrame')
        
        title_label = tk.Label(header,
                              text=title,
                              font=FONTS['heading_small'],
                              fg=COLORS['text_primary'],  # Changed from text_white to text_primary
                              bg=COLORS['bg_secondary'])
        title_label.pack(anchor='w', padx=10, pady=8)
        
        return card
        
    def create_stat_card(self, parent, title, value, side, padx=(0, 0)):
        """Create a statistics card"""
        card = ModernFrame(parent)
        card.pack(side=side, fill='x', expand=True, padx=padx)
        card.configure(style='Card.TFrame')
        
        # Value
        value_label = tk.Label(card,
                              text=value,
                              font=FONTS['heading_large'],
                              fg=COLORS['text_accent'],
                              bg=COLORS['bg_secondary'])
        value_label.pack(pady=(10, 0))
        
        # Title
        title_label = tk.Label(card,
                              text=title,
                              font=FONTS['body_medium'],
                              fg=COLORS['text_secondary'],
                              bg=COLORS['bg_secondary'])
        title_label.pack(pady=(0, 10))
        
    def create_footer(self):
        """Create modern footer"""
        footer_frame = ModernFrame(self.main_container)
        footer_frame.pack(fill='x', padx=20, pady=(10, 20))
        
        # Left side - Status
        status_label = tk.Label(footer_frame,
                               textvariable=self.status_var,
                               font=FONTS['body_small'],
                               fg=COLORS['text_secondary'],
                               bg=COLORS['bg_primary'])
        status_label.pack(side='left')
        
        # Right side - Credits
        credits_label = tk.Label(footer_frame,
                                text="AlphaMind • Alicization Vision • Intelligent Prompt Hub",
                                font=FONTS['body_small'],
                                fg=COLORS['text_secondary'],
                                bg=COLORS['bg_primary'])
        credits_label.pack(side='right')
        
    def apply_modern_theming(self):
        """Apply additional modern theming"""
        # Configure root window
        self.root.configure(bg=COLORS['bg_primary'])
        
        # Bind hover effects
        self.setup_hover_effects()
        
    def setup_hover_effects(self):
        """Setup modern hover effects"""
        # Add hover effects to buttons and interactive elements
        pass
        
    # Event handlers (placeholder methods)
    def show_settings(self):
        messagebox.showinfo("Settings", "Settings dialog coming soon!")
        
    def show_analytics(self):
        messagebox.showinfo("Analytics", "Advanced analytics coming soon!")
        
    def store_current(self):
        messagebox.showinfo("Store", "Storing current text...")
        
    def process_with_llm(self):
        """Process current text with LLM - from original implementation"""
        current_text = self.live_text.get(1.0, 'end-1c').strip()
        if not current_text:
            self.status_var.set("❌ No text to process")
            self.root.after(3000, lambda: self.status_var.set("🚀 AlphaMind Ready"))
            return
        
        if not self.llm_api_key:
            self.status_var.set("⚠️ No LLM API key found")
            self.root.after(3000, lambda: self.status_var.set("🚀 AlphaMind Ready"))
            return
        
        # Show processing
        original_text = current_text
        self.live_text.delete(1.0, 'end')
        self.live_text.insert(1.0, "🤖 Processing with LLM...")
        self.status_var.set("🤖 Processing text with AI...")
        
        # Process in background
        threading.Thread(
            target=self.process_text_thread,
            args=(original_text,),
            daemon=True
        ).start()
    
    def process_text_thread(self, text):
        """Process text with LLM in background - from original implementation"""
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
            
            # Format result like original
            result = f"ORIGINAL:\n{text}\n\n{'='*50}\nPROCESSED:\n{response}"
            
            self.root.after(0, lambda: self.live_text.delete(1.0, 'end'))
            self.root.after(0, lambda: self.live_text.insert(1.0, result))
            self.root.after(0, lambda: self.status_var.set("✅ Processing complete"))
            self.root.after(3000, lambda: self.status_var.set("🚀 AlphaMind Ready"))
            
        except Exception as e:
            self.root.after(0, lambda: self.live_text.delete(1.0, 'end'))
            self.root.after(0, lambda: self.live_text.insert(1.0, f"❌ Processing failed: {e}"))
            self.root.after(0, lambda: self.status_var.set("❌ Processing failed"))
            self.root.after(3000, lambda: self.status_var.set("🚀 AlphaMind Ready"))
    
    def claude_text(self, prompt):
        """Claude text API call - Updated for AlphaMind"""
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": self.llm_api_key,
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01"
            },
            json={
                "model": "claude-3-5-sonnet-20241022",
                "max_tokens": 2000,  # Increased for better responses
                "messages": [{
                    "role": "user",
                    "content": prompt
                }]
            },
            timeout=45  # Increased timeout
        )
        
        if response.status_code == 200:
            return response.json()['content'][0]['text']
        else:
            raise Exception(f"Claude API error: {response.status_code} - {response.text}")
    
    def openai_text(self, prompt):
        """OpenAI text API call - Updated for AlphaMind"""
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {self.llm_api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "gpt-4-turbo-preview",  # Updated to latest model
                "messages": [{
                    "role": "user",
                    "content": prompt
                }],
                "max_tokens": 2000,  # Increased for better responses
                "temperature": 0.7  # Added for more natural responses
            },
            timeout=45  # Increased timeout
        )
        
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            raise Exception(f"OpenAI API error: {response.status_code} - {response.text}")
    
    def gemini_text(self, prompt):
        """Gemini text API call - Updated for AlphaMind"""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={self.llm_api_key}"
        
        response = requests.post(
            url,
            json={
                "contents": [{
                    "parts": [{
                        "text": prompt
                    }]
                }],
                "generationConfig": {
                    "maxOutputTokens": 2000,  # Increased for better responses
                    "temperature": 0.7,
                    "topP": 0.8,
                    "topK": 40
                }
            },
            timeout=45  # Increased timeout
        )
        
        if response.status_code == 200:
            result = response.json()
            return result['candidates'][0]['content']['parts'][0]['text']
        else:
            raise Exception(f"Gemini API error: {response.status_code} - {response.text}")
    
    def edit_prompt(self):
        """Edit LLM prompt - Simple tall window with all content visible"""
        dialog = tk.Toplevel(self.root)
        dialog.title("⚙️ AlphaMind - Edit LLM Prompt")
        dialog.geometry("700x800")  # Tall enough to show everything
        dialog.configure(bg=COLORS['bg_primary'])
        dialog.attributes('-topmost', True)
        dialog.resizable(True, True)
        
        # Make it modal
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Handle window close button (X) - ask to save
        def on_window_close():
            current_text = prompt_text.get(1.0, 'end-1c').strip()
            if current_text != self.llm_prompt:
                # Prompt has been modified
                result = tk.messagebox.askyesnocancel(
                    "Save Changes?", 
                    "Do you want to save your changes to the prompt?"
                )
                if result is True:  # Yes - save
                    self.llm_prompt = current_text
                    self.status_var.set("✅ Prompt saved")
                    self.root.after(3000, lambda: self.status_var.set("🚀 AlphaMind Ready"))
                elif result is False:  # No - don't save
                    pass  # Just close
                else:  # Cancel - don't close
                    return
            dialog.destroy()
        
        dialog.protocol("WM_DELETE_WINDOW", on_window_close)
        
        # Header
        header_frame = ModernFrame(dialog)
        header_frame.pack(fill='x', padx=15, pady=(15, 10))
        
        tk.Label(header_frame, 
                text="🤖 LLM Prompt Template",
                font=FONTS['heading_medium'],
                fg=COLORS['text_primary'],
                bg=COLORS['bg_primary']).pack(side='left')
        
        # Instructions
        instructions_frame = ModernFrame(dialog)
        instructions_frame.pack(fill='x', padx=15, pady=(0, 10))
        
        tk.Label(instructions_frame,
                text="Use {text} as placeholder for the input text. Customize how AI processes your content:",
                font=FONTS['body_medium'],
                fg=COLORS['text_secondary'],
                bg=COLORS['bg_primary'],
                wraplength=650,
                justify='left').pack(anchor='w')
        
        # Prompt editor
        editor_frame = ModernFrame(dialog)
        editor_frame.pack(fill='both', expand=True, padx=15, pady=(0, 10))
        
        prompt_text = scrolledtext.ScrolledText(
            editor_frame, 
            wrap='word',
            font=FONTS['mono'],
            bg=COLORS['bg_tertiary'],
            fg=COLORS['text_primary'],
            insertbackground=COLORS['text_accent'],
            selectbackground=COLORS['bg_accent'],
            selectforeground=COLORS['text_primary'],
            borderwidth=0,
            relief='flat'
        )
        prompt_text.pack(fill='both', expand=True)
        prompt_text.insert(1.0, self.llm_prompt)
        
        # Preset buttons
        preset_frame = ModernFrame(dialog)
        preset_frame.pack(fill='x', padx=15, pady=(0, 10))
        
        tk.Label(preset_frame, 
                text="🎯 Quick Presets:",
                font=FONTS['body_medium'],
                fg=COLORS['text_primary'],
                bg=COLORS['bg_primary']).pack(side='left')
        
        presets = {
            "Explain": "Explain this text clearly and concisely:\n- What does it do/mean?\n- Key points to understand\n- Any important warnings or notes\n\nText to explain:\n{text}",
            "Code": "Analyze this code:\n- What it does\n- How it works\n- Potential issues or improvements\n- Best practices\n\nCode to analyze:\n{text}",
            "Translate": "Translate this text to Chinese (Traditional):\n\n{text}",
            "Summarize": "Create a concise summary with key points:\n\n{text}",
            "Fix": "Review and fix any errors in this text:\n- Grammar and spelling\n- Clarity and structure\n- Technical accuracy\n\nText to fix:\n{text}"
        }
        
        preset_buttons_frame = ModernFrame(preset_frame)
        preset_buttons_frame.pack(side='right')
        
        for name, preset in presets.items():
            ModernButton(preset_buttons_frame, text=name,
                        command=lambda p=preset: (
                            prompt_text.delete(1.0, 'end'),
                            prompt_text.insert(1.0, p)
                        )).pack(side='left', padx=(5, 0))
        
        # Define action functions first
        def save_and_close():
            new_prompt = prompt_text.get(1.0, 'end-1c').strip()
            if new_prompt:
                self.llm_prompt = new_prompt
                self.status_var.set("✅ Prompt updated successfully")
                self.root.after(3000, lambda: self.status_var.set("🚀 AlphaMind Ready"))
                dialog.destroy()
            else:
                # Show warning if prompt is empty
                tk.messagebox.showwarning("Empty Prompt", "Please enter a prompt before saving.")
        
        def cancel_edit():
            dialog.destroy()
        
        def reset_to_default():
            prompt_text.delete(1.0, 'end')
            prompt_text.insert(1.0, """Explain this text clearly and concisely:
- What does it do/mean?
- Key points to understand
- Any important warnings or notes

Text to explain:
{text}""")
        
        # Keyboard shortcuts
        def on_ctrl_s(event):
            save_and_close()
            return "break"
        
        def on_ctrl_enter(event):
            save_and_close()
            return "break"
        
        def on_escape(event):
            cancel_edit()
            return "break"
        
        # Bind keyboard shortcuts
        dialog.bind('<Control-s>', on_ctrl_s)
        dialog.bind('<Control-Return>', on_ctrl_enter)
        dialog.bind('<Escape>', on_escape)
        prompt_text.bind('<Control-s>', on_ctrl_s)
        prompt_text.bind('<Control-Return>', on_ctrl_enter)
        
        # SIMPLE, CLEAR BUTTON SECTION
        button_section = tk.Frame(dialog, bg=COLORS['bg_secondary'], relief='solid', bd=2)
        button_section.pack(fill='x', padx=15, pady=15)
        
        # Section title
        tk.Label(button_section, 
                text="🎯 ACTIONS:",
                font=FONTS['heading_medium'],
                fg=COLORS['text_primary'],
                bg=COLORS['bg_secondary']).pack(pady=10)
        
        # Button row
        btn_row = tk.Frame(button_section, bg=COLORS['bg_secondary'])
        btn_row.pack(fill='x', padx=20, pady=(0, 15))
        
        # Reset button (left)
        ModernButton(btn_row, text="🔄 Reset to Default", command=reset_to_default).pack(side='left')
        
        # Cancel button (right)
        ModernButton(btn_row, text="❌ Cancel", command=cancel_edit).pack(side='right', padx=(5, 0))
        
        # SAVE BUTTON (right, most prominent)
        save_btn = ModernButton(btn_row, text="💾 SAVE & LEAVE", command=save_and_close)
        save_btn.pack(side='right', padx=(10, 0))
        save_btn.configure(style='Accent.TButton')
        
        # Make save button larger and more visible (ttk buttons use style, not font directly)
        # The Accent.TButton style already makes it prominent
        
        # Keyboard shortcuts help
        help_frame = ModernFrame(dialog)
        help_frame.pack(fill='x', padx=15, pady=(0, 15))
        
        tk.Label(help_frame,
                text="💡 Shortcuts: Ctrl+S (Save & Leave) • Ctrl+Enter (Save & Leave) • Escape (Cancel)",
                font=FONTS['body_small'],
                fg=COLORS['text_secondary'],
                bg=COLORS['bg_primary']).pack(anchor='w')
        
        # Focus on text area
        prompt_text.focus_set()
        
    def clear_live(self):
        self.live_text.delete(1.0, 'end')
        
    def copy_selected(self):
        messagebox.showinfo("Copy", "Copying selected item...")
        
    def delete_selected(self):
        messagebox.showinfo("Delete", "Deleting selected item...")
        
    def export_items(self):
        messagebox.showinfo("Export", "Exporting items...")
        
    def save_prompt(self):
        messagebox.showinfo("Save", "Saving prompt...")
        
    def use_prompt(self):
        messagebox.showinfo("Use", "Using prompt...")
        
    def copy_prompt(self):
        messagebox.showinfo("Copy", "Copying prompt template...")
        
    def send_message(self):
        """Send message to LLM - show loading indicator"""
        if self.is_processing:
            return
            
        # Get message text
        message = self.message_entry.get(1.0, 'end-1c').strip()
        if not message:
            self.status_var.set("❌ No message to send")
            self.root.after(3000, lambda: self.status_var.set("🚀 AlphaMind Ready"))
            return
            
        # Start processing
        self.start_llm_processing(message, is_chat=True)
        
    def clear_chat(self):
        self.conversation_display.config(state='normal')
        self.conversation_display.delete(1.0, 'end')
        self.conversation_display.config(state='disabled')
        
    def use_clipboard_in_chat(self):
        messagebox.showinfo("Clipboard", "Using clipboard content...")
    
    def create_screen_ocr_section(self, parent):
        """Create screen OCR section at the top of Live Capture tab"""
        # OCR Card at the top
        ocr_card = self.create_card_frame(parent, "📷 Screen OCR - Direct Crop")
        ocr_card.pack(fill='x', padx=10, pady=(10, 10))
        
        # OCR content layout
        ocr_content = ModernFrame(ocr_card)
        ocr_content.pack(fill='x', padx=10, pady=(0, 10))
        
        # Left side - Controls
        controls_frame = ModernFrame(ocr_content)
        controls_frame.pack(side='left', fill='y')
        
        ModernButton(controls_frame, text="📷 Crop Screen", 
                    command=self.crop_screen).pack(pady=(0, 5))
        ModernButton(controls_frame, text="🔍 Extract Text", 
                    command=self.extract_text_from_image).pack(pady=(0, 5))
        
        # Status indicator
        self.ocr_status = tk.Label(controls_frame,
                                  text="Ready to capture",
                                  font=FONTS['body_small'],
                                  fg=COLORS['text_secondary'],
                                  bg=COLORS['bg_secondary'])
        self.ocr_status.pack(pady=(5, 0))
        
        # Right side - Image preview
        preview_frame = ModernFrame(ocr_content)
        preview_frame.pack(side='right', fill='both', expand=True, padx=(10, 0))
        
        self.image_label = tk.Label(preview_frame,
                                   text="[No image captured]\nClick 'Crop Screen' to select area",
                                   font=FONTS['body_medium'],
                                   fg=COLORS['text_secondary'],
                                   bg=COLORS['bg_tertiary'],
                                   relief='solid',
                                   borderwidth=1,
                                   width=25, 
                                   height=6,
                                   justify='center')
        self.image_label.pack(fill='both', expand=True)
    
    def toggle_ocr_panel(self):
        """Toggle the OCR panel visibility"""
        if self.ocr_expanded:
            # Hide panel
            self.ocr_panel.pack_forget()
            self.ocr_toggle_btn.config(text="▼ Screen OCR")
            self.ocr_expanded = False
        else:
            # Show panel
            self.ocr_panel.pack(fill='x', padx=10, pady=(0, 10))
            self.ocr_toggle_btn.config(text="▲ Screen OCR")
            self.ocr_expanded = True
    
    def crop_screen(self):
        """Interactive screen cropping - from original implementation"""
        try:
            from PIL import Image, ImageGrab, ImageTk
        except ImportError:
            self.status_var.set("❌ Please install: pip install Pillow")
            self.root.after(3000, lambda: self.status_var.set("🚀 AlphaMind Ready"))
            return
        
        self.ocr_status.config(text="Select screen region...", fg=COLORS['text_warning'])
        self.status_var.set("📷 Click and drag to select area...")
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
                end_x, end_y = event.x, event.y
                
                # Ensure we have a valid selection
                if abs(end_x - start_x) < 10 or abs(end_y - start_y) < 10:
                    overlay.destroy()
                    self.root.deiconify()
                    self.ocr_status.config(text="Selection too small", fg=COLORS['text_error'])
                    self.status_var.set("🚀 AlphaMind Ready")
                    return
                
                # Calculate crop area
                x1, x2 = min(start_x, end_x), max(start_x, end_x)
                y1, y2 = min(start_y, end_y), max(start_y, end_y)
                
                overlay.destroy()
                
                # Capture the selected area
                self.capture_selected_area(x1, y1, x2, y2)
            
            def on_escape(event):
                overlay.destroy()
                self.root.deiconify()
                self.ocr_status.config(text="Capture cancelled", fg=COLORS['text_secondary'])
                self.status_var.set("🚀 AlphaMind Ready")
            
            # Bind events
            canvas.bind('<Button-1>', on_mouse_down)
            canvas.bind('<B1-Motion>', on_mouse_drag)
            canvas.bind('<ButtonRelease-1>', on_mouse_up)
            overlay.bind('<Escape>', on_escape)
            overlay.focus_set()
            
            # Instructions
            instructions = tk.Label(canvas, 
                                   text="Click and drag to select area • Press ESC to cancel",
                                   font=FONTS['body_large'],
                                   fg='white',
                                   bg='black')
            instructions.pack(pady=20)
            
        except Exception as e:
            overlay.destroy() if 'overlay' in locals() else None
            self.root.deiconify()
            self.ocr_status.config(text=f"Error: {str(e)}", fg=COLORS['text_error'])
            self.status_var.set("🚀 AlphaMind Ready")
    
    def capture_selected_area(self, x1, y1, x2, y2):
        """Capture the selected screen area"""
        try:
            from PIL import Image, ImageGrab, ImageTk
            
            # Capture the selected area
            screenshot = ImageGrab.grab(bbox=(x1, y1, x2, y2))
            self.current_image = screenshot
            
            # Create thumbnail for preview
            thumbnail = screenshot.copy()
            thumbnail.thumbnail((200, 150), Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage for display
            photo = ImageTk.PhotoImage(thumbnail)
            
            # Update the image label
            self.image_label.configure(image=photo, text="")
            self.image_label.image = photo  # Keep a reference
            
            # Update status
            self.ocr_status.config(text=f"Captured {screenshot.width}×{screenshot.height}", 
                                  fg=COLORS['text_success'])
            self.status_var.set("✅ Screen area captured - ready for OCR")
            self.root.deiconify()
            
            # Auto-extract text
            self.root.after(1000, self.extract_text_from_image)
            
        except Exception as e:
            self.root.deiconify()
            self.ocr_status.config(text=f"Capture error: {str(e)}", fg=COLORS['text_error'])
            self.status_var.set("🚀 AlphaMind Ready")
    
    def extract_text_from_image(self):
        """Extract text from captured image using LLM vision"""
        if not self.current_image:
            self.status_var.set("❌ No image to process")
            self.root.after(3000, lambda: self.status_var.set("🚀 AlphaMind Ready"))
            return
        
        self.ocr_status.config(text="AI analyzing image...", fg=COLORS['text_warning'])
        self.status_var.set("🤖 AI extracting text from image...")
        
        # Use LLM vision for text extraction in a separate thread
        def extract_with_llm():
            try:
                # Convert image to base64 for LLM processing
                import base64
                import io
                
                # Save image to bytes
                img_buffer = io.BytesIO()
                self.current_image.save(img_buffer, format='PNG')
                img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
                
                # Try different LLM providers in order of preference
                extracted_text = None
                
                # Try Claude first (best vision capabilities)
                claude_key = os.getenv("ANTHROPIC_API_KEY") or os.getenv("CLAUDE_API_KEY")
                if claude_key:
                    extracted_text = self.extract_text_with_claude(img_base64, claude_key)
                
                # Try GPT-4 Vision if Claude failed
                if not extracted_text:
                    openai_key = os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_KEY")
                    if openai_key:
                        extracted_text = self.extract_text_with_openai(img_base64, openai_key)
                
                # Try Gemini Vision if others failed
                if not extracted_text:
                    gemini_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
                    if gemini_key:
                        extracted_text = self.extract_text_with_gemini(img_base64, gemini_key)
                
                # Fallback if no LLM available
                if not extracted_text:
                    fallback_text = f"🤖 No LLM API keys found\n\nImage captured: {self.current_image.width}×{self.current_image.height} pixels\n\nTo enable AI text extraction, add API keys to .env:\n- ANTHROPIC_API_KEY (Claude - recommended)\n- OPENAI_API_KEY (GPT-4 Vision)\n- GOOGLE_API_KEY (Gemini Vision)"
                    self.root.after(0, lambda: self.ocr_extraction_complete(fallback_text, success=False))
                    return
                
                self.root.after(0, lambda: self.ocr_extraction_complete(extracted_text, success=True))
                
            except Exception as e:
                error_text = f"AI Vision Error: {str(e)}\n\nImage captured: {self.current_image.width}×{self.current_image.height} pixels"
                self.root.after(0, lambda: self.ocr_extraction_complete(error_text, success=False))
        
        # Run LLM vision in background thread
        llm_thread = threading.Thread(target=extract_with_llm, daemon=True)
        llm_thread.start()
    
    def extract_text_with_claude(self, img_base64, api_key):
        """Extract text using Claude Vision"""
        try:
            import requests
            
            headers = {
                "Content-Type": "application/json",
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01"
            }
            
            data = {
                "model": "claude-3-5-sonnet-20241022",
                "max_tokens": 4000,
                "messages": [{
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Extract all text from this image. Return only the text content, exactly as it appears, without any commentary or formatting. If there's no readable text, return 'No text found'."
                        },
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": img_base64
                            }
                        }
                    ]
                }]
            }
            
            response = requests.post("https://api.anthropic.com/v1/messages", 
                                   headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                return result["content"][0]["text"]
            
        except Exception as e:
            print(f"Claude vision error: {e}")
        
        return None
    
    def extract_text_with_openai(self, img_base64, api_key):
        """Extract text using GPT-4 Vision"""
        try:
            import requests
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            
            data = {
                "model": "gpt-4-vision-preview",
                "messages": [{
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Extract all text from this image. Return only the text content, exactly as it appears, without any commentary or formatting. If there's no readable text, return 'No text found'."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{img_base64}"
                            }
                        }
                    ]
                }],
                "max_tokens": 4000
            }
            
            response = requests.post("https://api.openai.com/v1/chat/completions", 
                                   headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            
        except Exception as e:
            print(f"OpenAI vision error: {e}")
        
        return None
    
    def extract_text_with_gemini(self, img_base64, api_key):
        """Extract text using Gemini Vision"""
        try:
            import requests
            
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro-vision:generateContent?key={api_key}"
            
            data = {
                "contents": [{
                    "parts": [
                        {
                            "text": "Extract all text from this image. Return only the text content, exactly as it appears, without any commentary or formatting. If there's no readable text, return 'No text found'."
                        },
                        {
                            "inline_data": {
                                "mime_type": "image/png",
                                "data": img_base64
                            }
                        }
                    ]
                }]
            }
            
            response = requests.post(url, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                return result["candidates"][0]["content"]["parts"][0]["text"]
            
        except Exception as e:
            print(f"Gemini vision error: {e}")
        
        return None
    
    def ocr_extraction_complete(self, extracted_text, success=True):
        """Complete AI vision extraction and update UI"""
        self.live_text.delete(1.0, 'end')
        self.live_text.insert(1.0, extracted_text.strip())
        
        if not success or "No LLM API keys found" in extracted_text or "AI Vision Error" in extracted_text:
            self.ocr_status.config(text="AI vision unavailable", fg=COLORS['text_warning'])
            self.status_var.set("⚠️ AI vision not available - image captured")
        else:
            self.ocr_status.config(text="AI extracted text", fg=COLORS['text_success'])
            self.status_var.set("✅ Text extracted with AI vision")
        
        self.root.after(3000, lambda: self.status_var.set("🚀 AlphaMind Ready"))
    
    def show_prompt_library(self):
        """Show prompt library window"""
        self.create_prompt_library_window()
    
    def create_prompt_library_window(self):
        """Create a separate window for prompt library management"""
        prompt_window = tk.Toplevel(self.root)
        prompt_window.title("📝 Prompt Library - AlphaMind")
        prompt_window.geometry("800x600")
        prompt_window.configure(bg=COLORS['bg_primary'])
        
        # Make it modal
        prompt_window.transient(self.root)
        prompt_window.grab_set()
        
        # Split into categories and prompt editor
        paned = ttk.PanedWindow(prompt_window, orient='horizontal')
        paned.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Left - Categories
        categories_frame = ttk.Frame(paned, style='Card.TFrame')
        paned.add(categories_frame, weight=1)
        
        tk.Label(categories_frame, text="🗂️ Prompt Categories",
                font=FONTS['heading_small'],
                fg=COLORS['text_primary'],
                bg=COLORS['bg_secondary']).pack(anchor='w', padx=10, pady=8)
        
        # Categories list
        categories = ["📝 Writing", "💻 Coding", "🔍 Analysis", "🎨 Creative", "🧠 Problem Solving", "📊 Data", "🎯 Custom"]
        
        categories_listbox = tk.Listbox(
            categories_frame,
            font=FONTS['body_medium'],
            bg=COLORS['bg_tertiary'],
            fg=COLORS['text_primary'],
            selectbackground=COLORS['bg_accent'],
            selectforeground=COLORS['text_primary'],
            borderwidth=0,
            relief='flat'
        )
        categories_listbox.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        for category in categories:
            categories_listbox.insert('end', category)
        
        # Right - Prompt editor
        editor_frame = ttk.Frame(paned, style='Card.TFrame')
        paned.add(editor_frame, weight=2)
        
        tk.Label(editor_frame, text="✨ Prompt Editor",
                font=FONTS['heading_small'],
                fg=COLORS['text_primary'],
                bg=COLORS['bg_secondary']).pack(anchor='w', padx=10, pady=8)
        
        # Prompt name
        name_frame = ModernFrame(editor_frame)
        name_frame.pack(fill='x', padx=10, pady=(0, 10))
        name_frame.configure(style='Card.TFrame')
        
        tk.Label(name_frame, text="Prompt Name:",
                font=FONTS['body_medium'],
                fg=COLORS['text_primary'],
                bg=COLORS['bg_secondary']).pack(anchor='w')
        
        prompt_name_entry = ModernEntry(name_frame)
        prompt_name_entry.pack(fill='x', pady=(5, 0))
        
        # Prompt content
        content_frame = ModernFrame(editor_frame)
        content_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        content_frame.configure(style='Card.TFrame')
        
        tk.Label(content_frame, text="Prompt Template:",
                font=FONTS['body_medium'],
                fg=COLORS['text_primary'],
                bg=COLORS['bg_secondary']).pack(anchor='w')
        
        prompt_editor = scrolledtext.ScrolledText(
            content_frame,
            height=10,
            font=FONTS['mono'],
            bg=COLORS['bg_tertiary'],
            fg=COLORS['text_primary'],
            insertbackground=COLORS['text_accent'],
            borderwidth=0,
            relief='flat'
        )
        prompt_editor.pack(fill='both', expand=True, pady=(5, 0))
        
        # Buttons
        btn_frame = ModernFrame(editor_frame)
        btn_frame.pack(fill='x', padx=10, pady=(0, 10))
        btn_frame.configure(style='Card.TFrame')
        
        ModernButton(btn_frame, text="💾 Save Prompt", 
                    command=lambda: self.save_prompt_action(prompt_name_entry.get(), prompt_editor.get(1.0, 'end-1c'))).pack(side='left', padx=(0, 5))
        ModernButton(btn_frame, text="🚀 Use Prompt", 
                    command=lambda: self.use_prompt_action(prompt_editor.get(1.0, 'end-1c'), prompt_window)).pack(side='left', padx=(0, 5))
        ModernButton(btn_frame, text="❌ Close", 
                    command=prompt_window.destroy).pack(side='right')
    
    def save_prompt_action(self, name, content):
        """Save a prompt template"""
        if name and content:
            self.status_var.set(f"✅ Saved prompt: {name}")
            self.root.after(3000, lambda: self.status_var.set("🚀 AlphaMind Ready"))
        else:
            self.status_var.set("❌ Please enter name and content")
            self.root.after(3000, lambda: self.status_var.set("🚀 AlphaMind Ready"))
    
    def use_prompt_action(self, content, window):
        """Use a prompt template in live capture"""
        if content:
            self.live_text.delete(1.0, 'end')
            self.live_text.insert(1.0, content)
            window.destroy()
            self.status_var.set("✅ Prompt loaded to live capture")
            self.root.after(3000, lambda: self.status_var.set("🚀 AlphaMind Ready"))
        else:
            self.status_var.set("❌ No content to use")
            self.root.after(3000, lambda: self.status_var.set("🚀 AlphaMind Ready"))
    
    def start_llm_processing(self, text, is_chat=False):
        """Start LLM processing with animated loading indicator"""
        self.is_processing = True
        self.processing_symbols = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        self.processing_index = 0
        
        # Update status
        self.status_var.set("🤖 Processing with LLM...")
        
        # Start animation
        self.animate_processing()
        
        # Start processing in background thread
        processing_thread = threading.Thread(
            target=self.process_text_with_llm, 
            args=(text, is_chat), 
            daemon=True
        )
        processing_thread.start()
    
    def animate_processing(self):
        """Animate the processing indicator"""
        if self.is_processing:
            symbol = self.processing_symbols[self.processing_index]
            self.processing_status.set(f"{symbol} Processing...")
            self.processing_index = (self.processing_index + 1) % len(self.processing_symbols)
            # Continue animation every 100ms
            self.root.after(100, self.animate_processing)
    
    def process_text_with_llm(self, text, is_chat=False):
        """Simulate LLM processing (replace with actual LLM calls)"""
        import time
        
        # Simulate processing time
        time.sleep(2)  # Replace with actual LLM API call
        
        # Simulate response
        response = f"✨ Processed: {text[:50]}..." if len(text) > 50 else f"✨ Processed: {text}"
        
        # Update UI in main thread
        self.root.after(0, lambda: self.finish_llm_processing(response, is_chat))
    
    
    def finish_llm_processing(self, response, is_chat=False):
        """Finish LLM processing and update UI"""
        self.is_processing = False
        self.processing_status.set("")
        self.status_var.set("✅ Processing complete")
        
        if is_chat:
            # Add to chat conversation
            self.conversation_display.config(state='normal')
            self.conversation_display.insert('end', f"🤖 AI: {response}\n\n")
            self.conversation_display.config(state='disabled')
            self.conversation_display.see('end')
            # Clear message input
            self.message_entry.delete(1.0, 'end')
        else:
            # Replace text in live capture
            self.live_text.delete(1.0, 'end')
            self.live_text.insert(1.0, response)
        
        # Reset status after 3 seconds
        self.root.after(3000, lambda: self.status_var.set("🚀 AlphaMind Ready"))
        
    def run(self):
        """Start the application"""
        self.root.mainloop()

def main():
    """Main entry point"""
    print("🧠 Starting AlphaMind - Intelligent Prompt Hub...")
    app = PromptHubGUI()
    app.run()

if __name__ == "__main__":
    main()
