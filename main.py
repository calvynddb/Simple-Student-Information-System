"""
Main entry point for nexo SIS application.
"""

import customtkinter as ctk
from config import BG_COLOR, WINDOW_WIDTH, WINDOW_HEIGHT
from backend import init_files, load_csv
from frontend_ui.auth import LoginFrame
from frontend_ui.dashboard import DashboardFrame
from frontend_ui.ui.utils import show_dialog


class App(ctk.CTk):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.title("nexo")
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        
        # authentication state
        self.logged_in = False

        # initialize data files
        init_files()

        # load data (guarded)
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

        # create container
        self.container = ctk.CTkFrame(self)
        self.container.pack(fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # create frames
        self.frames = {}
        for F in (LoginFrame, DashboardFrame):
            frame = F(self.container, self)
            self.frames[F] = frame
            # use place so we can animate sliding transitions between frames
            frame.place(relx=0, rely=0, relwidth=1, relheight=1)

        # show dashboard frame first (without fade animation)
        self.current_frame = None
        self.show_frame(DashboardFrame, fade=False)

    def show_custom_dialog(self, title, message, dialog_type="info", callback=None):
        """Show a custom styled dialog matching the app theme.

        dialog_type: 'info', 'error', 'warning', 'yesno'
        For 'yesno', returns True/False. For others, returns None.
        """
        return show_dialog(self, title, message, dialog_type, callback)

    def show_frame(self, cont, fade=True):
        """Show a specific frame."""
        new_frame = self.frames[cont]
        old_frame = getattr(self, 'current_frame', None)
        if old_frame is new_frame:
            return

        # fast window fade (alpha) transition: fade out, swap frames, fade in
        if not fade:
            # skip fade animation on launch
            new_frame.lift()
            self.current_frame = new_frame
            from frontend_ui.ui.utils import apply_button_hover
            try:
                apply_button_hover(new_frame)
            except Exception:
                pass
            # call on_frame_shown callback if it exists
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
                    self.after(15, lambda: fade_out(i + 1))
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
                    self.after(15, lambda: fade_in(i + 1))
                else:
                    # call on_frame_shown callback if it exists
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
            # call on_frame_shown callback if it exists
            if hasattr(new_frame, 'on_frame_shown'):
                try:
                    new_frame.on_frame_shown()
                except Exception:
                    pass


def main():
    """Run the application."""
    try:
        app = App()
        app.mainloop()
    except Exception as e:
        import traceback
        import sys
        traceback.print_exc()
        try:
            # try to show a dialog if tkinter is still usable
            from tkinter import messagebox
            messagebox.showerror("Application Error", f"Unhandled exception during startup:\n{e}")
        except Exception:
            pass
        sys.exit(1)


if __name__ == "__main__":
    main()
