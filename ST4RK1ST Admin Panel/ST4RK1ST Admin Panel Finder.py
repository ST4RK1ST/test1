"""
ST4RK1ST Admin Panel Finder - Premium Cybersecurity Terminal Interface
Professional security operations center design with terminal aesthetics
"""

import os
import sys
import subprocess
import json
import re
import threading
import time
import queue
import webbrowser
import urllib.request
import urllib.parse
import socket
import ssl
from datetime import datetime
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, field
from pathlib import Path

# Auto-dependency installation
def check_and_install_dependencies():
    """Check and install required dependencies"""
    required = {
        'requests': 'requests',
        'tkinter': 'tk',
    }
    
    missing = []
    for module, package in required.items():
        try:
            if module == 'tkinter':
                import tkinter
            else:
                __import__(module)
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"Missing dependencies: {', '.join(missing)}")
        print("Installing required packages...")
        for package in missing:
            if package != 'tk':
                try:
                    subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                    print(f"✓ Installed {package}")
                except Exception as e:
                    print(f"✗ Failed to install {package}: {e}")
                    print(f"Please install manually: pip install {package}")
                    return False
    return True

# Check dependencies before proceeding
if not check_and_install_dependencies():
    input("Press Enter to exit...")
    sys.exit(1)

# Now import all required modules
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, font, filedialog
import ctypes
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import concurrent.futures


def set_window_icon(window):
    """Set custom window icon from rakib.ico file"""
    try:
        # Look for rakib.ico in multiple locations
        icon_paths = [
            r"C:\Users\bigbang\OneDrive\Desktop\main\m3u\rakib.ico",
            "rakib.ico",
            os.path.join(os.path.dirname(__file__), "rakib.ico"),
            os.path.join(os.getcwd(), "rakib.ico"),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "rakib.ico")
        ]
        
        icon_loaded = False
        for icon_path in icon_paths:
            try:
                if os.path.exists(icon_path):
                    # Set window icon
                    window.iconbitmap(icon_path)
                    icon_loaded = True
                    print(f"Custom icon loaded from: {icon_path}")
                    
                    # Also set for taskbar and Alt+Tab using Windows API
                    try:
                        hwnd = window.winfo_id()
                        # Load the icon from file
                        icon_handle = ctypes.windll.user32.LoadImageW(
                            0, icon_path, 1, 0, 0, 0x00000010 | 0x00002000
                        )
                        if icon_handle:
                            # Set both big and small icons
                            ctypes.windll.user32.SendMessageW(hwnd, 0x0080, 0, icon_handle)  # WM_SETICON
                            ctypes.windll.user32.SendMessageW(hwnd, 0x0080, 1, icon_handle)
                    except:
                        pass
                    break
            except Exception as e:
                continue
        
        if not icon_loaded:
            print("Warning: rakib.ico not found. Using default icon.")
            # Try to remove default Tkinter icon
            try:
                hwnd = window.winfo_id()
                # Remove default icon
                ctypes.windll.user32.SendMessageW(hwnd, 0x0080, 0, 0)
                ctypes.windll.user32.SendMessageW(hwnd, 0x0080, 1, 0)
                ctypes.windll.user32.SetClassLongW(hwnd, -14, 0)
            except:
                pass
            
    except Exception as e:
        print(f"Warning: Could not load custom icon: {e}")
        # Continue without icon


def load_icon_for_header():
    """Load icon for header logo - returns PhotoImage or None"""
    try:
        # Look for rakib.ico in multiple locations
        icon_paths = [
            r"C:\Users\bigbang\OneDrive\Desktop\main\m3u\rakib.ico",
            "rakib.ico",
            os.path.join(os.path.dirname(__file__), "rakib.ico"),
            os.path.join(os.getcwd(), "rakib.ico"),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "rakib.ico")
        ]
        
        for icon_path in icon_paths:
            try:
                if os.path.exists(icon_path):
                    # Load ICO file and convert to PhotoImage
                    from PIL import Image, ImageTk
                    img = Image.open(icon_path)
                    # Resize for header (32x32)
                    img = img.resize((32, 32), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    return photo
            except Exception:
                continue
    except Exception:
        pass
    return None


@dataclass
class ScanResult:
    """Data class for scan results"""
    url: str
    status_code: int
    title: str
    response_size: int
    response_time: float
    found: bool
    error: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)


class SettingsManager:
    """Manage application settings"""
    
    DEFAULT_SETTINGS = {
        'window_size': '1300x850',
        'max_threads': 30,
        'timeout': 5,
        'user_agent': 'RakibAdminPanelFinder/1.0',
        'follow_redirects': True,
        'verify_ssl': False,
        'save_history': True
    }
    
    def __init__(self):
        """Initialize settings manager"""
        self.config_dir = Path(os.getenv('APPDATA', os.path.expanduser('~'))) / 'RakibsAdminPanelFinder'
        self.config_file = self.config_dir / 'settings.json'
        self.settings = {}
        self.load()
    
    def load(self):
        """Load settings from file"""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.settings = json.load(f)
            else:
                self.settings = {}
            
            for key, value in self.DEFAULT_SETTINGS.items():
                if key not in self.settings:
                    self.settings[key] = value
            
            self.save()
        except Exception:
            self.settings = self.DEFAULT_SETTINGS.copy()
    
    def save(self):
        """Save settings to file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2)
        except Exception:
            pass
    
    def get(self, key, default=None):
        """Get a setting value"""
        return self.settings.get(key, default)
    
    def set(self, key, value):
        """Set a setting value"""
        self.settings[key] = value
        self.save()


class TerminalLogger:
    """Professional terminal-style logging with precise colors"""
    
    def __init__(self, text_widget):
        """Initialize terminal logger"""
        self.text_widget = text_widget
        
        # Configure terminal color tags
        self.text_widget.tag_configure('error', foreground='#FF5A5A')
        self.text_widget.tag_configure('success', foreground='#00FF66')
        self.text_widget.tag_configure('warning', foreground='#FFC107')
        self.text_widget.tag_configure('info', foreground='#CFCFCF')
        self.text_widget.tag_configure('scan', foreground='#7CFF7C')
        self.text_widget.tag_configure('system', foreground='#808080')
        self.text_widget.tag_configure('timestamp', foreground='#666666')
        self.text_widget.tag_configure('level', foreground='#808080')
        self.text_widget.tag_configure('default', foreground='#CFCFCF')
        
        # Configure font
        try:
            terminal_font = font.Font(family='Cascadia Code', size=9)
            self.text_widget.configure(font=terminal_font)
        except:
            try:
                terminal_font = font.Font(family='JetBrains Mono', size=9)
                self.text_widget.configure(font=terminal_font)
            except:
                terminal_font = font.Font(family='Consolas', size=9)
                self.text_widget.configure(font=terminal_font)
    
    def _format_message(self, message, level, tag):
        """Format message with timestamp and level"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        # Clear message with precise alignment
        self.text_widget.insert(tk.END, "[", 'timestamp')
        self.text_widget.insert(tk.END, timestamp, 'timestamp')
        self.text_widget.insert(tk.END, "] ", 'timestamp')
        
        # Level with exact padding
        level_padded = f"{level:<8}"
        self.text_widget.insert(tk.END, level_padded, 'level')
        
        # Message
        self.text_widget.insert(tk.END, message, tag)
        self.text_widget.insert(tk.END, "\n", 'default')
        
        self.text_widget.see(tk.END)
        self.text_widget.update_idletasks()
    
    def log(self, message, tag='default', level='INFO'):
        """Log a message to the terminal"""
        self._format_message(message, level, tag)
    
    def error(self, message):
        """Log error message"""
        self._format_message(message, 'ERROR', 'error')
    
    def success(self, message):
        """Log success message"""
        self._format_message(message, 'SUCCESS', 'success')
    
    def warning(self, message):
        """Log warning message"""
        self._format_message(message, 'WARNING', 'warning')
    
    def info(self, message):
        """Log info message"""
        self._format_message(message, 'INFO', 'info')
    
    def scan(self, message):
        """Log scan message"""
        self._format_message(message, 'SCAN', 'scan')
    
    def system(self, message):
        """Log system message"""
        self._format_message(message, 'SYSTEM', 'system')
    
    def clear(self):
        """Clear the terminal"""
        self.text_widget.delete('1.0', tk.END)


class ScanEngine:
    """Scan engine for web scanning"""
    
    # Common admin panel paths
    COMMON_PATHS = [
        '', 'admin', 'login', 'dashboard', 'panel', 'cpanel',
        'wp-admin', 'administrator', 'admincp', 'backend',
        'admin/login', 'admin/dashboard', 'admin/index',
        'administrator/login', 'administrator/dashboard',
        'cp', 'controlpanel', 'control-panel', 'adminpanel',
        'manage', 'management', 'system', 'config', 'setup',
        'install', 'admin/config', 'admin/setup', 'admin/install'
    ]
    
    def __init__(self, console_logger, progress_callback=None, status_callback=None):
        """Initialize scan engine"""
        self.console = console_logger
        self.progress_callback = progress_callback
        self.status_callback = status_callback
        self.is_running = False
        self.results = []
        self.scanned_urls = set()
        self.session = None
        self._setup_session()
    
    def _setup_session(self):
        """Setup requests session"""
        try:
            self.session = requests.Session()
            
            # Setup retry strategy
            retry_strategy = Retry(
                total=2,
                backoff_factor=0.5,
                status_forcelist=[429, 500, 502, 503, 504]
            )
            adapter = HTTPAdapter(max_retries=retry_strategy)
            self.session.mount('http://', adapter)
            self.session.mount('https://', adapter)
            
            # Set headers
            self.session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
        except Exception:
            self.session = None
    
    def _normalize_url(self, base_url, path):
        """Normalize URL"""
        base_url = base_url.rstrip('/')
        path = path.lstrip('/')
        return f"{base_url}/{path}"
    
    def _check_url(self, url):
        """Check a single URL"""
        if not self.is_running:
            return None
        
        try:
            start_time = time.time()
            
            # Make request
            response = self.session.get(
                url,
                timeout=5,
                verify=False,
                allow_redirects=True,
                stream=True
            )
            
            response_time = time.time() - start_time
            
            # Get content
            try:
                content = response.text[:5000]
            except:
                content = ''
            
            # Extract title
            title = self._extract_title(content)
            
            # Check if it's an admin panel
            is_admin = self._is_admin_panel(response, content)
            
            result = ScanResult(
                url=url,
                status_code=response.status_code,
                title=title[:50] if title else 'No title',
                response_size=len(response.content),
                response_time=response_time,
                found=is_admin
            )
            
            return result
            
        except requests.exceptions.Timeout:
            return ScanResult(
                url=url,
                status_code=0,
                title='Timeout',
                response_size=0,
                response_time=5.0,
                found=False,
                error='Timeout'
            )
        except requests.exceptions.ConnectionError:
            return ScanResult(
                url=url,
                status_code=0,
                title='Connection Error',
                response_size=0,
                response_time=0,
                found=False,
                error='Connection Error'
            )
        except Exception as e:
            return ScanResult(
                url=url,
                status_code=0,
                title='Error',
                response_size=0,
                response_time=0,
                found=False,
                error=str(e)[:50]
            )
    
    def _is_admin_panel(self, response, content):
        """Check if the page is an admin panel"""
        # Check status code
        if response.status_code not in [200, 302, 301, 303, 307]:
            return False
        
        # Check for admin indicators in URL
        url_lower = response.url.lower()
        admin_indicators = ['admin', 'login', 'dashboard', 'panel', 'control', 'manage', 'system', 'config']
        for indicator in admin_indicators:
            if indicator in url_lower:
                return True
        
        # Check for admin indicators in content
        content_lower = content.lower()
        admin_patterns = [
            'admin', 'login', 'username', 'password', 'dashboard',
            'panel', 'control', 'management', 'configuration',
            'user', 'account', 'signin', 'log in', 'log-in',
            'admin panel', 'control panel', 'administration'
        ]
        
        found_patterns = 0
        for pattern in admin_patterns:
            if pattern in content_lower:
                found_patterns += 1
        
        # If we find multiple indicators, it's likely an admin panel
        if found_patterns >= 3:
            return True
        
        # Check for login forms
        if '<form' in content_lower and ('password' in content_lower or 'login' in content_lower):
            return True
        
        return False
    
    def _extract_title(self, content):
        """Extract page title from HTML"""
        try:
            title_match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE | re.DOTALL)
            if title_match:
                return title_match.group(1).strip()
        except Exception:
            pass
        return None
    
    def scan_target(self, target_url, use_common_paths=True, custom_paths=None):
        """Scan a target"""
        self.is_running = True
        self.results = []
        self.scanned_urls = set()
        
        # Normalize target URL
        if not target_url.startswith('http://') and not target_url.startswith('https://'):
            target_url = 'http://' + target_url
        
        # Get paths to scan
        paths = []
        if custom_paths:
            paths = custom_paths.split(',')
            paths = [p.strip() for p in paths if p.strip()]
        elif use_common_paths:
            paths = self.COMMON_PATHS.copy()
        
        # Add root path
        if '' not in paths:
            paths.insert(0, '')
        
        total_urls = len(paths)
        scanned = 0
        
        self.console.info(f"Target: {target_url}")
        self.console.info(f"Queued {total_urls} paths for discovery")
        
        # Use thread pool for scanning
        max_workers = 30
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            
            for path in paths:
                if not self.is_running:
                    break
                
                url = self._normalize_url(target_url, path)
                if url in self.scanned_urls:
                    continue
                self.scanned_urls.add(url)
                
                future = executor.submit(self._check_url, url)
                futures.append(future)
                
                # Update progress
                if self.progress_callback:
                    self.progress_callback(scanned, total_urls, f"Scanning: {path}")
                if self.status_callback:
                    self.status_callback(f"Scanning: {path}")
            
            # Process results as they complete
            for future in concurrent.futures.as_completed(futures):
                if not self.is_running:
                    break
                
                result = future.result()
                if result:
                    self.results.append(result)
                    
                    if result.found:
                        self.console.success(f"Found admin panel: {result.url} [{result.status_code}]")
                    elif result.error:
                        self.console.warning(f"Failed: {result.url} - {result.error}")
                    else:
                        self.console.scan(f"Checked: {result.url} [{result.status_code}]")
                
                scanned += 1
                if self.progress_callback:
                    self.progress_callback(scanned, total_urls, f"Completed {scanned}/{total_urls}")
        
        self.is_running = False
        
        # Summary
        found_count = len([r for r in self.results if r.found])
        self.console.info(f"Scan completed. Found {found_count} admin panels")
        
        if self.status_callback:
            self.status_callback(f"Scan complete - Found {found_count}")
        
        return self.results
    
    def stop(self):
        """Stop the scan"""
        self.is_running = False
        self.console.warning("Scan terminated by user")


class RakibsAdminPanelFinderApp:
    """Main application class - Premium Cybersecurity Interface"""
    
    def __init__(self):
        """Initialize the application"""
        self.settings = SettingsManager()
        
        # Main window
        self.root = tk.Tk()
        self.root.title("ST4RK1ST Admin Panel Finder")
        self.root.geometry(self.settings.get('window_size', '1300x850'))
        self.root.minsize(1100, 750)
        self.root.configure(bg='#050505')
        
        # Set custom window icon from rakib.ico
        set_window_icon(self.root)
        
        # Setup DPI awareness
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            pass
        
        # Initialize variables
        self.scan_engine = None
        self.scan_thread = None
        self.is_scanning = False
        self.results = []
        self.current_target = None
        self.timer_start = None
        self.timer_id = None
        self.selection_count = 0
        
        # Apply premium terminal style
        self._apply_premium_style()
        
        # Setup UI
        self._setup_ui()
        
        # Setup keyboard shortcuts
        self._setup_shortcuts()
        
        # Setup context menu
        self._setup_context_menu()
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Setup terminal
        self.terminal = TerminalLogger(self.terminal_text)
        self.terminal.system("ST4RK1ST Admin Panel Finder v1.0")
        self.terminal.system("Terminal ready. Awaiting commands.")
    
    def _apply_premium_style(self):
        """Apply premium cybersecurity terminal styling"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Premium color palette
        self.colors = {
            'bg': '#050505',
            'bg2': '#0a0a0a',
            'bg3': '#111111',
            'bg4': '#161616',
            'fg': '#7CFF7C',
            'fg2': '#CFCFCF',
            'accent': '#00D9FF',
            'success': '#00FF66',
            'warning': '#FFC107',
            'error': '#FF5A5A',
            'border': '#1a1a1a',
            'hover': '#1a1a1a',
            'selected': '#0a1a0a'
        }
        
        self.root.configure(bg=self.colors['bg'])
        
        # Configure ttk styles
        style.configure('Terminal.TFrame', background=self.colors['bg'])
        style.configure('Terminal.TLabel', background=self.colors['bg'], 
                       foreground=self.colors['fg2'])
        style.configure('Terminal.TLabelframe', background=self.colors['bg'],
                       foreground=self.colors['fg'], relief='flat')
        style.configure('Terminal.TLabelframe.Label', background=self.colors['bg'],
                       foreground=self.colors['fg'])
        
        # Button styles
        style.configure('Terminal.TButton',
                       background=self.colors['bg3'],
                       foreground=self.colors['fg2'],
                       borderwidth=1,
                       focuscolor='none',
                       relief='flat',
                       padding=(16, 8))
        style.map('Terminal.TButton',
                 background=[('active', self.colors['hover'])],
                 foreground=[('active', self.colors['fg'])])
        
        # Accent button
        style.configure('Accent.TButton',
                       background='#002233',
                       foreground=self.colors['accent'],
                       borderwidth=1,
                       focuscolor='none',
                       relief='flat',
                       padding=(16, 8))
        style.map('Accent.TButton',
                 background=[('active', '#003344')],
                 foreground=[('active', '#66ddff')])
        
        # Danger button
        style.configure('Danger.TButton',
                       background='#220000',
                       foreground=self.colors['error'],
                       borderwidth=1,
                       focuscolor='none',
                       relief='flat',
                       padding=(16, 8))
        style.map('Danger.TButton',
                 background=[('active', '#330000')])
        
        # Entry styles
        style.configure('Terminal.TEntry',
                       fieldbackground=self.colors['bg2'],
                       foreground=self.colors['fg'],
                       bordercolor=self.colors['border'],
                       borderwidth=1,
                       padding=10)
        style.map('Terminal.TEntry',
                 fieldbackground=[('focus', self.colors['bg3'])],
                 bordercolor=[('focus', self.colors['accent'])])
        
        # Progressbar style
        style.configure('Terminal.Horizontal.TProgressbar',
                       background=self.colors['success'],
                       troughcolor=self.colors['bg2'],
                       borderwidth=0)
        
        # Scrollbar style
        style.configure('Terminal.Vertical.TScrollbar',
                       background=self.colors['bg2'],
                       troughcolor=self.colors['bg'],
                       bordercolor=self.colors['bg'],
                       arrowcolor=self.colors['fg2'],
                       borderwidth=0)
        
        # Treeview style
        style.configure('Terminal.Treeview',
                       background=self.colors['bg2'],
                       foreground=self.colors['fg2'],
                       fieldbackground=self.colors['bg2'],
                       borderwidth=0)
        style.map('Terminal.Treeview',
                 background=[('selected', self.colors['selected'])],
                 foreground=[('selected', self.colors['fg'])])
        
        # Combobox style
        style.configure('Terminal.TCombobox',
                       fieldbackground=self.colors['bg2'],
                       foreground=self.colors['fg'],
                       background=self.colors['bg2'],
                       arrowcolor=self.colors['fg2'],
                       padding=10)
        style.map('Terminal.TCombobox',
                 fieldbackground=[('readonly', self.colors['bg2'])])
    
    def _setup_ui(self):
        """Setup the complete UI with premium design"""
        # Main container
        self.main_container = ttk.Frame(self.root, style='Terminal.TFrame')
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Header
        self._create_header()
        
        # Content
        self._create_content()
        
        # Status bar
        self._create_statusbar()
    
    def _create_header(self):
        """Create the header with professional branding"""
        header = ttk.Frame(self.main_container, style='Terminal.TFrame', height=70)
        header.pack(fill=tk.X, padx=15, pady=(10, 5))
        header.pack_propagate(False)
        
        # Left section: Logo and title
        left_frame = ttk.Frame(header, style='Terminal.TFrame')
        left_frame.pack(side=tk.LEFT)
        
        # Load custom icon for header
        icon_photo = load_icon_for_header()
        
        if icon_photo:
            # Display custom icon
            icon_label = tk.Label(left_frame, image=icon_photo, 
                                 bg=self.colors['bg'])
            icon_label.image = icon_photo  # Keep reference
            icon_label.pack(side=tk.LEFT, padx=(0, 8))
        else:
            # No icon available - just add small spacing
            ttk.Frame(left_frame, width=32, style='Terminal.TFrame').pack(side=tk.LEFT, padx=(0, 8))
        
        # Title
        title_label = tk.Label(left_frame, text="ST4RK1ST Admin Panel Finder",
                              font=('Segoe UI', 16, 'bold'),
                              fg=self.colors['fg'], bg=self.colors['bg'])
        title_label.pack(side=tk.LEFT)
        
        # Subtitle
        subtitle_label = tk.Label(left_frame, text="— Cybersecurity Dashboard",
                                 font=('Segoe UI', 10),
                                 fg=self.colors['fg2'], bg=self.colors['bg'])
        subtitle_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Version
        version_label = tk.Label(left_frame, text="v1.0",
                                font=('Segoe UI', 9),
                                fg=self.colors['fg2'], bg=self.colors['bg'])
        version_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Spacer
        ttk.Frame(header, style='Terminal.TFrame').pack(side=tk.LEFT, expand=True)
        
        # Right section: About button
        self.btn_about = ttk.Button(header, text="ℹ  About",
                                   command=self.show_about, style='Terminal.TButton',
                                   width=10)
        self.btn_about.pack(side=tk.RIGHT, padx=2)
    
    def _create_content(self):
        """Create main content area"""
        content = ttk.Frame(self.main_container, style='Terminal.TFrame')
        content.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)
        
        # Control panel
        self._create_control_panel(content)
        
        # Results and terminal split
        split_frame = ttk.Frame(content, style='Terminal.TFrame')
        split_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Results panel
        results_frame = ttk.Frame(split_frame, style='Terminal.TFrame')
        results_frame.pack(fill=tk.BOTH, expand=True)
        self._create_results_panel(results_frame)
        
        # Terminal panel
        terminal_frame = ttk.Frame(split_frame, style='Terminal.TFrame')
        terminal_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        self._create_terminal_panel(terminal_frame)
    
    def _create_control_panel(self, parent):
        """Create control panel with scanner controls"""
        control_frame = ttk.LabelFrame(parent, text=" SCAN CONTROLS ",
                                      style='Terminal.TLabelframe')
        control_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Target input row
        target_row = ttk.Frame(control_frame, style='Terminal.TFrame')
        target_row.pack(fill=tk.X, pady=8, padx=12)
        
        target_label = tk.Label(target_row, text="TARGET",
                               font=('Segoe UI', 9, 'bold'),
                               fg=self.colors['fg2'], bg=self.colors['bg'])
        target_label.pack(side=tk.LEFT, padx=5)
        
        self.target_entry = ttk.Entry(target_row, style='Terminal.TEntry')
        self.target_entry.pack(side=tk.LEFT, padx=8, expand=True, fill=tk.X)
        self.target_entry.insert(0, "https://example.com")
        self.target_entry.bind('<Return>', lambda e: self.start_scan())
        
        # Options row
        options_row = ttk.Frame(control_frame, style='Terminal.TFrame')
        options_row.pack(fill=tk.X, pady=5, padx=12)
        
        self.use_common_paths_var = tk.BooleanVar(value=True)
        common_check = ttk.Checkbutton(options_row, text="COMMON PATHS",
                                      variable=self.use_common_paths_var,
                                      style='Terminal.TCheckbutton')
        common_check.pack(side=tk.LEFT, padx=5)
        
        custom_label = tk.Label(options_row, text="CUSTOM PATHS:",
                               font=('Segoe UI', 9),
                               fg=self.colors['fg2'], bg=self.colors['bg'])
        custom_label.pack(side=tk.LEFT, padx=(15, 5))
        
        self.custom_paths_entry = ttk.Entry(options_row, width=30,
                                           style='Terminal.TEntry')
        self.custom_paths_entry.pack(side=tk.LEFT, padx=5)
        self.custom_paths_entry.insert(0, "admin,login,dashboard,panel,auth,signin,signup,register,logout,signout,forgot-password,reset-password,profile,account,cpanel,controlpanel,manage,management,administrator,portal,workspace,console,system,backend,setup,install,users,user,members,roles,permissions,clients,customers,api,v1,v2,graphql,swagger,docs,db,database,phpmyadmin,server-status,metrics,health,settings,config,preferences,logs,audit,system-logs,backup,backups,home,about,contact,services,pricing,faq,help,search,blog,posts,news,uploads,images,assets,static,files,media,download,css,js,.git,.env,test,tests,staging,dev,development,tmp,temp,wp-admin,wp-login.php,xmlrpc.php,index,index.php,default,main,site,web,app,application,modules,plugins,themes,templates,views,controllers,models,components,inc,includes,lib,library,vendor,node_modules,src,public,private,hidden,secret,nginx,nginx.conf,nginx_status,nginx-status,stub_status,status,nginx.conf.bak,nginx.conf.old,nginx.conf.save,nginx.conf.swp,nginx.conf~,nginx.pid,logs,logs/access.log,logs/error.log,logs/nginx.log,access.log,error.log,conf.d,sites-available,sites-enabled,mime.types,fastcgi_params,scgi_params,uwsgi_params,fastcgi.conf,proxy.conf,etc/nginx,etc/nginx/nginx.conf,etc/nginx/conf.d,etc/nginx/sites-available,etc/nginx/sites-enabled,var/log/nginx,var/log/nginx/access.log,var/log/nginx/error.log,usr/local/nginx,usr/share/nginx,usr/share/nginx/html,50x.html,404.html,index.html,.htpasswd,.nginx.conf.swp,nginx.vh.default.conf")
        
        # Buttons row
        btn_row = ttk.Frame(control_frame, style='Terminal.TFrame')
        btn_row.pack(fill=tk.X, pady=8, padx=12)
        
        self.btn_start = ttk.Button(btn_row, text="▶  START SCAN",
                                   command=self.start_scan, style='Accent.TButton')
        self.btn_start.pack(side=tk.LEFT, padx=3)
        
        self.btn_stop = ttk.Button(btn_row, text="■  STOP",
                                   command=self.stop_scan, style='Danger.TButton')
        self.btn_stop.pack(side=tk.LEFT, padx=3)
        self.btn_stop.config(state=tk.DISABLED)
        
        self.btn_clear = ttk.Button(btn_row, text="✕  CLEAR ALL",
                                   command=self.clear_all, style='Terminal.TButton')
        self.btn_clear.pack(side=tk.LEFT, padx=3)
        
        # Progress row
        progress_row = ttk.Frame(control_frame, style='Terminal.TFrame')
        progress_row.pack(fill=tk.X, pady=5, padx=12)
        
        self.progress_bar = ttk.Progressbar(progress_row,
                                           style='Terminal.Horizontal.TProgressbar',
                                           length=400, mode='determinate')
        self.progress_bar.pack(fill=tk.X, pady=3)
        
        progress_info = ttk.Frame(progress_row, style='Terminal.TFrame')
        progress_info.pack(fill=tk.X)
        
        self.progress_label = tk.Label(progress_info,
                                      text="READY",
                                      font=('Segoe UI', 9, 'bold'),
                                      fg=self.colors['fg2'], bg=self.colors['bg'])
        self.progress_label.pack(side=tk.LEFT)
        
        self.timer_label = tk.Label(progress_info,
                                   text="⏱  00:00:00",
                                   font=('Segoe UI', 9),
                                   fg=self.colors['fg2'], bg=self.colors['bg'])
        self.timer_label.pack(side=tk.RIGHT)
    
    def _create_results_panel(self, parent):
        """Create results panel with professional table"""
        results_frame = ttk.LabelFrame(parent, text=" SCAN RESULTS ",
                                      style='Terminal.TLabelframe')
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        # Toolbar
        toolbar = ttk.Frame(results_frame, style='Terminal.TFrame')
        toolbar.pack(fill=tk.X, pady=5, padx=8)
        
        # Search
        search_label = tk.Label(toolbar, text="🔍",
                               fg=self.colors['fg2'], bg=self.colors['bg'])
        search_label.pack(side=tk.LEFT, padx=5)
        
        self.search_entry = ttk.Entry(toolbar, width=20, style='Terminal.TEntry')
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind('<KeyRelease>', self.filter_results)
        
        # Filter
        filter_label = tk.Label(toolbar, text="FILTER:",
                               fg=self.colors['fg2'], bg=self.colors['bg'])
        filter_label.pack(side=tk.LEFT, padx=(15, 5))
        
        self.filter_combo = ttk.Combobox(toolbar, values=['ALL', 'FOUND', 'NOT FOUND'],
                                        width=10, style='Terminal.TCombobox')
        self.filter_combo.pack(side=tk.LEFT, padx=5)
        self.filter_combo.set('ALL')
        self.filter_combo.bind('<<ComboboxSelected>>', self.filter_results)
        
        # Separator
        sep = ttk.Separator(toolbar, orient='vertical')
        sep.pack(side=tk.LEFT, padx=10, fill=tk.Y)
        
        # Action buttons
        self.btn_copy = ttk.Button(toolbar, text="COPY",
                                  command=self.copy_selected, style='Terminal.TButton')
        self.btn_copy.pack(side=tk.LEFT, padx=2)
        
        self.btn_copy_all = ttk.Button(toolbar, text="COPY ALL",
                                      command=self.copy_all, style='Terminal.TButton')
        self.btn_copy_all.pack(side=tk.LEFT, padx=2)
        
        self.btn_export_csv = ttk.Button(toolbar, text="CSV",
                                        command=self.export_csv, style='Terminal.TButton')
        self.btn_export_csv.pack(side=tk.LEFT, padx=2)
        
        self.btn_export_txt = ttk.Button(toolbar, text="TXT",
                                        command=self.export_txt, style='Terminal.TButton')
        self.btn_export_txt.pack(side=tk.LEFT, padx=2)
        
        self.btn_clear_results = ttk.Button(toolbar, text="CLEAR",
                                           command=self.clear_results, style='Danger.TButton')
        self.btn_clear_results.pack(side=tk.LEFT, padx=2)
        
        # Treeview
        tree_frame = ttk.Frame(results_frame, style='Terminal.TFrame')
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=5)
        
        columns = ('URL', 'Status', 'Title', 'Size', 'Time')
        self.results_tree = ttk.Treeview(tree_frame, columns=columns,
                                        show='headings', style='Terminal.Treeview',
                                        height=12)
        
        # Headings
        self.results_tree.heading('URL', text='URL', anchor='w')
        self.results_tree.heading('Status', text='STATUS', anchor='center')
        self.results_tree.heading('Title', text='TITLE', anchor='w')
        self.results_tree.heading('Size', text='SIZE', anchor='e')
        self.results_tree.heading('Time', text='TIME', anchor='e')
        
        # Columns
        self.results_tree.column('URL', width=400, minwidth=200)
        self.results_tree.column('Status', width=80, minwidth=60, anchor='center')
        self.results_tree.column('Title', width=250, minwidth=100)
        self.results_tree.column('Size', width=100, minwidth=60, anchor='e')
        self.results_tree.column('Time', width=80, minwidth=60, anchor='e')
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical',
                                 command=self.results_tree.yview,
                                 style='Terminal.Vertical.TScrollbar')
        self.results_tree.configure(yscrollcommand=scrollbar.set)
        
        self.results_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind events
        self.results_tree.bind('<Double-Button-1>', self.open_selected_url)
        self.results_tree.bind('<ButtonRelease-3>', self.show_context_menu)
        self.results_tree.bind('<<TreeviewSelect>>', self.on_selection_change)
    
    def _create_terminal_panel(self, parent):
        """Create terminal console panel"""
        terminal_frame = ttk.LabelFrame(parent, text=" TERMINAL ",
                                       style='Terminal.TLabelframe')
        terminal_frame.pack(fill=tk.BOTH, expand=True)
        
        # Terminal text widget
        self.terminal_text = tk.Text(terminal_frame,
                                    bg='#050505',
                                    fg='#CFCFCF',
                                    wrap=tk.WORD,
                                    relief=tk.FLAT,
                                    highlightthickness=0,
                                    padx=12,
                                    pady=8,
                                    spacing1=1,
                                    spacing2=0,
                                    spacing3=1)
        self.terminal_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Terminal scrollbar
        terminal_scroll = ttk.Scrollbar(terminal_frame, orient='vertical',
                                       command=self.terminal_text.yview,
                                       style='Terminal.Vertical.TScrollbar')
        terminal_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.terminal_text.config(yscrollcommand=terminal_scroll.set)
    
    def _create_statusbar(self):
        """Create status bar"""
        statusbar = ttk.Frame(self.main_container, style='Terminal.TFrame', height=28)
        statusbar.pack(fill=tk.X, side=tk.BOTTOM, padx=15, pady=(0, 8))
        statusbar.pack_propagate(False)
        
        # Status indicator
        self.status_indicator = tk.Label(statusbar, text="●",
                                        font=('Segoe UI', 11),
                                        fg=self.colors['success'],
                                        bg=self.colors['bg'])
        self.status_indicator.pack(side=tk.LEFT, padx=(0, 8))
        
        self.status_label = tk.Label(statusbar, text="READY",
                                    font=('Segoe UI', 9, 'bold'),
                                    fg=self.colors['fg2'], bg=self.colors['bg'])
        self.status_label.pack(side=tk.LEFT)
        
        # Separator
        sep1 = tk.Label(statusbar, text="|",
                       font=('Segoe UI', 9),
                       fg=self.colors['fg2'], bg=self.colors['bg'])
        sep1.pack(side=tk.LEFT, padx=12)
        
        # Results count
        self.results_count_label = tk.Label(statusbar, text="RESULTS: 0",
                                           font=('Segoe UI', 9),
                                           fg=self.colors['fg2'], bg=self.colors['bg'])
        self.results_count_label.pack(side=tk.LEFT)
        
        sep2 = tk.Label(statusbar, text="|",
                       font=('Segoe UI', 9),
                       fg=self.colors['fg2'], bg=self.colors['bg'])
        sep2.pack(side=tk.LEFT, padx=12)
        
        # Selection count
        self.selection_label = tk.Label(statusbar, text="SELECTED: 0",
                                       font=('Segoe UI', 9),
                                       fg=self.colors['fg2'], bg=self.colors['bg'])
        self.selection_label.pack(side=tk.LEFT)
        
        # Spacer
        ttk.Frame(statusbar, style='Terminal.TFrame').pack(side=tk.LEFT, expand=True)
        
        # Version
        version_info = tk.Label(statusbar, text="v1.0",
                               font=('Segoe UI', 9),
                               fg=self.colors['fg2'], bg=self.colors['bg'])
        version_info.pack(side=tk.RIGHT)
    
    def _setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        self.root.bind('<Control-s>', lambda e: self.start_scan())
        self.root.bind('<Control-S>', lambda e: self.start_scan())
        self.root.bind('<Control-c>', lambda e: self.copy_selected())
        self.root.bind('<Control-C>', lambda e: self.copy_selected())
        self.root.bind('<Control-a>', lambda e: self.select_all())
        self.root.bind('<Control-A>', lambda e: self.select_all())
        self.root.bind('<Control-q>', lambda e: self.on_close())
        self.root.bind('<Control-Q>', lambda e: self.on_close())
        self.root.bind('<Escape>', lambda e: self.stop_scan())
        self.root.bind('<F5>', lambda e: self.start_scan())
    
    def _setup_context_menu(self):
        """Setup right-click context menu"""
        self.context_menu = tk.Menu(self.root, tearoff=0,
                                   bg='#0a0a0a', fg='#CFCFCF',
                                   activebackground='#1a1a1a',
                                   activeforeground='#7CFF7C',
                                   relief='flat')
        self.context_menu.add_command(label="Copy URL", command=self.copy_selected)
        self.context_menu.add_command(label="Copy All URLs", command=self.copy_all)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Open in Browser", command=self.open_selected_url)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Select All", command=self.select_all)
        self.context_menu.add_command(label="Clear Results", command=self.clear_results)
    
    def show_context_menu(self, event):
        """Show context menu"""
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()
    
    def on_selection_change(self, event):
        """Handle selection change in results tree"""
        selection = self.results_tree.selection()
        self.selection_count = len(selection)
        self.selection_label.config(text=f"SELECTED: {self.selection_count}")
    
    def start_scan(self):
        """Start the scanning process"""
        if self.is_scanning:
            return
        
        target = self.target_entry.get().strip()
        if not target:
            self.terminal.error("No target URL specified")
            return
        
        # Validate URL
        if not target.startswith('http://') and not target.startswith('https://'):
            target = 'http://' + target
        
        # Clear previous results
        self.clear_results()
        
        # Start scan
        self.is_scanning = True
        self.btn_start.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.NORMAL)
        self.progress_bar['value'] = 0
        self.progress_label.config(text="INITIALIZING")
        self.status_label.config(text="SCANNING")
        self.status_indicator.config(fg=self.colors['warning'])
        
        # Start timer
        self.timer_start = time.time()
        self._update_timer()
        
        # Get options
        use_common = self.use_common_paths_var.get()
        custom_paths = self.custom_paths_entry.get().strip()
        
        self.terminal.info(f"Target: {target}")
        if use_common:
            self.terminal.info("Using common paths")
        if custom_paths:
            self.terminal.info(f"Custom paths: {custom_paths}")
        
        # Create scan engine
        self.scan_engine = ScanEngine(
            self.terminal,
            progress_callback=self.update_progress,
            status_callback=self.update_status
        )
        
        # Start scan in background thread
        self.scan_thread = threading.Thread(
            target=self._run_scan,
            args=(target, use_common, custom_paths),
            daemon=True
        )
        self.scan_thread.start()
    
    def _run_scan(self, target, use_common, custom_paths):
        """Run the scan in background"""
        try:
            results = self.scan_engine.scan_target(
                target,
                use_common_paths=use_common,
                custom_paths=custom_paths if custom_paths else None
            )
            
            # Update results
            self.results = results
            
            # Update UI on main thread
            self.root.after(0, self._on_scan_complete)
            
        except Exception as e:
            self.root.after(0, lambda: self.terminal.error(f"Scan error: {e}"))
            self.root.after(0, self._on_scan_complete)
    
    def _on_scan_complete(self):
        """Handle scan completion"""
        self.is_scanning = False
        self.btn_start.config(state=tk.NORMAL)
        self.btn_stop.config(state=tk.DISABLED)
        self.status_label.config(text="READY")
        self.status_indicator.config(fg=self.colors['success'])
        
        # Stop timer
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None
        
        # Update results
        self.update_results_display()
        self.results_count_label.config(text=f"RESULTS: {len(self.results)}")
        
        # Save to history
        self.save_to_history()
    
    def update_progress(self, current, total, message):
        """Update progress bar"""
        def _update():
            if total > 0:
                progress = (current / total) * 100
                self.progress_bar['value'] = progress
                self.progress_label.config(text=message.upper())
            else:
                self.progress_bar['value'] = 0
                self.progress_label.config(text=message.upper())
        
        self.root.after(0, _update)
    
    def update_status(self, status):
        """Update status message"""
        def _update():
            self.status_label.config(text=status.upper())
        
        self.root.after(0, _update)
    
    def _update_timer(self):
        """Update the timer display"""
        if self.is_scanning and self.timer_start:
            elapsed = time.time() - self.timer_start
            hours = int(elapsed // 3600)
            minutes = int((elapsed % 3600) // 60)
            seconds = int(elapsed % 60)
            
            self.timer_label.config(text=f"⏱  {hours:02d}:{minutes:02d}:{seconds:02d}")
            self.timer_id = self.root.after(1000, self._update_timer)
        else:
            if self.timer_id:
                self.root.after_cancel(self.timer_id)
                self.timer_id = None
    
    def stop_scan(self):
        """Stop the current scan"""
        if self.scan_engine:
            self.scan_engine.stop()
        self.is_scanning = False
        self.btn_start.config(state=tk.NORMAL)
        self.btn_stop.config(state=tk.DISABLED)
        self.status_label.config(text="STOPPED")
        self.status_indicator.config(fg=self.colors['error'])
        self.terminal.warning("Scan terminated by user")
    
    def clear_results(self):
        """Clear results from treeview"""
        self.results_tree.delete(*self.results_tree.get_children())
        self.results_count_label.config(text="RESULTS: 0")
        self.terminal.info("Results cleared")
    
    def clear_all(self):
        """Clear all data"""
        self.clear_results()
        self.results = []
        self.progress_bar['value'] = 0
        self.progress_label.config(text="READY")
        self.timer_label.config(text="⏱  00:00:00")
        self.terminal.clear()
        self.terminal.system("System cleared")
        self.terminal.system("Ready for new scan")
    
    def update_results_display(self):
        """Update the results treeview"""
        self.results_tree.delete(*self.results_tree.get_children())
        
        for result in self.results:
            status_text = str(result.status_code) if result.status_code > 0 else "ERR"
            
            tags = ()
            if result.found:
                if 200 <= result.status_code < 400:
                    tags = ('success',)
                elif 400 <= result.status_code < 500:
                    tags = ('warning',)
                elif result.status_code >= 500:
                    tags = ('error',)
            else:
                tags = ('error',)
            
            self.results_tree.insert('', 'end', values=(
                result.url[:200],
                status_text,
                result.title[:50],
                result.response_size,
                f"{result.response_time:.2f}"
            ), tags=tags)
        
        self.results_tree.tag_configure('success', background='#001a00')
        self.results_tree.tag_configure('warning', background='#1a1a00')
        self.results_tree.tag_configure('error', background='#1a0000')
    
    def filter_results(self, event=None):
        """Filter results based on search and filter criteria"""
        search_text = self.search_entry.get().lower()
        filter_value = self.filter_combo.get()
        
        self.results_tree.delete(*self.results_tree.get_children())
        
        for result in self.results:
            if filter_value == 'FOUND' and not result.found:
                continue
            if filter_value == 'NOT FOUND' and result.found:
                continue
            
            if search_text and search_text not in result.url.lower():
                continue
            
            status_text = str(result.status_code) if result.status_code > 0 else "ERR"
            
            tags = ()
            if result.found:
                tags = ('found',)
            
            self.results_tree.insert('', 'end', values=(
                result.url[:200],
                status_text,
                result.title[:50],
                result.response_size,
                f"{result.response_time:.2f}"
            ), tags=tags)
    
    def copy_selected(self):
        """Copy selected result to clipboard"""
        selection = self.results_tree.selection()
        if not selection:
            self.terminal.warning("No items selected")
            return
        
        items = []
        for item in selection:
            values = self.results_tree.item(item)['values']
            if values:
                items.append(values[0])
        
        if items:
            text = '\n'.join(items)
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            self.terminal.success(f"Copied {len(items)} URL(s)")
    
    def copy_all(self):
        """Copy all results to clipboard"""
        if not self.results:
            self.terminal.warning("No results to copy")
            return
        
        items = [f"{r.url}" for r in self.results]
        text = '\n'.join(items)
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.terminal.success(f"Copied {len(items)} URL(s)")
    
    def select_all(self):
        """Select all items in treeview"""
        self.results_tree.selection_set(self.results_tree.get_children())
        self.terminal.info(f"Selected {len(self.results_tree.selection())} items")
    
    def open_selected_url(self, event=None):
        """Open selected URL in browser"""
        selection = self.results_tree.selection()
        if not selection:
            self.terminal.warning("No item selected")
            return
        
        item = self.results_tree.item(selection[0])
        values = item['values']
        if values:
            url = values[0]
            try:
                webbrowser.open(url)
                self.terminal.info(f"Opened: {url}")
            except Exception as e:
                self.terminal.error(f"Failed to open URL: {e}")
    
    def export_csv(self):
        """Export results to CSV"""
        if not self.results:
            self.terminal.warning("No results to export")
            return
        
        try:
            filepath = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv")]
            )
            
            if not filepath:
                return
            
            import csv
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['URL', 'Status', 'Title', 'Size', 'Time', 'Found'])
                for r in self.results:
                    writer.writerow([
                        r.url, r.status_code, r.title,
                        r.response_size, f"{r.response_time:.2f}",
                        'Yes' if r.found else 'No'
                    ])
            
            self.terminal.success(f"Exported: {filepath}")
            
        except Exception as e:
            self.terminal.error(f"Export failed: {e}")
    
    def export_txt(self):
        """Export results to TXT"""
        if not self.results:
            self.terminal.warning("No results to export")
            return
        
        try:
            filepath = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt")]
            )
            
            if not filepath:
                return
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write("ST4RK1ST ADMIN PANEL FINDER - SCAN RESULTS\n")
                f.write("=" * 80 + "\n\n")
                
                for i, r in enumerate(self.results, 1):
                    f.write(f"[{i}] URL: {r.url}\n")
                    f.write(f"    Status: {r.status_code}\n")
                    f.write(f"    Title: {r.title}\n")
                    f.write(f"    Size: {r.response_size} bytes\n")
                    f.write(f"    Time: {r.response_time:.2f}s\n")
                    f.write(f"    Found: {'Yes' if r.found else 'No'}\n")
                    f.write("-" * 80 + "\n\n")
            
            self.terminal.success(f"Exported: {filepath}")
            
        except Exception as e:
            self.terminal.error(f"Export failed: {e}")
    
    def save_to_history(self):
        """Save current scan to history"""
        if not self.results:
            return
        
        history_file = self.settings.config_dir / 'history.json'
        try:
            history = []
            if history_file.exists():
                with open(history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            
            entry = {
                'timestamp': datetime.now().isoformat(),
                'target': self.target_entry.get(),
                'total_urls': len(self.results),
                'found': len([r for r in self.results if r.found])
            }
            
            history.append(entry)
            
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(history[-100:], f, indent=2)
            
        except Exception:
            pass
    
    def show_about(self):
        """Show about dialog"""
        about_text = """
        ST4RK1ST Admin Panel Finder v1.0
        
        Professional web scanning tool for discovering
        admin panels and web interfaces on target domains.
        
        Features:
        • Multi-threaded scanning
        • Common admin path discovery
        • Real-time progress tracking
        • Detailed results with filtering
        • Export to CSV/TXT
        • Copy to clipboard
        • Live terminal console
        • Premium cybersecurity interface
        
        Built with Python 3 and Tkinter
        
        © 2024 ST4RK1ST Admin Panel Finder
        """
        messagebox.showinfo("About", about_text)
    
    def on_close(self):
        """Handle application close"""
        if self.is_scanning:
            if self.scan_engine:
                self.scan_engine.stop()
            if self.scan_thread and self.scan_thread.is_alive():
                self.scan_thread.join(timeout=2.0)
        
        # Save settings
        self.settings.set('window_size', self.root.geometry())
        self.settings.save()
        
        self.root.destroy()
    
    def run(self):
        """Run the application"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.on_close()
        except Exception as e:
            print(f"Application error: {e}")
            self.on_close()


def main():
    """Main entry point"""
    try:
        # Ensure requests is installed
        try:
            import requests
        except ImportError:
            print("Installing requests...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
            print("Installation complete. Starting application...")
        
        # Run application
        app = RakibsAdminPanelFinderApp()
        app.run()
        
    except Exception as e:
        print(f"Error: {e}")
        input("Press Enter to exit...")
        sys.exit(1)


if __name__ == "__main__":
    main()