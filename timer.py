import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import time
from datetime import datetime, timedelta

class TimeNotificationApp:
    def __init__(self):
        # Main Window Setup
        self.main_window = tk.Tk()
        self.main_window.title("⏱️ TimeNotifier Pro")
        self.main_window.geometry("400x300")
        self.main_window.resizable(False, False)
        self.main_window.configure(bg='#2d2d2d')
        
        # Custom Styles
        self.setup_styles()
        
        # Header Frame
        header_frame = ttk.Frame(self.main_window, style='Dark.TFrame')
        header_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(
            header_frame,
            text="TIMENOTIFIER PRO",
            style='Header.TLabel'
        ).pack(pady=5)
        
        # Main Content Frame
        content_frame = ttk.Frame(self.main_window, style='Dark.TFrame')
        content_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Progress Bar
        self.progress = ttk.Progressbar(
            content_frame,
            orient='horizontal',
            length=300,
            mode='determinate',
            style='Custom.Horizontal.TProgressbar'
        )
        self.progress.pack(pady=15)
        
        # Time Display
        self.time_label = ttk.Label(
            content_frame,
            text="00:00",
            style='TimeDisplay.TLabel'
        )
        self.time_label.pack(pady=5)
        
        # Status Display
        self.status_label = ttk.Label(
            content_frame,
            text="Ready",
            style='Status.TLabel'
        )
        self.status_label.pack(pady=5)
        
        # Button Frame
        button_frame = ttk.Frame(content_frame, style='Dark.TFrame')
        button_frame.pack(pady=15)
        
        # Buttons
        self.start_btn = ttk.Button(
            button_frame,
            text="▶ Start 30s Timer",
            command=self.start_default_timer,
            style='Accent.TButton'
        )
        self.start_btn.pack(side='left', padx=5)
        
        self.manual_btn = ttk.Button(
            button_frame,
            text="⚙ Manual Setup",
            command=self.manual_time_setup,
            style='Secondary.TButton'
        )
        self.manual_btn.pack(side='left', padx=5)
        
        # Timer state
        self.notification_time = None
        self.timer_running = False
        self.check_schedule()
        
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Dark Theme Colors
        bg_color = '#2d2d2d'
        fg_color = '#ffffff'
        accent_color = '#4e8cff'
        secondary_color = '#6c757d'
        progress_color = '#4e8cff'
        
        # Configure Styles
        style.configure('Dark.TFrame', background=bg_color)
        style.configure('Header.TLabel', 
                       background=bg_color,
                       foreground=accent_color,
                       font=('Segoe UI', 14, 'bold'))
        
        style.configure('TimeDisplay.TLabel',
                       background=bg_color,
                       foreground=fg_color,
                       font=('Segoe UI', 24, 'bold'))
        
        style.configure('Status.TLabel',
                       background=bg_color,
                       foreground=secondary_color,
                       font=('Segoe UI', 10))
        
        style.configure('Accent.TButton',
                       background=accent_color,
                       foreground=fg_color,
                       font=('Segoe UI', 10, 'bold'),
                       borderwidth=0,
                       focusthickness=0,
                       focuscolor='none',
                       padding=8)
        
        style.map('Accent.TButton',
                 background=[('active', '#3a7bf0'), ('pressed', '#2c5fc9')])
        
        style.configure('Secondary.TButton',
                       background=secondary_color,
                       foreground=fg_color,
                       font=('Segoe UI', 10),
                       borderwidth=0,
                       padding=8)
        
        style.map('Secondary.TButton',
                 background=[('active', '#5a6268'), ('pressed', '#4a5258')])
        
        style.configure('Custom.Horizontal.TProgressbar',
                       thickness=15,
                       troughcolor='#3d3d3d',
                       background=progress_color,
                       lightcolor=progress_color,
                       darkcolor=progress_color,
                       bordercolor='#3d3d3d')
        
    def start_default_timer(self):
        """Start the default 30-second timer"""
        self.notification_time = datetime.now() + timedelta(seconds=30)
        self.timer_running = True
        self.update_display()
        
    def manual_time_setup(self):
        # PIN verification
        pin = simpledialog.askstring("PIN Verification", "Enter your PIN:", show='*')
        if pin != "062100!":
            messagebox.showerror("Access Denied", "Incorrect PIN!")
            return
            
        # Get time increment
        multiplier = simpledialog.askinteger(
            "Set Custom Timer", 
            "Enter number of 25-minute blocks:",
            minvalue=1,
            maxvalue=100
        )
        
        if multiplier:
            minutes_to_add = 25 * multiplier
            self.notification_time = datetime.now() + timedelta(minutes=minutes_to_add)
            self.timer_running = True
            self.update_display()
    
    def update_display(self):
        if self.timer_running and self.notification_time:
            remaining = self.notification_time - datetime.now()
            total_seconds = max(0, remaining.total_seconds())
            
            # Update progress bar
            if hasattr(self, 'total_duration'):
                progress_value = (total_seconds / self.total_duration) * 100
                self.progress['value'] = progress_value
            
            # Update time display
            minutes, seconds = divmod(int(total_seconds), 60)
            self.time_label.config(text=f"{minutes:02d}:{seconds:02d}")
            
            # Update status
            if total_seconds > 10:
                self.status_label.config(text="Timer running...")
            elif total_seconds > 0:
                self.status_label.config(text="Almost done!", foreground='#ff9800')
            else:
                self.status_label.config(text="TIME'S UP!", foreground='#ff5252')
                self.timer_running = False
                self.show_notification("TIME'S UP!", '#ff5252', 3000)
        else:
            self.time_label.config(text="00:00")
            self.status_label.config(text="Ready", foreground='#6c757d')
            self.progress['value'] = 0
    
    def check_schedule(self):
        if self.timer_running and self.notification_time:
            # Calculate total duration on first run
            if not hasattr(self, 'total_duration'):
                self.total_duration = (self.notification_time - datetime.now()).total_seconds()
            
            remaining = (self.notification_time - datetime.now()).total_seconds()
            
            # Show 10-second warning
            if 9.9 < remaining <= 10.1 and not hasattr(self, 'warning_shown'):
                self.show_notification("10 SECONDS LEFT!", '#ff9800', 5000)
                self.warning_shown = True
            
            # Reset flags when timer is restarted
            if remaining > 10:
                if hasattr(self, 'warning_shown'):
                    del self.warning_shown
        
        self.update_display()
        self.main_window.after(100, self.check_schedule)
    
    def show_notification(self, message, bg_color, display_time):
        notif = tk.Toplevel()
        notif.overrideredirect(True)
        notif.attributes('-topmost', True)
        notif.attributes('-alpha', 0.0)
        notif.attributes('-transparentcolor', 'grey15')
        notif.configure(bg='grey15')
        
        # Shadow effect
        shadow = tk.Frame(notif, bg='black')
        shadow.pack(padx=5, pady=5)
        
        # Main notification frame
        main_frame = tk.Frame(
            shadow,
            bg=bg_color,
            padx=20,
            pady=15,
            highlightthickness=0
        )
        main_frame.pack()
        
        # Notification content
        tk.Label(
            main_frame,
            text=message,
            bg=bg_color,
            fg='white',
            font=('Segoe UI', 14, 'bold')
        ).pack()
        
        # Position at top-right
        screen_width = notif.winfo_screenwidth()
        window_width = 250
        x_position = screen_width - window_width - 20
        
        notif.geometry(f"+{x_position}+20")
        
        # Fade in animation
        for i in range(0, 11):
            alpha = i/10
            notif.attributes('-alpha', alpha)
            notif.update()
            time.sleep(0.02)
        
        # Auto-close after specified time
        notif.after(display_time, lambda: self.fade_out(notif))
    
    def fade_out(self, window):
        for i in range(10, -1, -1):
            alpha = i/10
            window.attributes('-alpha', alpha)
            window.update()
            time.sleep(0.02)
        window.destroy()
    
    def run(self):
        self.main_window.mainloop()

if __name__ == "__main__":
    app = TimeNotificationApp()
    app.run()
