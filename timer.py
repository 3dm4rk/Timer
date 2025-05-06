import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
from datetime import datetime, timedelta
import pygame
from pygame import mixer
import os
import sys
import keyboard
import time
import atexit

class FullscreenTimerApp:
    def __init__(self):
        # Initialize pygame mixer
        pygame.init()
        mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        atexit.register(self.cleanup)
        
        # Main Window Setup
        self.main_window = tk.Tk()
        self.main_window.title("⏱️ Timer")
        self.set_fullscreen(True)
        self.main_window.configure(bg='black')
        self.main_window.protocol("WM_DELETE_WINDOW", self.prevent_close)
        self.main_window.resizable(False, False)
        
        # Block keyboard shortcuts
        self.setup_keyboard_blocking()
        
        # Load sound files
        self.setup_sounds()
        
        # Timer state
        self.notification_time = None
        self.timer_running = False
        self.sound_enabled = True
        self.current_warning_window = None
        self.is_fullscreen = True
        self.sound_playing = False
        self.active_notifications = []
        self.five_min_warning_played = False
        self.timeout_sound_played = False
        self.total_duration = 0
        self.timeout_shown = False
        
        # UI Setup
        self.setup_ui()
        
        # Start checking the timer
        self.check_schedule()

    def show_notification(self, message, bg_color='#ff9800', display_time=5000):
        """Show a notification popup"""
        notif = tk.Toplevel(self.main_window)
        notif.overrideredirect(True)
        notif.attributes('-topmost', True)
        notif.attributes('-alpha', 0.0)
        notif.configure(bg='grey15')
        
        screen_width = self.main_window.winfo_screenwidth()
        notif.geometry(f"+{screen_width-320}+20")
        
        shadow = tk.Frame(notif, bg='black')
        shadow.pack(padx=5, pady=5)
        
        main_frame = tk.Frame(
            shadow,
            bg=bg_color,
            padx=20,
            pady=15,
            highlightthickness=0
        )
        main_frame.pack()
        
        tk.Label(
            main_frame,
            text=message,
            bg=bg_color,
            fg='white',
            font=('Segoe UI', 14, 'bold')
        ).pack()
        
        for i in range(0, 11):
            alpha = i/10
            notif.attributes('-alpha', alpha)
            notif.update()
            time.sleep(0.02)
        
        self.active_notifications.append(notif)
        notif.after(display_time, lambda: self.fade_out_notification(notif))

    def fade_out_notification(self, notification):
        """Fade out notification"""
        if notification.winfo_exists():
            for i in range(10, -1, -1):
                alpha = i/10
                notification.attributes('-alpha', alpha)
                notification.update()
                time.sleep(0.02)
            notification.destroy()
            if notification in self.active_notifications:
                self.active_notifications.remove(notification)

    def cleanup(self):
        """Cleanup resources"""
        try:
            for notif in self.active_notifications[:]:
                if notif.winfo_exists():
                    notif.destroy()
            mixer.quit()
            pygame.quit()
            keyboard.unhook_all()
        except Exception as e:
            print(f"Cleanup error: {e}")

    def setup_ui(self):
        """Initialize UI components"""
        content_frame = tk.Frame(self.main_window, bg='black')
        content_frame.pack(expand=True, fill='both')
        
        # Time Display
        self.time_label = tk.Label(
            content_frame,
            text="00:00",
            fg='white',
            bg='black',
            font=('Arial', 80, 'bold')
        )
        self.time_label.pack(expand=True, pady=(20, 10))
        
        # Status Display
        self.status_label = tk.Label(
            content_frame,
            text="Ready",
            fg='#6c757d',
            bg='black',
            font=('Arial', 18)
        )
        self.status_label.pack(pady=5)
        
        # Button Frame
        self.button_frame = tk.Frame(content_frame, bg='black')
        self.button_frame.pack(pady=10)
        
        # Add Time Button
        self.add_time_btn = tk.Button(
            self.button_frame,
            text="➕ Add Time",
            command=self.verify_pin_for_add_time,
            bg='#4CAF50',
            fg='white',
            font=('Arial', 12, 'bold'),
            padx=15,
            pady=8
        )
        self.add_time_btn.pack(side='left', padx=5)
        
        # Extend Time Button
        self.extend_time_btn = tk.Button(
            self.button_frame,
            text="⏱ Extend Time",
            command=self.verify_pin_for_add_time,
            bg='#2196F3',
            fg='white',
            font=('Arial', 12, 'bold'),
            padx=15,
            pady=8
        )
        
        # Reset Time Button
        self.reset_btn = tk.Button(
            self.button_frame,
            text="🔄 Reset",
            command=self.reset_timer,
            bg='#ff9800',
            fg='white',
            font=('Arial', 12, 'bold'),
            padx=15,
            pady=8
        )
        self.reset_btn.pack(side='left', padx=5)
        
        # Settings Button
        self.settings_btn = tk.Button(
            self.button_frame,
            text="⚙ Settings",
            command=self.verify_pin_for_settings,
            bg='#6c757d',
            fg='white',
            font=('Arial', 12, 'bold'),
            padx=15,
            pady=8
        )
        self.settings_btn.pack(side='left', padx=5)

    def set_fullscreen(self, fullscreen):
        """Toggle fullscreen mode"""
        self.is_fullscreen = fullscreen
        self.main_window.attributes('-fullscreen', fullscreen)
        self.main_window.attributes('-topmost', fullscreen)
        if not fullscreen:
            self.main_window.geometry("400x300")

    def setup_keyboard_blocking(self):
        """Block keyboard shortcuts"""
        try:
            keyboard.block_key('windows')
            keyboard.block_key('windows left')
            keyboard.block_key('windows right')
            keyboard.add_hotkey('alt+tab', lambda: None, suppress=True)
            keyboard.add_hotkey('ctrl+esc', lambda: None, suppress=True)
            keyboard.add_hotkey('alt+f4', lambda: None, suppress=True)
        except Exception as e:
            print(f"Keyboard blocking error: {e}")

    def setup_sounds(self):
        """Load sound files"""
        try:
            base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
            warning_path = os.path.join(base_path, "warning.mp3")
            timeout_path = os.path.join(base_path, "timeout.mp3")
            
            self.warning_sound = warning_path if os.path.exists(warning_path) else None
            self.timeout_sound = timeout_path if os.path.exists(timeout_path) else None
            
        except Exception as e:
            print(f"Sound setup error: {e}")
            self.warning_sound = None
            self.timeout_sound = None

    def play_sound(self, sound_type):
        """Play sounds"""
        if not self.sound_enabled or self.sound_playing:
            return
            
        try:
            sound_file = self.warning_sound if sound_type == "warning" else self.timeout_sound
            if sound_file:
                self.sound_playing = True
                mixer.music.stop()
                mixer.music.load(sound_file)
                mixer.music.play()
                sound = mixer.Sound(sound_file)
                self.main_window.after(int(sound.get_length() * 1000), self.reset_sound_flag)
        except Exception as e:
            print(f"Sound error: {e}")
            self.sound_playing = False

    def reset_sound_flag(self):
        """Reset sound flag"""
        self.sound_playing = False

    def prevent_close(self):
        """Prevent closing"""
        pass

    def reset_timer(self):
        """Reset timer"""
        confirm = messagebox.askyesno(
            "Confirm Reset", 
            "Are you sure you want to reset your time to 0?",
            parent=self.main_window
        )
        if confirm:
            self.notification_time = None
            self.timer_running = False
            self.five_min_warning_played = False
            self.timeout_sound_played = False
            self.timeout_shown = False
            self.update_display()
            self.status_label.config(text="Timer Reset", fg='#ff9800')
            self.main_window.after(2000, lambda: self.status_label.config(
                text="Ready", 
                fg='#6c757d'
            ))

    def verify_pin_for_add_time(self):
        """Verify PIN for adding time"""
        pin = simpledialog.askstring(
            "PIN Verification", 
            "Enter PIN to add time:",
            parent=self.main_window,
            show='*'
        )
        if pin == "062100!":
            self.show_time_options()
        else:
            messagebox.showerror("Access Denied", "Incorrect PIN!", parent=self.main_window)
    
    def show_time_options(self):
        """Show time options"""
        time_menu = tk.Toplevel(self.main_window)
        time_menu.title("Add Time")
        time_menu.geometry("300x200")
        time_menu.resizable(False, False)
        time_menu.configure(bg='#2d2d2d')
        time_menu.attributes('-topmost', True)
        time_menu.grab_set()
        
        tk.Label(
            time_menu,
            text="ADD TIME OPTIONS",
            fg='white',
            bg='#2d2d2d',
            font=('Arial', 14, 'bold')
        ).pack(pady=10)
        
        btn_frame = tk.Frame(time_menu, bg='#2d2d2d')
        btn_frame.pack(pady=10)
        
        tk.Button(
            btn_frame,
            text="Custom Minutes",
            command=lambda: [self.add_custom_minutes(), time_menu.destroy()],
            bg='#4CAF50',
            fg='white',
            font=('Arial', 12),
            width=15
        ).pack(pady=5)
        
        tk.Button(
            btn_frame,
            text="Custom Seconds",
            command=lambda: [self.add_custom_seconds(), time_menu.destroy()],
            bg='#2196F3',
            fg='white',
            font=('Arial', 12),
            width=15
        ).pack(pady=5)
        
        tk.Button(
            btn_frame,
            text="Cancel",
            command=time_menu.destroy,
            bg='#f44336',
            fg='white',
            font=('Arial', 12),
            width=15
        ).pack(pady=5)

    def add_custom_minutes(self):
        """Add minutes"""
        minutes = simpledialog.askinteger(
            "Add Minutes", 
            "Enter minutes to add:",
            parent=self.main_window,
            minvalue=1,
            maxvalue=1000
        )
        if minutes:
            self.add_time(minutes * 60)

    def add_custom_seconds(self):
        """Add seconds"""
        seconds = simpledialog.askinteger(
            "Add Seconds", 
            "Enter seconds to add:",
            parent=self.main_window,
            minvalue=1,
            maxvalue=3600
        )
        if seconds:
            self.add_time(seconds)

    def add_time(self, seconds_to_add):
        """Add time to timer"""
        if self.timer_running and self.notification_time:
            self.notification_time += timedelta(seconds=seconds_to_add)
            self.total_duration += seconds_to_add
        else:
            self.notification_time = datetime.now() + timedelta(seconds=seconds_to_add)
            self.total_duration = seconds_to_add
            self.timer_running = True
        
        self.five_min_warning_played = False
        self.timeout_sound_played = False
        self.timeout_shown = False
        
        if self.is_fullscreen:
            self.set_fullscreen(False)
        
        self.update_display()
        
        mins, secs = divmod(seconds_to_add, 60)
        time_str = f"{mins} minutes" if mins > 0 else f"{secs} seconds"
        
        self.status_label.config(text=f"Added {time_str}", fg='#4CAF50')
        self.main_window.after(2000, lambda: self.status_label.config(
            text="Timer running...", 
            fg='#6c757d'
        ) if self.timer_running else None)

    def verify_pin_for_settings(self):
        """Verify PIN for settings"""
        pin = simpledialog.askstring(
            "PIN Verification", 
            "Enter your PIN:",
            parent=self.main_window,
            show='*'
        )
        if pin == "062100!":
            self.show_settings_menu()
        else:
            messagebox.showerror("Access Denied", "Incorrect PIN!", parent=self.main_window)
    
    def show_settings_menu(self):
        """Show settings menu"""
        settings_menu = tk.Toplevel(self.main_window)
        settings_menu.title("Settings")
        settings_menu.geometry("250x200")
        settings_menu.resizable(False, False)
        settings_menu.configure(bg='#2d2d2d')
        settings_menu.attributes('-topmost', True)
        settings_menu.grab_set()
        
        tk.Label(
            settings_menu,
            text="SETTINGS",
            fg='white',
            bg='#2d2d2d',
            font=('Arial', 14, 'bold')
        ).pack(pady=10)
        
        options_frame = tk.Frame(settings_menu, bg='#2d2d2d')
        options_frame.pack(pady=10)
        
        sound_text = "🔊 Disable Sound" if self.sound_enabled else "🔇 Enable Sound"
        tk.Button(
            options_frame,
            text=sound_text,
            command=lambda: [self.toggle_sound(), settings_menu.destroy()],
            bg='#6c757d',
            fg='white',
            font=('Arial', 12),
            width=20
        ).pack(pady=5)
        
        fs_text = "⬜ Windowed Mode" if self.is_fullscreen else "🟩 Fullscreen Mode"
        tk.Button(
            options_frame,
            text=fs_text,
            command=lambda: [self.toggle_fullscreen(), settings_menu.destroy()],
            bg='#6c757d',
            fg='white',
            font=('Arial', 12),
            width=20
        ).pack(pady=5)
        
        tk.Button(
            options_frame,
            text="Close",
            command=settings_menu.destroy,
            bg='#f44336',
            fg='white',
            font=('Arial', 12),
            width=20
        ).pack(pady=5)

    def toggle_fullscreen(self):
        """Toggle fullscreen"""
        self.set_fullscreen(not self.is_fullscreen)

    def toggle_sound(self):
        """Toggle sound"""
        self.sound_enabled = not self.sound_enabled
        if not self.sound_enabled:
            mixer.music.stop()

    def check_schedule(self):
        """Check timer schedule"""
        if self.timer_running and self.notification_time:
            remaining = (self.notification_time - datetime.now()).total_seconds()
            
            if 299 < remaining <= 300 and not self.five_min_warning_played:
                self.play_sound("warning")
                self.show_notification("5 MINUTES REMAINING!", bg_color='#ff9800')
                self.five_min_warning_played = True
                
            if remaining <= 0:
                if not self.timeout_sound_played:
                    self.play_sound("timeout")
                    self.show_notification("TIME'S UP!", bg_color='#ff5252')
                    self.timeout_sound_played = True
                
                if not self.timeout_shown:
                    self.timer_running = False
                    self.timeout_shown = True
                    self.show_shutdown_warning()
        
        self.update_display()
        self.main_window.after(100, self.check_schedule)

    def update_display(self):
        """Update timer display"""
        if self.timer_running and self.notification_time:
            remaining = self.notification_time - datetime.now()
            total_seconds = max(0, remaining.total_seconds())
            
            minutes, seconds = divmod(int(total_seconds), 60)
            self.time_label.config(text=f"{minutes:02d}:{seconds:02d}")
            
            if total_seconds > 300:
                self.status_label.config(text="Timer running...", fg='#6c757d')
                if self.current_warning_window:
                    self.current_warning_window.destroy()
                    self.current_warning_window = None
                
                if not self.extend_time_btn.winfo_ismapped():
                    self.extend_time_btn.pack(side='left', padx=5)
            elif total_seconds > 0:
                self.status_label.config(text="Almost done!", fg='#ff9800')
            else:
                self.status_label.config(text="TIME'S UP!", fg='#ff5252')
        else:
            self.time_label.config(text="00:00")
            self.status_label.config(text="Ready", fg='#6c757d')
            
            if self.extend_time_btn.winfo_ismapped():
                self.extend_time_btn.pack_forget()

    def show_shutdown_warning(self):
        """Show shutdown warning"""
        if self.current_warning_window and self.current_warning_window.winfo_exists():
            return
            
        self.set_fullscreen(True)
        
        warning = tk.Toplevel(self.main_window)
        self.current_warning_window = warning
        warning.attributes('-fullscreen', True)
        warning.configure(bg='black')
        warning.attributes('-topmost', True)
        warning.grab_set()
        
        warning.protocol("WM_DELETE_WINDOW", lambda: None)
        warning.bind('<Alt-F4>', lambda e: "break")
        warning.bind('<Escape>', lambda e: "break")
        warning.bind('<Control-q>', lambda e: "break")
        
        tk.Label(
            warning,
            text="TIME'S UP!",
            fg='white',
            bg='black',
            font=('Arial', 48, 'bold')
        ).pack(pady=50)
        
        tk.Label(
            warning,
            text="Please add more time to continue",
            fg='white',
            bg='black',
            font=('Arial', 24)
        ).pack(pady=20)
        
        countdown_label = tk.Label(
            warning,
            text="This computer will shutdown after 30 seconds",
            fg='red',
            bg='black',
            font=('Arial', 18, 'bold')
        )
        countdown_label.pack(pady=30)
        
        tk.Button(
            warning,
            text="➕ Add Time (1-30 minutes)",
            command=lambda: self.verify_pin_for_add_time_warning(warning),
            bg='#4CAF50',
            fg='white',
            font=('Arial', 18, 'bold'),
            padx=20,
            pady=10
        ).pack(pady=20)
        
        self.shutdown_countdown(30, warning, countdown_label)
    
    def verify_pin_for_add_time_warning(self, warning_window):
        """Verify PIN from warning"""
        pin = simpledialog.askstring(
            "PIN Verification", 
            "Enter PIN to add time:",
            parent=warning_window,
            show='*'
        )
        if pin == "062100!":
            self.add_time_from_warning(warning_window)
        else:
            messagebox.showerror("Access Denied", "Incorrect PIN!", parent=warning_window)
    
    def add_time_from_warning(self, warning_window):
        """Add time from warning"""
        minutes_to_add = simpledialog.askinteger(
            "Add Time", 
            "Enter minutes to add (1-30):",
            parent=warning_window,
            minvalue=1,
            maxvalue=30
        )
        
        if minutes_to_add:
            self.notification_time = datetime.now() + timedelta(minutes=minutes_to_add)
            self.total_duration = minutes_to_add * 60
            self.timer_running = True
            self.timeout_shown = False
            
            if warning_window.winfo_exists():
                warning_window.destroy()
                self.current_warning_window = None
                self.set_fullscreen(False)
            
            self.update_display()
            self.status_label.config(text=f"Added {minutes_to_add} minutes", fg='#4CAF50')
            self.main_window.after(2000, lambda: self.status_label.config(
                text="Timer running...", 
                fg='#6c757d'
            ) if self.timer_running else None)
    
    def shutdown_countdown(self, seconds, window, label):
        """Shutdown countdown"""
        if seconds > 0 and window.winfo_exists():
            label.config(text=f"This computer will shutdown after {seconds} seconds")
            window.after(1000, self.shutdown_countdown, seconds-1, window, label)
        elif window.winfo_exists():
            try:
                os.system("shutdown /s /t 1")
                #print("Shutdown command would execute here")
            except Exception as e:
                messagebox.showerror("Shutdown Error", f"Failed to shutdown: {str(e)}")

    def run(self):
        """Run application"""
        try:
            self.main_window.mainloop()
        except KeyboardInterrupt:
            self.cleanup()
        except Exception as e:
            print(f"Unexpected error: {e}")
            self.cleanup()

if __name__ == "__main__":
    app = FullscreenTimerApp()
    app.run()
