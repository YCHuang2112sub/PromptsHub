"""
Floating Command Window - Modern Modular Architecture
Main application entry point with modular tab system
"""

import tkinter as tk
from tkinter import ttk, messagebox
import queue
import threading
import time
import os
import sys

# Add the lib directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'lib'))

# Import our modules
from data_manager import DataManager
from config_manager import ConfigManager
from text_capture import TextCaptureTab
from commands import CommandsTab
from screen_parse import ScreenParseTab
from text_history import TextHistoryTab


class FloatingCommandWindow:
    """Main application class with modular architecture"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Floating Command Window")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Initialize data management
        self.data_manager = DataManager()
        self.config_manager = ConfigManager(self.data_manager, self.root)
        
        # GUI queue for thread communication
        self.gui_queue = queue.Queue()
        
        # Tab references for cleanup
        self.tabs = {}
        
        # Setup UI
        self.setup_ui()
        self.apply_window_settings()
        
        # Start GUI queue processor
        self.process_gui_queue()
    
    def setup_ui(self):
        """Setup the main user interface"""
        # Create menu bar
        self.create_menu()
        
        # Create main container with padding
        main_container = ttk.Frame(self.root)
        main_container.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill='both', expand=True)
        
        # Initialize all tabs
        self.init_tabs()
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_bar = ttk.Label(main_container, textvariable=self.status_var, 
                                   relief=tk.SUNKEN, anchor='w')
        self.status_bar.pack(fill='x', pady=(5, 0))
    
    def create_menu(self):
        """Create application menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Export History...", command=self.export_history)
        file_menu.add_command(label="Import Commands...", command=self.import_commands)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Clear All History", command=self.clear_all_data)
        edit_menu.add_command(label="Settings...", command=self.config_manager.show_config_dialog)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_checkbutton(label="Always on Top", command=self.toggle_always_on_top)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Keyboard Shortcuts", command=self.show_shortcuts)
        help_menu.add_command(label="About", command=self.show_about)
    
    def init_tabs(self):
        """Initialize all application tabs"""
        try:
            # Text Capture Tab
            self.tabs['text_capture'] = TextCaptureTab(
                self.notebook, self.gui_queue, self.data_manager
            )
            
            # Commands Tab  
            self.tabs['commands'] = CommandsTab(
                self.notebook, self.gui_queue, self.data_manager
            )
            
            # Screen Parse Tab
            self.tabs['screen_parse'] = ScreenParseTab(
                self.notebook, self.gui_queue, self.data_manager
            )
            
            # Text History Tab
            self.tabs['text_history'] = TextHistoryTab(
                self.notebook, self.gui_queue, self.data_manager
            )
            
            # Select first tab
            self.notebook.select(0)
            
        except Exception as e:
            messagebox.showerror("Initialization Error", 
                               f"Failed to initialize tabs:\n{str(e)}")
            self.root.destroy()
    
    def apply_window_settings(self):
        """Apply saved window settings"""
        settings = self.config_manager.get_window_settings()
        
        try:
            self.root.geometry(settings['geometry'])
        except Exception:
            self.root.geometry("600x800+100+100")
        
        if settings['always_on_top']:
            self.root.attributes('-topmost', True)
    
    def process_gui_queue(self):
        """Process messages from background threads"""
        try:
            while not self.gui_queue.empty():
                message_type, data = self.gui_queue.get_nowait()
                
                if message_type == 'capture':
                    # Handle text capture from clipboard monitor
                    self.tabs['text_capture'].display_captured_text(data)
                    # Also add to history tab display
                    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
                    self.tabs['text_history'].add_to_history_display(data, timestamp)
                    self.status_var.set(f"Captured {len(data)} characters")
                
                elif message_type == 'command_output':
                    # Handle command execution output
                    output, success = data
                    if 'commands' in self.tabs:
                        self.tabs['commands'].update_command_output(output, success)
                
                elif message_type == 'parsed_text':
                    # Handle parsed text from OCR/LLM
                    text, source, metadata = data
                    self.data_manager.add_parsed_text_to_history(text, source, metadata)
                    if 'text_history' in self.tabs:
                        self.tabs['text_history'].refresh_history()
                    self.status_var.set(f"Parsed {len(text)} characters from {source}")
                
                elif message_type == 'status':
                    # Handle status updates
                    self.status_var.set(data)
                
                elif message_type == 'error':
                    # Handle error messages
                    messagebox.showerror("Error", data)
                    self.status_var.set("Error occurred")
                
        except queue.Empty:
            pass
        except Exception as e:
            print(f"GUI queue processing error: {e}")
        
        # Schedule next check
        self.root.after(100, self.process_gui_queue)
    
    def toggle_always_on_top(self):
        """Toggle always on top setting"""
        current = self.root.attributes('-topmost')
        new_value = not current
        self.root.attributes('-topmost', new_value)
        self.config_manager.save_window_settings(self.root.geometry(), new_value)
        
        status = "enabled" if new_value else "disabled"
        self.status_var.set(f"Always on top {status}")
    
    def export_history(self):
        """Export text history to file"""
        if 'text_history' in self.tabs:
            self.tabs['text_history'].export_history()
    
    def import_commands(self):
        """Import commands from file"""
        from tkinter import filedialog
        
        filename = filedialog.askopenfilename(
            title="Import Commands",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                import json
                with open(filename, 'r', encoding='utf-8') as f:
                    commands = json.load(f)
                
                imported = 0
                for name, data in commands.items():
                    if isinstance(data, dict) and 'command' in data:
                        if self.data_manager.add_command(name, data['command']):
                            imported += 1
                    elif isinstance(data, str):
                        if self.data_manager.add_command(name, data):
                            imported += 1
                
                if 'commands' in self.tabs:
                    self.tabs['commands'].refresh_commands_list()
                
                messagebox.showinfo("Import Complete", 
                                  f"Successfully imported {imported} commands")
                
            except Exception as e:
                messagebox.showerror("Import Error", 
                                   f"Failed to import commands:\n{str(e)}")
    
    def clear_all_data(self):
        """Clear all application data"""
        if messagebox.askyesno("Clear All Data", 
                              "This will permanently delete:\n" +
                              "• All captured text history\n" +
                              "• All saved commands\n" +
                              "• All screenshots\n\n" +
                              "This action cannot be undone. Continue?"):
            
            try:
                # Clear history
                self.data_manager.clear_all_history()
                
                # Clear commands
                self.data_manager.commands = {}
                self.data_manager._save_commands()
                
                # Clean up screenshots
                self.data_manager.cleanup_old_screenshots(0)  # Remove all
                
                # Refresh all tabs
                for tab in self.tabs.values():
                    if hasattr(tab, 'refresh_history'):
                        tab.refresh_history()
                    if hasattr(tab, 'refresh_commands_list'):
                        tab.refresh_commands_list()
                
                messagebox.showinfo("Clear Complete", "All data has been cleared")
                self.status_var.set("All data cleared")
                
            except Exception as e:
                messagebox.showerror("Clear Error", 
                                   f"Failed to clear data:\n{str(e)}")
    
    def show_shortcuts(self):
        """Show keyboard shortcuts help"""
        shortcuts = """Keyboard Shortcuts:

Text Capture:
• Ctrl+C - Capture selected text (when monitor is active)

Commands:
• Double-click - Copy command to clipboard
• Enter - Execute selected command

Screen Parse:
• Drag to select area on screenshot
• Right-click - Context menu options

Text History:
• Ctrl+F - Search text (when implemented)
• Select text + Copy - Copy to clipboard

General:
• Ctrl+T - Toggle always on top
• F1 - Show this help
"""
        messagebox.showinfo("Keyboard Shortcuts", shortcuts)
    
    def show_about(self):
        """Show about dialog"""
        about_text = """Floating Command Window v2.0

A modern productivity tool for:
• Text capture and management
• Command storage and execution  
• Screen parsing with OCR and LLM
• Comprehensive text history

Built with modular architecture for reliability and extensibility.

© 2024 - Modern Python GUI Application"""
        
        messagebox.showinfo("About", about_text)
    
    def on_closing(self):
        """Handle application closing"""
        try:
            # Save window geometry
            geometry = self.root.geometry()
            always_on_top = self.root.attributes('-topmost')
            self.config_manager.save_window_settings(geometry, always_on_top)
            
            # Cleanup tabs
            for tab in self.tabs.values():
                if hasattr(tab, 'cleanup'):
                    tab.cleanup()
            
            # Clean up old screenshots
            self.data_manager.cleanup_old_screenshots()
            
        except Exception as e:
            print(f"Cleanup error: {e}")
        
        self.root.quit()
        self.root.destroy()
    
    def run(self):
        """Start the application"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.on_closing()


def main():
    """Main entry point"""
    try:
        app = FloatingCommandWindow()
        app.run()
    except Exception as e:
        print(f"Application startup error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()