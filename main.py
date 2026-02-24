"""
Main entry point for EduMdge SIS application
"""

import customtkinter as ctk
from config import BG_COLOR, WINDOW_WIDTH, WINDOW_HEIGHT
from backend import init_files, load_csv
from frontend_ui.auth import LoginFrame
from frontend_ui.dashboard import DashboardFrame
import os
import time


class App(ctk.CTk):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.title("nexo")
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        
        # Authentication state
        self.logged_in = False
        
        # Initialize data files
        init_files()
        
        # Load data (guarded)
        try:
            self.colleges = load_csv('college')
        except Exception:
            import traceback
            traceback.print_exc()
            self.colleges = []
        try:
            self.programs = load_csv('program')
        except Exception:
            import traceback
            traceback.print_exc()
            self.programs = []
        try:
            self.students = load_csv('student')
        except Exception:
            import traceback
            traceback.print_exc()
            self.students = []

        # Create container
        self.container = ctk.CTkFrame(self)
        self.container.pack(fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # Create frames
        self.frames = {}
        for F in (LoginFrame, DashboardFrame):
            frame = F(self.container, self)
            self.frames[F] = frame
            # use place so we can animate sliding transitions between frames
            frame.place(relx=0, rely=0, relwidth=1, relheight=1)

        # Show dashboard frame first (without fade animation)
        self.current_frame = None
        self.show_frame(DashboardFrame, fade=False)

    def show_custom_dialog(self, title, message, dialog_type="info", callback=None):
        """Show a custom styled dialog matching the app theme.
        
        dialog_type: 'info', 'error', 'warning', 'yesno'
        For 'yesno', returns True/False. For others, returns None.
        """
        from config import BG_COLOR, ACCENT_COLOR, TEXT_PRIMARY, TEXT_MUTED, PANEL_COLOR, BORDER_COLOR
        from config import get_font
        
        result = [None]  # mutable container for yesno result
        
        dialog_window = ctk.CTkToplevel(self)
        dialog_window.title(title)
        dialog_window.overrideredirect(False)
        dialog_window.configure(fg_color=BG_COLOR)
        dialog_window.attributes('-topmost', True)
        dialog_window.grab_set()
        dialog_window.focus_force()
        
        # Size based on message length
        msg_len = len(message)
        height = 200 if msg_len < 100 else 250 if msg_len < 200 else 300
        dialog_window.geometry(f"450x{height}")
        
        dialog_window.update_idletasks()
        x = (dialog_window.winfo_screenwidth() // 2) - (225)
        y = (dialog_window.winfo_screenheight() // 2) - (height // 2)
        dialog_window.geometry(f"+{x}+{y}")
        
        # Pick accent color by dialog type
        if dialog_type == "error":
            accent = "#c41e3a"
            icon_text = "ERROR"
        elif dialog_type == "warning":
            accent = "#d4a017"
            icon_text = "WARNING"
        elif dialog_type == "yesno":
            accent = ACCENT_COLOR
            icon_text = "CONFIRM"
        else:
            accent = ACCENT_COLOR
            icon_text = "INFO"
        
        # Content frame
        frame = ctk.CTkFrame(dialog_window, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Type badge
        badge = ctk.CTkLabel(frame, text=icon_text, font=get_font(9, True),
                            text_color="white", fg_color=accent, corner_radius=6,
                            width=70, height=22)
        badge.pack(pady=(0, 10))
        
        # Title
        title_label = ctk.CTkLabel(frame, text=title, font=get_font(14, True), text_color=TEXT_PRIMARY)
        title_label.pack(pady=(0, 10))
        
        # Message
        msg_label = ctk.CTkLabel(frame, text=message, font=get_font(11), text_color=TEXT_MUTED, wraplength=380)
        msg_label.pack(pady=(0, 20), fill="both", expand=True)
        
        # Buttons
        button_frame = ctk.CTkFrame(frame, fg_color="transparent")
        button_frame.pack(fill="x")
        
        if dialog_type == "yesno":
            def _yes():
                result[0] = True
                if callback:
                    callback(True)
                dialog_window.destroy()
            
            def _no():
                result[0] = False
                if callback:
                    callback(False)
                dialog_window.destroy()
            
            ctk.CTkButton(button_frame, text="Yes", fg_color=accent, text_color="white",
                         hover_color="#7C3AED", font=get_font(11, True), height=36, command=_yes).pack(side="left", fill="x", expand=True, padx=(0, 8))
            ctk.CTkButton(button_frame, text="No", fg_color="#3a3a3f", text_color="white",
                         hover_color="#4a4a4f", font=get_font(11, True), height=36, command=_no).pack(side="left", fill="x", expand=True, padx=(8, 0))
        else:
            ctk.CTkButton(button_frame, text="OK", fg_color=accent, text_color="white",
                         hover_color="#7C3AED", font=get_font(11, True), height=36,
                         command=dialog_window.destroy).pack(fill="x")
        
        dialog_window.protocol("WM_DELETE_WINDOW", lambda: (result.__setitem__(0, False), dialog_window.destroy()))
        self.wait_window(dialog_window)
        return result[0]

    def show_frame(self, cont, fade=True):
        """Show a specific frame."""
        new_frame = self.frames[cont]
        old_frame = getattr(self, 'current_frame', None)
        if old_frame is new_frame:
            return

        # fast window fade (alpha) transition: fade out, swap frames, fade in
        if not fade:
            # Skip fade animation on launch
            new_frame.lift()
            self.current_frame = new_frame
            from frontend_ui.ui.utils import apply_button_hover
            try:
                apply_button_hover(new_frame)
            except Exception:
                pass
            # Call on_frame_shown callback if it exists
            if hasattr(new_frame, 'on_frame_shown'):
                try:
                    new_frame.on_frame_shown()
                except Exception:
                    pass
            return
        
        try:
            steps = max(3, int(180 // 15))
            def fade_out(i=0):
                a = 1.0 - (i / steps)
                try:
                    self.attributes('-alpha', max(0.0, a))
                except Exception:
                    pass
                if i < steps:
                    self.after(15, lambda: fade_out(i+1))
                else:
                    # swap frames while invisible
                    try:
                        new_frame.lift()
                        self.current_frame = new_frame
                        from frontend_ui.ui.utils import apply_button_hover
                        try:
                            apply_button_hover(new_frame)
                        except Exception:
                            pass
                    except Exception:
                        pass
                    fade_in(0)

            def fade_in(i=0):
                a = (i / steps)
                try:
                    self.attributes('-alpha', min(1.0, a))
                except Exception:
                    pass
                if i < steps:
                    self.after(15, lambda: fade_in(i+1))
                else:
                    # Call on_frame_shown callback if it exists
                    if hasattr(new_frame, 'on_frame_shown'):
                        try:
                            new_frame.on_frame_shown()
                        except Exception:
                            pass

            fade_out(0)
        except Exception:
            # fallback to instant raise
            new_frame.tkraise()
            try:
                from frontend_ui.ui.utils import apply_button_hover
                apply_button_hover(new_frame)
            except Exception:
                pass
            self.current_frame = new_frame
            # Call on_frame_shown callback if it exists
            if hasattr(new_frame, 'on_frame_shown'):
                try:
                    new_frame.on_frame_shown()
                except Exception:
                    pass


def _lerp(a, b, t):
    return a + (b - a) * t


def main():
    """Run the application."""
    # Quick verification to show which file is being executed and its timestamp
    try:
        mtime = time.ctime(os.path.getmtime(__file__))
    except Exception:
        mtime = "unknown"
    print(f"Starting {os.path.abspath(__file__)} (mtime: {mtime})")

    try:
        app = App()
        app.mainloop()
    except Exception as e:
        import traceback, sys
        traceback.print_exc()
        try:
            # try to show a dialog if tkinter is usable
            from tkinter import messagebox
            messagebox.showerror("Application Error", f"Unhandled exception during startup:\n{e}")
        except Exception:
            pass
        sys.exit(1)


if __name__ == "__main__":
    main()
