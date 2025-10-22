#!/usr/bin/env python3
"""Expandable Clipper - Klein menu dat uitklapt naar groot"""
import warnings
warnings.filterwarnings("ignore", category=UserWarning)
import tkinter as tk
from tkinter import ttk, simpledialog
import subprocess
import requests

API_BASE = "http://localhost:8081"
API_TOKEN = "devtoken123"  # Set to empty string "" if no auth needed

def get_active_browser_tab():
    """Get active browser tab - tries Chrome, Brave, Safari, Arc"""
    # First try to get from any running browser, not just frontmost app
    browsers = [
        ("Google Chrome", "Chrome"),
        ("Brave Browser", "Brave Browser"),
        ("Safari", "Safari"),
        ("Arc", "Arc"),
        ("ChatGPT Atlas", "Atlas")
    ]
    
    for app_name, display_name in browsers:
        try:
            if "Safari" in app_name:
                script = f'''
                tell application "{app_name}"
                    if it is running then
                        if (count of windows) > 0 then
                            return URL of current tab of front window & "|" & name of current tab of front window
                        end if
                    end if
                end tell
                return "No|"
                '''
            elif "Safari" in app_name:
                script = f'''
                tell application "{app_name}"
                    if it is running then
                        if (count of windows) > 0 then
                            return URL of current tab of front window & "|" & name of current tab of front window
                        end if
                    end if
                end tell
                return "No|"
                '''
            else:
                script = f'''
                tell application "{app_name}"
                    if it is running then
                        if (count of windows) > 0 then
                            return URL of active tab of front window & "|" & title of active tab of front window
                        end if
                    end if
                end tell
                return "No|"
                '''
            
            result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True, timeout=2)
            if result.returncode == 0 and '|' in result.stdout:
                output = result.stdout.strip()
                if output != "No|" and output != "|":
                    url, title = output.split('|', 1)
                    if url and url != "No":
                        return url, title
        except:
            continue
    
    return None, None

class ExpandableClipper(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CLIPPER")
        self.configure(bg='#1a1a1a')
        self.attributes('-topmost', True)
        self.overrideredirect(True)
        
        # Sizes
        self.compact_width = 280
        self.compact_height = 140
        self.expanded_width = 340
        self.expanded_height = 240
        
        screen_width = self.winfo_screenwidth()
        self.geometry(f"{self.compact_width}x{self.compact_height}+{screen_width-300}+20")
        
        self.bind('<Button-1>', self.start_move)
        self.bind('<B1-Motion>', self.on_move)
        
        self.is_expanded = False
        self.current_url = None
        self.current_title = None
        self.category_var = tk.StringVar()
        self.categories = []
        
        self.build_ui()
        self.update_active_tab()
        self.load_categories()
    
    def start_move(self, event):
        self.x = event.x
        self.y = event.y
    
    def on_move(self, event):
        x = self.winfo_x() + event.x - self.x
        y = self.winfo_y() + event.y - self.y
        self.geometry(f"+{x}+{y}")
    
    def build_ui(self):
        self.main = tk.Frame(self, bg='#1a1a1a', padx=12, pady=10)
        self.main.pack(fill='both', expand=True)
        
        # Header
        header = tk.Frame(self.main, bg='#667eea', height=32)
        header.pack(fill='x', pady=(0, 10))
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text="📌 Clipper",
            font=('Helvetica', 11, 'bold'),
            fg='#ffffff',
            bg='#667eea'
        ).pack(side='left', padx=8, expand=True, anchor='w')
        
        # Expand/collapse button
        self.expand_btn = tk.Frame(header, bg='#5568d3', width=24, height=24, cursor='hand2')
        self.expand_btn.pack(side='right', padx=2, pady=4)
        self.expand_btn.pack_propagate(False)
        self.expand_btn.bind('<Button-1>', lambda e: self.toggle_expand())
        self.expand_label = tk.Label(self.expand_btn, text="⬇", bg='#5568d3', fg='white', font=('Helvetica', 10, 'bold'), cursor='hand2')
        self.expand_label.pack(expand=True)
        self.expand_label.bind('<Button-1>', lambda e: self.toggle_expand())
        
        close_btn = tk.Frame(header, bg='#cc0000', width=24, height=24, cursor='hand2')
        close_btn.pack(side='right', padx=2, pady=4)
        close_btn.pack_propagate(False)
        close_btn.bind('<Button-1>', lambda e: self.quit())
        tk.Label(close_btn, text="✕", bg='#cc0000', fg='white', font=('Helvetica', 10, 'bold'), cursor='hand2').pack(expand=True)
        
        # Tab info - always visible
        tab_frame = tk.Frame(self.main, bg='#2a2a2a', height=40)
        tab_frame.pack(fill='x', pady=(0, 8))
        tab_frame.pack_propagate(False)
        
        tk.Label(
            tab_frame,
            text="🌐",
            font=('Helvetica', 10),
            fg='#888888',
            bg='#2a2a2a'
        ).pack(side='left', padx=(8, 4))
        
        self.url_label = tk.Label(
            tab_frame,
            text="Detecting...",
            font=('Helvetica', 9),
            fg='#ffffff',
            bg='#2a2a2a',
            anchor='w',
            wraplength=220,
            justify='left'
        )
        self.url_label.pack(side='left', fill='both', expand=True, padx=(0, 8), pady=6)
        
        # SEND TO DATABASE - always visible
        self.clip_frame = tk.Frame(self.main, bg='#22c55e', height=42, cursor='hand2')
        self.clip_frame.pack(fill='x')
        self.clip_frame.pack_propagate(False)
        self.clip_frame.bind('<Button-1>', lambda e: self.clip_current())
        
        self.clip_label = tk.Label(
            self.clip_frame,
            text="🚀 SEND TO DATABASE",
            font=('Helvetica', 11, 'bold'),
            fg='#ffffff',
            bg='#22c55e',
            cursor='hand2'
        )
        self.clip_label.pack(expand=True)
        self.clip_label.bind('<Button-1>', lambda e: self.clip_current())
        
        # EXPANDED SECTION - hidden by default
        self.expanded_frame = tk.Frame(self.main, bg='#1a1a1a')
        
        # Category
        cat_frame = tk.Frame(self.expanded_frame, bg='#1a1a1a', height=28)
        cat_frame.pack(fill='x', pady=(8, 6))
        cat_frame.pack_propagate(False)
        
        tk.Label(
            cat_frame,
            text="Category:",
            font=('Helvetica', 9),
            fg='#888888',
            bg='#1a1a1a'
        ).pack(side='left', padx=(0, 6))
        
        self.category_combo = ttk.Combobox(
            cat_frame,
            textvariable=self.category_var,
            font=('Helvetica', 9),
            state='readonly',
            width=18
        )
        self.category_combo.pack(side='left', fill='x', expand=True)
        
        plus_frame = tk.Frame(cat_frame, bg='#3a3a3a', width=24, height=24, cursor='hand2')
        plus_frame.pack(side='right', padx=(6, 0))
        plus_frame.pack_propagate(False)
        plus_frame.bind('<Button-1>', lambda e: self.new_category())
        tk.Label(plus_frame, text="+", bg='#3a3a3a', fg='white', font=('Helvetica', 10, 'bold'), cursor='hand2').pack(expand=True)
        
        # Tags input
        tags_label = tk.Label(
            self.expanded_frame,
            text="Tags (comma separated):",
            font=('Helvetica', 9),
            fg='#888888',
            bg='#1a1a1a',
            anchor='w'
        )
        tags_label.pack(fill='x', pady=(0, 4))
        
        tags_input_frame = tk.Frame(self.expanded_frame, bg='#2a2a2a', height=28)
        tags_input_frame.pack(fill='x', pady=(0, 6))
        tags_input_frame.pack_propagate(False)
        
        self.tags_var = tk.StringVar()
        self.tags_entry = tk.Entry(
            tags_input_frame,
            textvariable=self.tags_var,
            font=('Helvetica', 9),
            bg='#2a2a2a',
            fg='#ffffff',
            insertbackground='#ffffff',
            relief='flat',
            bd=0
        )
        self.tags_entry.pack(fill='both', expand=True, padx=8, pady=4)
        
        # Refresh button
        refresh_frame = tk.Frame(self.expanded_frame, bg='#3a3a3a', height=28, cursor='hand2')
        refresh_frame.pack(fill='x')
        refresh_frame.pack_propagate(False)
        refresh_frame.bind('<Button-1>', lambda e: self.force_refresh())
        
        tk.Label(
            refresh_frame,
            text="🔄 Refresh Tab",
            font=('Helvetica', 9),
            fg='#ffffff',
            bg='#3a3a3a',
            cursor='hand2'
        ).pack(expand=True)
    
    def toggle_expand(self):
        if self.is_expanded:
            # Collapse
            self.expanded_frame.pack_forget()
            self.geometry(f"{self.compact_width}x{self.compact_height}")
            self.expand_label.config(text="⬇")
            self.is_expanded = False
        else:
            # Expand
            self.expanded_frame.pack(fill='x', pady=(8, 0))
            self.geometry(f"{self.expanded_width}x{self.expanded_height}")
            self.expand_label.config(text="⬆")
            self.is_expanded = True
    
    def update_active_tab(self):
        url, title = get_active_browser_tab()
        if url and url != "No":
            self.current_url = url
            self.current_title = title
            
            short_title = title[:30] + "..." if len(title) > 30 else title
            short_url = url[:35] + "..." if len(url) > 35 else url
            
            self.url_label.config(text=f"{short_title}\n{short_url}", fg='#22c55e')
            self.clip_label.config(text="🚀 SEND TO DATABASE")
        else:
            self.current_url = None
            self.current_title = None
            self.url_label.config(text="No active browser", fg='#ef4444')
            self.clip_label.config(text="⏸️ NO TAB")
        
        self.after(2000, self.update_active_tab)
    
    def force_refresh(self):
        url, title = get_active_browser_tab()
        if url and url != "No":
            self.current_url = url
            self.current_title = title
            short_title = title[:30] + "..." if len(title) > 30 else title
            short_url = url[:35] + "..." if len(url) > 35 else url
            self.url_label.config(text=f"{short_title}\n{short_url}", fg='#22c55e')
    
    def load_categories(self):
        try:
            headers = {}
            if API_TOKEN:
                headers["Authorization"] = f"Bearer {API_TOKEN}"
            r = requests.get(f"{API_BASE}/categories", headers=headers, timeout=5)
            r.raise_for_status()
            self.categories = [cat['name'] for cat in r.json().get('categories', [])]
            self.category_combo['values'] = self.categories
            if self.categories:
                self.category_var.set(self.categories[0])
        except:
            pass
    
    def new_category(self):
        name = simpledialog.askstring("New Category", "Category name:", parent=self)
        if name:
            try:
                headers = {}
                if API_TOKEN:
                    headers["Authorization"] = f"Bearer {API_TOKEN}"
                r = requests.post(f"{API_BASE}/categories", headers=headers, json={"name": name}, timeout=5)
                r.raise_for_status()
                self.load_categories()
                self.category_var.set(name)
            except:
                pass
    
    def clip_current(self):
        if not self.current_url:
            self.clip_label.config(text="⚠️ NO TAB")
            self.after(1000, lambda: self.clip_label.config(text="🚀 SEND TO DATABASE"))
            return
        
        # Disable button during send
        self.clip_frame.unbind('<Button-1>')
        self.clip_label.unbind('<Button-1>')
        self.clip_label.config(text="⏳ SENDING...")
        self.update()  # Force UI update
        
        # Get tags if expanded
        tags = []
        if self.is_expanded and self.tags_var.get():
            tags = [t.strip() for t in self.tags_var.get().split(',') if t.strip()]
        
        try:
            headers = {}
            if API_TOKEN:
                headers["Authorization"] = f"Bearer {API_TOKEN}"
            r = requests.post(
                f"{API_BASE}/capture",
                headers=headers,
                json={
                    "url": self.current_url,
                    "title": self.current_title,
                    "category": self.category_var.get() or None,
                    "tags": tags
                },
                timeout=10
            )
            r.raise_for_status()
            result = r.json()
            
            # Immediate SENT feedback
            self.clip_frame.config(bg='#3b82f6')
            self.clip_label.config(bg='#3b82f6', text="📤 SENT!")
            if self.is_expanded:
                self.tags_var.set("")
            
            # Then show SAVED with ID
            self.after(600, lambda: self.clip_frame.config(bg='#10b981'))
            self.after(600, lambda: self.clip_label.config(bg='#10b981', text=f"✅ SAVED! ID: {result.get('id', '?')}"))
            
            # Flash effect
            self.after(1200, lambda: self.clip_frame.config(bg='#22c55e'))
            self.after(1200, lambda: self.clip_label.config(bg='#22c55e'))
            self.after(1400, lambda: self.clip_frame.config(bg='#10b981'))
            self.after(1400, lambda: self.clip_label.config(bg='#10b981'))
            self.after(1600, lambda: self.clip_frame.config(bg='#22c55e'))
            self.after(1600, lambda: self.clip_label.config(bg='#22c55e'))
            
            # Reset after 3 seconds
            self.after(3000, self._reset_clip_button)
            
        except Exception as e:
            # Error feedback
            self.clip_frame.config(bg='#ef4444')
            self.clip_label.config(bg='#ef4444', text=f"❌ ERROR: {str(e)[:20]}")
            self.after(2500, self._reset_clip_button)
    
    def _reset_clip_button(self):
        """Reset clip button to normal state"""
        self.clip_frame.config(bg='#22c55e')
        self.clip_label.config(bg='#22c55e', text="🚀 SEND TO DATABASE")
        self.clip_frame.bind('<Button-1>', lambda e: self.clip_current())
        self.clip_label.bind('<Button-1>', lambda e: self.clip_current())

if __name__ == "__main__":
    app = ExpandableClipper()
    app.mainloop()
