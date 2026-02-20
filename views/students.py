"""
Students view module extracted from original views.py
"""
import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox

try:
    import numpy as np
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

from config import (
    FONT_MAIN, FONT_BOLD, BG_COLOR, PANEL_COLOR, ACCENT_COLOR, 
    TEXT_MUTED, BORDER_COLOR, COLOR_PALETTE, TEXT_PRIMARY
)
from config import get_font
from ui import DepthCard, SmartSearchEntry, setup_treeview_style, placeholder_image
from data import validate_student, save_csv


class StudentsView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.sort_column = None
        self.sort_reverse = False
        self.setup_ui()

    def setup_ui(self):
        # Table Container
        table_container = DepthCard(self, fg_color=PANEL_COLOR, corner_radius=15, border_width=2, border_color=BORDER_COLOR)
        table_container.grid(row=1, column=0, sticky="nsew", padx=(0, 25))
        
        setup_treeview_style()
        cols = ("ID", "First Name", "Last Name", "Gender", "Year", "Program", "College")
        self.tree = ttk.Treeview(table_container, columns=cols, show="headings", style="Treeview")
        
        for c in cols: 
            self.tree.heading(c, text=c.upper())
        
        # Reduced base widths and centered
        self.tree.column("ID", width=80, anchor="center", stretch=True)
        self.tree.column("First Name", width=110, anchor="center", stretch=True)
        self.tree.column("Last Name", width=110, anchor="center", stretch=True)
        self.tree.column("Gender", width=70, anchor="center", stretch=True)
        self.tree.column("Year", width=60, anchor="center", stretch=True)
        self.tree.column("Program", width=80, anchor="center", stretch=True)
        self.tree.column("College", width=80, anchor="center", stretch=True)
        
        self.tree.pack(fill="both", expand=True, padx=15, pady=(15, 8))

        # Pagination controls (dynamic page size based on window height)
        ctrl = ctk.CTkFrame(table_container, fg_color="transparent")
        ctrl.pack(fill="x", padx=15, pady=(6,12))
        self.current_page = 1
        self.page_size = 25
        self._last_page_items = []
        self.table_container = table_container
        
        self.prev_btn = ctk.CTkButton(ctrl, text="◀ Prev", width=80, command=lambda: self.change_page(-1))
        self.prev_btn.pack(side="left", padx=(0,8))
        
        # Pagination indicator frame
        self.pagination_frame = ctk.CTkFrame(ctrl, fg_color="transparent")
        self.pagination_frame.pack(side="left", padx=8)
        self.page_buttons = []
        
        self.next_btn = ctk.CTkButton(ctrl, text="Next ▶", width=80, command=lambda: self.change_page(1))
        self.next_btn.pack(side="left", padx=(8,0))
        
        # Bind configure event to update page size dynamically
        table_container.bind('<Configure>', self._on_table_configure)
        
        self.tree.bind("<Double-1>", self.on_row_select)
        self.tree.bind("<Button-1>", self.on_column_click)
        self.tree.bind("<Motion>", self._on_tree_motion)
        self.tree.bind("<Leave>", self._on_tree_leave)
        self.tree.bind("<ButtonRelease-1>", self.on_row_click)
        # row tag styles for subtle striping
        self.tree.tag_configure('odd', background=PANEL_COLOR)
        self.tree.tag_configure('even', background="#1F1630")
        self.tree.tag_configure('hover', background="#2A1F3D")
        
        # New Sidebar Charts Panel
        right_panel = ctk.CTkFrame(self, width=240, fg_color="transparent")
        right_panel.grid(row=1, column=1, sticky="nsew")
        self.right_panel = right_panel
        ctk.CTkLabel(right_panel, text="OVERVIEW STATS", font=get_font(11, True), text_color=TEXT_MUTED).pack(anchor="w", pady=(0, 10))

        # Create small square placeholders for the stat icons and keep references
        self._stat_img_students = placeholder_image(size=28, color=ACCENT_COLOR)
        self._stat_img_programs = placeholder_image(size=28, color="#a78bfa")
        self._stat_img_colleges = placeholder_image(size=28, color="#6366f1")

        self.stat_card(right_panel, self._stat_img_students, str(len(self.controller.students)), "Total Students")
        self.stat_card(right_panel, self._stat_img_programs, str(len(self.controller.programs)), "Total Programs")
        self.stat_card(right_panel, self._stat_img_colleges, str(len(self.controller.colleges)), "Total Colleges")
        
        self.refresh_table()

    def refresh_sidebar(self):
        for w in self.right_panel.winfo_children():
            w.destroy()

        ctk.CTkLabel(self.right_panel, text="OVERVIEW STATS", font=get_font(11, True), text_color=TEXT_MUTED).pack(anchor="w", pady=(0, 10))

        self._stat_img_students = placeholder_image(size=28, color=ACCENT_COLOR)
        self._stat_img_programs = placeholder_image(size=28, color="#a78bfa")
        self._stat_img_colleges = placeholder_image(size=28, color="#6366f1")

        self.stat_card(self.right_panel, self._stat_img_students, str(len(self.controller.students)), "Total Students")
        self.stat_card(self.right_panel, self._stat_img_programs, str(len(self.controller.programs)), "Total Programs")
        self.stat_card(self.right_panel, self._stat_img_colleges, str(len(self.controller.colleges)), "Total Colleges")

    def _refresh_all_sidebars(self):
        try:
            from dashboard import DashboardFrame
            df = self.controller.frames.get(DashboardFrame)
            if not df:
                return
            for v in df.views.values():
                try:
                    if hasattr(v, 'refresh_sidebar'):
                        v.refresh_sidebar()
                except Exception:
                    pass
        except Exception:
            pass

    def refresh_table(self):
        rows = []
        for student in self.controller.students:
            college = next((p['college'] for p in self.controller.programs if p['code'] == student.get('program', '')), 'N/A')
            rows.append((student.get('id', ''), student.get('firstname', ''), student.get('lastname', ''), student.get('gender', ''), student.get('year', ''), student.get('program', ''), college))

        self._last_page_items = rows
        self.current_page = min(max(1, self.current_page), max(1, (len(rows) + self.page_size - 1) // self.page_size))
        self._render_page()
        self._last_hover = None

    def _render_page(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        total = len(self._last_page_items)
        per = self.page_size
        total_pages = max(1, (total + per - 1) // per)
        self.current_page = min(self.current_page, total_pages)
        start = (self.current_page - 1) * per
        end = start + per
        for idx, row in enumerate(self._last_page_items[start:end], start + 1):
            tag = 'even' if idx % 2 == 0 else 'odd'
            self.tree.insert("", "end", values=row, tags=(tag,))
        
        for btn in self.page_buttons:
            btn.destroy()
        self.page_buttons.clear()
        
        start_page = max(1, self.current_page - 2)
        end_page = min(total_pages, start_page + 4)
        if end_page - start_page < 4:
            start_page = max(1, end_page - 4)
        
        for p in range(start_page, end_page + 1):
            is_current = p == self.current_page
            btn = ctk.CTkButton(
                self.pagination_frame, 
                text=str(p), 
                width=32, 
                height=28,
                fg_color=ACCENT_COLOR if is_current else "#3b3b3f",
                command=lambda page=p: self.goto_page(page)
            )
            btn.pack(side="left", padx=2)
            self.page_buttons.append(btn)
        
        self.prev_btn.configure(state=("normal" if self.current_page > 1 else "disabled"))
        self.next_btn.configure(state=("normal" if self.current_page < total_pages else "disabled"))
    
    def goto_page(self, page):
        self.current_page = page
        self._render_page()

    def change_page(self, delta):
        self.current_page = max(1, self.current_page + delta)
        self._render_page()

    def _on_table_configure(self, event):
        available_height = self.table_container.winfo_height()
        usable_height = available_height - 80
        row_height = 25
        new_page_size = max(5, usable_height // row_height)
        
        if new_page_size != self.page_size:
            old_page = self.current_page
            self.page_size = new_page_size
            total_pages = max(1, (len(self._last_page_items) + self.page_size - 1) // self.page_size)
            self.current_page = min(old_page, total_pages)
            self._render_page()

    def _on_tree_motion(self, event):
        row = self.tree.identify_row(event.y)
        if not row:
            return
        if getattr(self, '_last_hover', None) == row:
            return
        if getattr(self, '_last_hover', None):
            prev_tags = list(self.tree.item(self._last_hover, 'tags'))
            if 'hover' in prev_tags:
                prev_tags.remove('hover')
                self.tree.item(self._last_hover, tags=prev_tags)
        tags = list(self.tree.item(row, 'tags'))
        if 'hover' not in tags:
            tags.append('hover')
            self.tree.item(row, tags=tags)
        self._last_hover = row

    def _on_tree_leave(self, event):
        if getattr(self, '_last_hover', None):
            prev_tags = list(self.tree.item(self._last_hover, 'tags'))
            if 'hover' in prev_tags:
                prev_tags.remove('hover')
                self.tree.item(self._last_hover, tags=prev_tags)
            self._last_hover = None

    def on_row_click(self, event):
        region = self.tree.identify_region(event.x, event.y)
        if region in ('cell', 'tree'):
            item = self.tree.identify_row(event.y)
            if item:
                self._show_action_dialog(item)

    def _show_action_dialog(self, item):
        row_values = self.tree.item(item)['values']
        dlg = ctk.CTkToplevel(self)
        dlg.title("Row Actions")
        dlg.geometry("300x160")
        dlg.attributes('-topmost', True)
        ctk.CTkLabel(dlg, text=str(row_values), wraplength=280).pack(pady=12, padx=8)
        btn_frame = ctk.CTkFrame(dlg, fg_color="transparent")
        btn_frame.pack(fill="x", padx=12, pady=8)
        def _edit():
            self.tree.selection_set(item)
            dlg.destroy()
            self.on_row_select(None)
        def _delete():
            self.tree.selection_set(item)
            dlg.destroy()
            self.delete_student()
        ctk.CTkButton(btn_frame, text="Edit", command=_edit, fg_color=ACCENT_COLOR).pack(side="left", expand=True, fill="x", padx=(0,6))
        ctk.CTkButton(btn_frame, text="Delete", command=_delete, fg_color="#c41e3a").pack(side="left", expand=True, fill="x", padx=(6,0))
        ctk.CTkButton(dlg, text="Cancel", command=dlg.destroy).pack(pady=(6,0))

    def filter_table(self, query):
        rows = []
        for student in self.controller.students:
            if (query in student.get('firstname', '').lower() or 
                query in student.get('lastname', '').lower() or
                query in student.get('id', '').lower()):
                college = next((p['college'] for p in self.controller.programs if p['code'] == student.get('program', '')), 'N/A')
                rows.append((student.get('id', ''), student.get('firstname', ''), student.get('lastname', ''), student.get('gender', ''), student.get('year', ''), student.get('program', ''), college))
        self._last_page_items = rows
        self.current_page = 1
        self._render_page()

    def on_column_click(self, event):
        region = self.tree.identify_region(event.x, event.y)
        if region == "heading":
            col = self.tree.identify_column(event.x)
            try:
                idx = int(col.replace('#', '')) - 1
                col_id = self.tree['columns'][idx]
            except Exception:
                col_id = self.tree.heading(col, "text")
            if self.sort_column == col_id:
                self.sort_reverse = not self.sort_reverse
            else:
                self.sort_column = col_id
                self.sort_reverse = False
            self.sort_table()
    
    def sort_table(self):
        if not self.sort_column:
            return
        
        items = [(self.tree.set(k, self.sort_column), k) for k in self.tree.get_children("")]
        items.sort(key=lambda x: self.try_numeric(x[0]), reverse=self.sort_reverse)
        
        for idx, (val, k) in enumerate(items):
            self.tree.move(k, "", idx)
    
    @staticmethod
    def try_numeric(val):
        try:
            return float(val)
        except ValueError:
            return val

    def stat_card(self, parent, icon_img, num, sub):
        height = 120
        card = DepthCard(parent, fg_color=PANEL_COLOR, corner_radius=15, border_width=2, border_color=BORDER_COLOR, height=height)
        card.pack(fill="x", pady=(0, 12))
        card.pack_propagate(False)
        icon_f = ctk.CTkFrame(card, width=45, height=45, fg_color="#2A1F3D", corner_radius=10)
        icon_f.place(x=20, y=16)
        lbl = ctk.CTkLabel(icon_f, image=icon_img, text="")
        lbl.image = icon_img
        lbl.place(relx=0.5, rely=0.5, anchor="center")
        ctk.CTkLabel(card, text=num, font=get_font(22, True)).place(x=20, y=54)
        ctk.CTkLabel(card, text=sub, font=get_font(12), text_color=TEXT_MUTED).place(x=20, y=84)
        return card
    def add_student(self):
        modal = ctk.CTkToplevel(self)
        modal.title("Add Student")
        screen_height = modal.winfo_screenheight()
        height = min(600, int(screen_height * 0.7))
        modal.geometry(f"500x{height}")
        modal.attributes('-topmost', True)
        
        modal.update_idletasks()
        x = (modal.winfo_screenwidth() // 2) - (modal.winfo_width() // 2)
        y = (modal.winfo_screenheight() // 2) - (modal.winfo_height() // 2)
        modal.geometry(f"500x{height}+{x}+{y}")
        
        form_frame = ctk.CTkScrollableFrame(modal, fg_color="transparent")
        form_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(form_frame, text="New Student Enrollment", font=get_font(16, True)).pack(pady=(0, 20))
        
        ctk.CTkLabel(form_frame, text="Student ID", font=FONT_BOLD).pack(anchor="w", pady=(10, 0))
        id_entry = ctk.CTkEntry(form_frame, placeholder_text="e.g., 2025-1234", height=40)
        id_entry.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(form_frame, text="First Name", font=FONT_BOLD).pack(anchor="w", pady=(10, 0))
        fname_entry = ctk.CTkEntry(form_frame, placeholder_text="First Name", height=40)
        fname_entry.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(form_frame, text="Last Name", font=FONT_BOLD).pack(anchor="w", pady=(10, 0))
        lname_entry = ctk.CTkEntry(form_frame, placeholder_text="Last Name", height=40)
        lname_entry.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(form_frame, text="Gender", font=FONT_BOLD).pack(anchor="w", pady=(10, 0))
        gender_combo = ctk.CTkOptionMenu(form_frame, values=["Male", "Female", "Other"], height=40)
        gender_combo.set("Male")
        gender_combo.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(form_frame, text="Year Level", font=FONT_BOLD).pack(anchor="w", pady=(10, 0))
        year_combo = ctk.CTkOptionMenu(form_frame, values=["1", "2", "3", "4", "5"], height=40)
        year_combo.set("1")
        year_combo.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(form_frame, text="Program", font=FONT_BOLD).pack(anchor="w", pady=(10, 0))
        program_values = [p['code'] for p in self.controller.programs]
        program_widget = SmartSearchEntry(form_frame, program_values, placeholder="Select Program", height=40)
        if program_values:
            program_widget.insert(0, program_values[0])
        program_widget.pack(fill="x", pady=(0, 20))
        
        def save():
            student_id = id_entry.get().strip()
            fname = fname_entry.get().strip()
            lname = lname_entry.get().strip()
            gender = gender_combo.get()
            year = year_combo.get()
            program = program_widget.get()
            
            if not all([student_id, fname, lname, gender, year, program]):
                messagebox.showerror("Error", "Please fill all fields")
                return
            
            if any(s['id'] == student_id for s in self.controller.students):
                messagebox.showerror("Error", "Student ID already exists")
                return
            
            new_student = {
                'id': student_id,
                'firstname': fname,
                'lastname': lname,
                'gender': gender,
                'year': year,
                'program': program,
            }
            ok, msg = validate_student(new_student)
            if not ok:
                messagebox.showerror("Error", msg)
                return
            
            self.controller.students.append(new_student)
            save_csv('student', self.controller.students)
            self.refresh_table()
            try:
                self.refresh_sidebar()
                self._refresh_all_sidebars()
            except Exception:
                pass
            modal.destroy()
            messagebox.showinfo("Success", "Student added successfully!")
        
        ctk.CTkButton(form_frame, text="Save Student", command=save, height=40, 
                     fg_color=ACCENT_COLOR, text_color="black", font=FONT_BOLD).pack(fill="x")

    def show_context_menu_student(self, event):
        item = self.tree.identify('item', event.x, event.y)
        if not item:
            return
        
        self.tree.selection_set(item)
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="Edit", command=lambda: self.on_row_select(None))
        menu.add_command(label="Delete", command=self.delete_student)
        
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()
    
    def delete_student(self):
        selection = self.tree.selection()
        if not selection:
            return
        
        selected_item = selection[0]
        row_data = self.tree.item(selected_item)['values']
        student_id = row_data[0]
        
        student = next((s for s in self.controller.students if s['id'] == student_id), None)
        if not student:
            messagebox.showerror("Error", "Student not found")
            return
        
        if messagebox.askyesno("Confirm Delete", f"Delete {student['firstname']} {student['lastname']}?"):
            self.controller.students.remove(student)
            save_csv('student', self.controller.students)
            self.refresh_table()
            try:
                self.refresh_sidebar()
                self._refresh_all_sidebars()
            except Exception:
                pass
            messagebox.showinfo("Success", "Student deleted successfully!")

    def on_row_select(self, event):
        selection = self.tree.selection()
        if not selection:
            return
        
        selected_item = selection[0]
        row_data = self.tree.item(selected_item)['values']
        
        edit_window = ctk.CTkToplevel(self)
        edit_window.title("Edit Student")
        edit_window.geometry("450x550")
        edit_window.attributes('-topmost', True)
        
        edit_window.update_idletasks()
        x = (edit_window.winfo_screenwidth() // 2) - (edit_window.winfo_width() // 2)
        y = (edit_window.winfo_screenheight() // 2) - (edit_window.winfo_height() // 2)
        edit_window.geometry(f"+{x}+{y}")
        
        form_frame = ctk.CTkScrollableFrame(edit_window, fg_color="transparent")
        form_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(form_frame, text=f"Edit Student - {row_data[0]}", font=get_font(16, True)).pack(pady=(0, 20))
        
        student = next((s for s in self.controller.students if s['id'] == row_data[0]), None)
        if not student:
            messagebox.showerror("Error", "Student not found")
            return
        
        ctk.CTkLabel(form_frame, text="Student ID", font=FONT_BOLD).pack(anchor="w", pady=(10, 0))
        id_entry = ctk.CTkEntry(form_frame, height=40)
        id_entry.insert(0, student['id'])
        id_entry.configure(state="disabled")
        id_entry.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(form_frame, text="First Name", font=FONT_BOLD).pack(anchor="w", pady=(10, 0))
        fname_entry = ctk.CTkEntry(form_frame, height=40)
        fname_entry.insert(0, student['firstname'])
        fname_entry.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(form_frame, text="Last Name", font=FONT_BOLD).pack(anchor="w", pady=(10, 0))
        lname_entry = ctk.CTkEntry(form_frame, height=40)
        lname_entry.insert(0, student['lastname'])
        lname_entry.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(form_frame, text="Gender", font=FONT_BOLD).pack(anchor="w", pady=(10, 0))
        gender_combo = ctk.CTkOptionMenu(form_frame, values=["Male", "Female", "Other"], height=40)
        gender_combo.set(student['gender'])
        gender_combo.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(form_frame, text="Year Level", font=FONT_BOLD).pack(anchor="w", pady=(10, 0))
        year_combo = ctk.CTkOptionMenu(form_frame, values=["1", "2", "3", "4", "5"], height=40)
        year_combo.set(student['year'])
        year_combo.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(form_frame, text="Program", font=FONT_BOLD).pack(anchor="w", pady=(10, 0))
        program_values = [p['code'] for p in self.controller.programs]
        program_widget = SmartSearchEntry(form_frame, program_values, placeholder="Select Program", height=40)
        program_widget.insert(0, student['program'])
        program_widget.pack(fill="x", pady=(0, 20))
        
        button_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=10)
        
        def save():
            student['firstname'] = fname_entry.get().strip()
            student['lastname'] = lname_entry.get().strip()
            student['gender'] = gender_combo.get()
            student['year'] = year_combo.get()
            student['program'] = program_widget.get()
            ok, msg = validate_student(student)
            if not ok:
                messagebox.showerror("Error", msg)
                return

            try:
                save_csv('student', self.controller.students)
            except Exception:
                messagebox.showerror("Error", "Failed to save student data")
                return
            edit_window.destroy()
            self.refresh_table()
            messagebox.showinfo("Success", "Student updated successfully!")
        
        def delete():
            if messagebox.askyesno("Confirm Delete", f"Delete {student['firstname']} {student['lastname']}?"):
                self.controller.students.remove(student)
                save_csv('student', self.controller.students)
                edit_window.destroy()
                self.refresh_table()
                messagebox.showinfo("Success", "Student deleted successfully!")
        
        ctk.CTkButton(button_frame, text="Save Changes", command=save, height=40, 
                     fg_color=ACCENT_COLOR, text_color="black", font=FONT_BOLD).pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkButton(button_frame, text="Delete", command=delete, height=40, 
                     fg_color="#c41e3a", font=FONT_BOLD).pack(side="left", fill="x", expand=True, padx=(5, 0))

