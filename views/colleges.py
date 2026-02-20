"""
Colleges view module extracted from original views.py
"""
import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox

from config import (
    FONT_MAIN, FONT_BOLD, BG_COLOR, PANEL_COLOR, ACCENT_COLOR, 
    TEXT_MUTED, BORDER_COLOR, COLOR_PALETTE, TEXT_PRIMARY
)
from config import get_font
from ui import DepthCard, placeholder_image, setup_treeview_style
from data import validate_college, save_csv


class CollegesView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        self.sort_column = None
        self.sort_reverse = False
        self.current_page = 1
        self.page_size = 25
        self._last_page_items = []
        self.setup_ui()

    def setup_ui(self):
        table_container = DepthCard(self, fg_color=PANEL_COLOR, corner_radius=15, border_width=2, border_color=BORDER_COLOR)
        table_container.grid(row=1, column=0, sticky="nsew", padx=(0, 25))
        
        setup_treeview_style()
        cols = ("#", "College Code", "College Name")
        self.tree = ttk.Treeview(table_container, columns=cols, show="headings", style="Treeview")
        for c in cols:
            self.tree.heading(c, text=c.upper())
            self.tree.column(c, anchor="center", stretch=True, width=120)
        self.tree.pack(fill="both", expand=True, padx=15, pady=15)
        self.tree.bind("<Button-1>", self.on_column_click)
        self.tree.bind("<Motion>", self._on_tree_motion)
        self.tree.bind("<Leave>", self._on_tree_leave)
        self.tree.bind("<ButtonRelease-1>", self.on_row_click)
        self.tree.tag_configure('odd', background=PANEL_COLOR)
        self.tree.tag_configure('even', background="#1F1630")
        self.tree.tag_configure('hover', background="#2A1F3D")

        ctrl = ctk.CTkFrame(table_container, fg_color="transparent")
        ctrl.pack(fill="x", padx=15, pady=(6,12))
        self.table_container = table_container
        
        self.prev_btn = ctk.CTkButton(ctrl, text="◀ Prev", width=80, command=lambda: self.change_page(-1))
        self.prev_btn.pack(side="left", padx=(0,8))
        
        self.pagination_frame = ctk.CTkFrame(ctrl, fg_color="transparent")
        self.pagination_frame.pack(side="left", padx=8)
        self.page_buttons = []
        
        self.next_btn = ctk.CTkButton(ctrl, text="Next ▶", width=80, command=lambda: self.change_page(1))
        self.next_btn.pack(side="left", padx=(8,0))

        def _on_table_config(e):
            total = max(e.width - 20, 200)
            props = [0.06, 0.32, 0.62]
            for i, col in enumerate(cols):
                self.tree.column(col, width=max(int(total * props[i]), 60))
            self._on_table_configure(e)

        table_container.bind('<Configure>', _on_table_config)

        right_panel = ctk.CTkFrame(self, width=240, fg_color="transparent")
        right_panel.grid(row=1, column=1, sticky="nsew")
        
        ctk.CTkLabel(right_panel, text="DIRECTORY FACTS", font=get_font(11, True), text_color=TEXT_MUTED).pack(anchor="w", pady=(0, 10))

        self._fact_img_students = placeholder_image(size=22, color=ACCENT_COLOR)
        self._fact_img_programs = placeholder_image(size=22, color="#8b5cf6")
        self._fact_img_colleges = placeholder_image(size=22, color="#4f6bed")

        total_students = str(len(self.controller.students))
        total_programs = str(len(self.controller.programs))
        total_colleges = str(len(self.controller.colleges))
        avg_students_per_program = "0"
        try:
            avg_students_per_program = f"{len(self.controller.students) // max(len(self.controller.programs),1)}"
        except Exception:
            avg_students_per_program = "0"

        self.fact_card(right_panel, "TOTAL STUDENTS", total_students, self._fact_img_students, "#1d2335", height=120)
        self.fact_card(right_panel, "TOTAL PROGRAMS", total_programs, self._fact_img_programs, "#2c2c30", height=120)
        self.fact_card(right_panel, "TOTAL COLLEGES", total_colleges, self._fact_img_colleges, "#2c2c30", height=120)
        self.fact_card(right_panel, "AVG STUDENTS/PROGRAM", avg_students_per_program, self._fact_img_students, "#2c2c30", height=120, expand=True)

        self.refresh_table()

    def fact_card(self, parent, title, val, icon_img, color, height=80, expand=False):
        card = DepthCard(parent, fg_color=color, corner_radius=10, border_width=2, border_color=BORDER_COLOR, height=height)
        if expand:
            card.pack(fill="both", expand=True, pady=8)
        else:
            card.pack(fill="x", pady=8)
        card.pack_propagate(False)
        ctk.CTkLabel(card, text=title, font=get_font(11, True), text_color=ACCENT_COLOR).place(x=15, y=14)
        ctk.CTkLabel(card, text=val, font=get_font(22, True)).place(x=15, y=36)
        lbl = ctk.CTkLabel(card, image=icon_img, text="")
        lbl.image = icon_img
        lbl.place(relx=0.85, rely=0.5, anchor="center")

    def refresh_table(self):
        rows = []
        for idx, c in enumerate(self.controller.colleges, 1):
            rows.append((idx, c['code'], c['name']))
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

    def refresh_sidebar(self):
        for w in self.right_panel.winfo_children():
            w.destroy()

        ctk.CTkLabel(self.right_panel, text="DIRECTORY FACTS", font=get_font(11, True), text_color=TEXT_MUTED).pack(anchor="w", pady=(0, 10))

        self._fact_img_students = placeholder_image(size=22, color=ACCENT_COLOR)
        self._fact_img_programs = placeholder_image(size=22, color="#8b5cf6")
        self._fact_img_colleges = placeholder_image(size=22, color="#4f6bed")

        total_students = str(len(self.controller.students))
        total_programs = str(len(self.controller.programs))
        total_colleges = str(len(self.controller.colleges))
        avg_students_per_program = "0"
        try:
            avg_students_per_program = f"{len(self.controller.students) // max(len(self.controller.programs),1)}"
        except Exception:
            avg_students_per_program = "0"

        self.fact_card(self.right_panel, "TOTAL STUDENTS", total_students, self._fact_img_students, "#1d2335", height=120)
        self.fact_card(self.right_panel, "TOTAL PROGRAMS", total_programs, self._fact_img_programs, "#2c2c30", height=120)
        self.fact_card(self.right_panel, "TOTAL COLLEGES", total_colleges, self._fact_img_colleges, "#2c2c30", height=120)
        self.fact_card(self.right_panel, "AVG STUDENTS/PROGRAM", avg_students_per_program, self._fact_img_students, "#2c2c30", height=120, expand=True)

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
        dlg.geometry("340x160")
        dlg.attributes('-topmost', True)
        ctk.CTkLabel(dlg, text=str(row_values), wraplength=320).pack(pady=12, padx=8)
        btn_frame = ctk.CTkFrame(dlg, fg_color="transparent")
        btn_frame.pack(fill="x", padx=12, pady=8)
        def _edit():
            self.tree.selection_set(item)
            dlg.destroy()
            self.on_row_select(None)
        def _delete():
            self.tree.selection_set(item)
            dlg.destroy()
            self.delete_college()
        ctk.CTkButton(btn_frame, text="Edit", command=_edit, fg_color=ACCENT_COLOR).pack(side="left", expand=True, fill="x", padx=(0,6))
        ctk.CTkButton(btn_frame, text="Delete", command=_delete, fg_color="#c41e3a").pack(side="left", expand=True, fill="x", padx=(6,0))
        ctk.CTkButton(dlg, text="Cancel", command=dlg.destroy).pack(pady=(6,0))

    def filter_table(self, query):
        rows = []
        for idx, c in enumerate(self.controller.colleges, 1):
            if (query in c.get('name', '').lower() or 
                query in c.get('code', '').lower()):
                rows.append((idx, c['code'], c['name']))
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

    def add_college(self):
        modal = ctk.CTkToplevel(self)
        modal.title("Add College")
        screen_height = modal.winfo_screenheight()
        height = min(350, int(screen_height * 0.55))
        modal.geometry(f"450x{height}")
        modal.attributes('-topmost', True)
        
        modal.update_idletasks()
        x = (modal.winfo_screenwidth() // 2) - (modal.winfo_width() // 2)
        y = (modal.winfo_screenheight() // 2) - (modal.winfo_height() // 2)
        modal.geometry(f"450x{height}+{x}+{y}")
        
        form_frame = ctk.CTkFrame(modal, fg_color="transparent")
        form_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(form_frame, text="New College", font=get_font(16, True)).pack(pady=(0, 20))
        
        ctk.CTkLabel(form_frame, text="College Code", font=FONT_BOLD).pack(anchor="w")
        code_entry = ctk.CTkEntry(form_frame, placeholder_text="e.g., COE", height=40)
        code_entry.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(form_frame, text="College Name", font=FONT_BOLD).pack(anchor="w")
        name_entry = ctk.CTkEntry(form_frame, placeholder_text="College Name", height=40)
        name_entry.pack(fill="x", pady=(0, 20))
        
        def save():
            code = code_entry.get().strip()
            name = name_entry.get().strip()
            
            if not code or not name:
                messagebox.showerror("Error", "Please fill all fields")
                return
            
            if any(c['code'] == code for c in self.controller.colleges):
                messagebox.showerror("Error", "College code already exists")
                return
            new_col = {'code': code, 'name': name}
            ok, msg = validate_college(new_col)
            if not ok:
                messagebox.showerror("Error", msg)
                return
            self.controller.colleges.append(new_col)
            save_csv('college', self.controller.colleges)
            self.refresh_table()
            try:
                self.refresh_sidebar()
                self._refresh_all_sidebars()
            except Exception:
                pass
            modal.destroy()
            messagebox.showinfo("Success", "College added successfully!")
        
        ctk.CTkButton(form_frame, text="Save College", command=save, height=40,
                     fg_color=ACCENT_COLOR, text_color="black", font=FONT_BOLD).pack(fill="x")

    def show_context_menu_college(self, event):
        item = self.tree.identify('item', event.x, event.y)
        if not item:
            return
        
        self.tree.selection_set(item)
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="Edit", command=lambda: self.on_row_select(None))
        menu.add_command(label="Delete", command=self.delete_college)
        
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()
    
    def delete_college(self):
        selection = self.tree.selection()
        if not selection:
            return
        
        selected_item = selection[0]
        row_data = self.tree.item(selected_item)['values']
        college_code = row_data[1]
        
        college = next((c for c in self.controller.colleges if c['code'] == college_code), None)
        if not college:
            messagebox.showerror("Error", "College not found")
            return
        
        has_programs = any(p['college'] == college['code'] for p in self.controller.programs)
        if has_programs:
            messagebox.showerror("Error", "Cannot delete college with associated programs")
            return
        
        if messagebox.askyesno("Confirm Delete", f"Delete {college_code}?"):
            self.controller.colleges.remove(college)
            save_csv('college', self.controller.colleges)
            self.refresh_table()
            try:
                self.refresh_sidebar()
                self._refresh_all_sidebars()
            except Exception:
                pass
            messagebox.showinfo("Success", "College deleted successfully!")

    def on_row_select(self, event):
        selection = self.tree.selection()
        if not selection:
            return
        
        selected_item = selection[0]
        row_data = self.tree.item(selected_item)['values']
        college_code = row_data[1]
        
        college = next((c for c in self.controller.colleges if c['code'] == college_code), None)
        if not college:
            return
        
        edit_window = ctk.CTkToplevel(self)
        edit_window.title("Edit College")
        edit_window.geometry("400x300")
        edit_window.attributes('-topmost', True)
        
        edit_window.update_idletasks()
        x = (edit_window.winfo_screenwidth() // 2) - (edit_window.winfo_width() // 2)
        y = (edit_window.winfo_screenheight() // 2) - (edit_window.winfo_height() // 2)
        edit_window.geometry(f"+{x}+{y}")
        
        form_frame = ctk.CTkFrame(edit_window, fg_color="transparent")
        form_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(form_frame, text=f"Edit College - {college_code}", 
                font=get_font(16, True)).pack(pady=(0, 20))
        
        ctk.CTkLabel(form_frame, text="College Code", font=FONT_BOLD).pack(anchor="w")
        code_entry = ctk.CTkEntry(form_frame, height=40)
        code_entry.insert(0, college['code'])
        code_entry.configure(state="disabled")
        code_entry.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(form_frame, text="College Name", font=FONT_BOLD).pack(anchor="w")
        name_entry = ctk.CTkEntry(form_frame, height=40)
        name_entry.insert(0, college['name'])
        name_entry.pack(fill="x", pady=(0, 20))
        
        button_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        button_frame.pack(fill="x")
        
        def save():
            college['name'] = name_entry.get().strip()
            save_csv('college', self.controller.colleges)
            edit_window.destroy()
            self.refresh_table()
            messagebox.showinfo("Success", "College updated successfully!")
        
        def delete():
            has_programs = any(p['college'] == college['code'] for p in self.controller.programs)
            if has_programs:
                messagebox.showerror("Error", "Cannot delete college with associated programs")
                return
            
            if messagebox.askyesno("Confirm Delete", f"Delete {college['code']}?"):
                self.controller.colleges.remove(college)
                save_csv('college', self.controller.colleges)
                edit_window.destroy()
                self.refresh_table()
                messagebox.showinfo("Success", "College deleted successfully!")
        
        ctk.CTkButton(button_frame, text="Save Changes", command=save, height=40,
                     fg_color=ACCENT_COLOR, text_color="black", font=FONT_BOLD).pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkButton(button_frame, text="Delete", command=delete, height=40,
                     fg_color="#c41e3a", font=FONT_BOLD).pack(side="left", fill="x", expand=True, padx=(5, 0))
