"""
Programs view module extracted from original views.py
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
from data import validate_program, save_csv


class ProgramsView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        self.setup_ui()

    def setup_ui(self):
        table_container = DepthCard(self, fg_color=PANEL_COLOR, corner_radius=15, border_width=2, border_color=BORDER_COLOR)
        table_container.grid(row=1, column=0, sticky="nsew", padx=(0, 25))

        setup_treeview_style()
        cols = ("#", "Code", "Program Name", "College", "Students")
        self.tree = ttk.Treeview(table_container, columns=cols, show="headings", style="Treeview")
        for c in cols:
            self.tree.heading(c, text=c.upper())
            self.tree.column(c, anchor="center", stretch=True, width=100)

        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        self.tree.bind("<Button-1>", self.on_column_click)
        self.tree.bind("<Motion>", self._on_tree_motion)
        self.tree.bind("<Leave>", self._on_tree_leave)
        self.tree.bind("<ButtonRelease-1>", self.on_row_click)
        self.tree.tag_configure('odd', background=PANEL_COLOR)
        self.tree.tag_configure('even', background="#1F1630")
        self.tree.tag_configure('hover', background="#2A1F3D")

        ctrl = ctk.CTkFrame(table_container, fg_color="transparent")
        ctrl.pack(fill="x", padx=10, pady=(6,12))
        self.current_page = 1
        self.page_size = 25
        self._last_page_items = []
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
            props = [0.06, 0.14, 0.6, 0.12, 0.08]
            for i, col in enumerate(cols):
                self.tree.column(col, width=max(int(total * props[i]), 50))
            self._on_table_configure(e)

        table_container.bind('<Configure>', _on_table_config)

        right_panel = ctk.CTkFrame(self, width=280, fg_color="transparent")
        right_panel.grid(row=1, column=1, sticky="nsew")
        self.right_panel = right_panel

        top_card = DepthCard(right_panel, fg_color=PANEL_COLOR, corner_radius=15, border_width=2, border_color=BORDER_COLOR)
        top_card.pack(fill="x", pady=(0, 20))
        ctk.CTkLabel(top_card, text="Top Enrolled", font=get_font(13, True)).pack(anchor="w", padx=20, pady=15)
        
        enrollments = {}
        for student in self.controller.students:
            prog = student.get('program', 'Unknown')
            enrollments[prog] = enrollments.get(prog, 0) + 1
        
        sorted_progs = sorted(enrollments.items(), key=lambda x: x[1], reverse=True)[:3]
        colors_list = [ACCENT_COLOR, "#a78bfa", "#6366f1"]
        
        for i, (p, val) in enumerate(sorted_progs):
            f = ctk.CTkFrame(top_card, fg_color="transparent")
            f.pack(fill="x", padx=20, pady=5)
            ctk.CTkLabel(f, text=p, font=get_font(13, True)).pack(side="left")
            ctk.CTkLabel(f, text=f"{val} Students", text_color=TEXT_MUTED).pack(side="right")
            bar = ctk.CTkProgressBar(top_card, progress_color=colors_list[i], fg_color="#2A1F3D", height=8)
            bar.pack(fill="x", padx=20, pady=(0, 15))
            bar.set(min(val / 50, 1.0))

        dist_card = DepthCard(right_panel, fg_color=PANEL_COLOR, corner_radius=15, border_width=2, border_color=BORDER_COLOR)
        dist_card.pack(fill="both", expand=True)
        ctk.CTkLabel(dist_card, text="College Program Distribution", font=get_font(13, True)).pack(anchor="w", padx=20, pady=15)

        self.create_donut_chart(dist_card)
        self.right_dist_card = dist_card
        self.refresh_table()

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

    def create_donut_chart(self, parent):
        if not MATPLOTLIB_AVAILABLE:
            ctk.CTkLabel(parent, text="Matplotlib required", text_color=TEXT_MUTED).pack(pady=40)
            return
        
        fig, ax = plt.subplots(figsize=(3, 3), dpi=100)
        fig.patch.set_facecolor(PANEL_COLOR)

        color_map = {
            'CCS': '#87CEEB',
            'COE': '#800000',
            'CSM': '#FF0000',
            'CED': '#00008B',
            'CASS': '#008000',
            'Cass': '#008000',
            'CEBA': '#FFD700',
            'CHS': '#FFFFFF',
        }

        college_counts = {}
        for p in self.controller.programs:
            coll = p.get('college', 'Unknown')
            college_counts[coll] = college_counts.get(coll, 0) + 1

        labels = list(college_counts.keys())
        data = [college_counts[k] for k in labels]

        if sum(data) > 0:
            colors = [color_map.get(k, COLOR_PALETTE[i % len(COLOR_PALETTE)]) for i, k in enumerate(labels)]
            wedges, texts = ax.pie(data, colors=colors, startangle=90,
                                   wedgeprops=dict(width=0.4, edgecolor=PANEL_COLOR, linewidth=2))
            ax.axis('equal')

            canvas = FigureCanvasTkAgg(fig, master=parent)
            canvas.draw()
            canvas.get_tk_widget().pack(pady=(6, 2))

            legend_frame = ctk.CTkFrame(parent, fg_color="transparent")
            legend_frame.pack(side="bottom", pady=(6, 12), padx=8)

            for i, (lab, col) in enumerate(zip(labels, colors)):
                r = i // 2
                c = i % 2
                f = ctk.CTkFrame(legend_frame, fg_color="transparent")
                f.grid(row=r, column=c, padx=8, pady=4, sticky="w")
                sq = ctk.CTkFrame(f, width=14, height=14, fg_color=col, corner_radius=3)
                sq.pack(side="left", padx=(0, 8))
                ctk.CTkLabel(f, text=f"{lab} ({college_counts.get(lab,0)})", font=get_font(10)).pack(side="left")

    def refresh_table(self):
        rows = []
        for idx, p in enumerate(self.controller.programs, 1):
            student_count = len([s for s in self.controller.students if s.get('program') == p['code']])
            rows.append((idx, p['code'], p['name'], p['college'], student_count))
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
        top_card = DepthCard(self.right_panel, fg_color=PANEL_COLOR, corner_radius=15, border_width=2, border_color=BORDER_COLOR)
        top_card.pack(fill="x", pady=(0, 20))
        ctk.CTkLabel(top_card, text="Top Enrolled", font=get_font(13, True)).pack(anchor="w", padx=20, pady=15)

        enrollments = {}
        for student in self.controller.students:
            prog = student.get('program', 'Unknown')
            enrollments[prog] = enrollments.get(prog, 0) + 1
        sorted_progs = sorted(enrollments.items(), key=lambda x: x[1], reverse=True)[:3]
        colors_list = [ACCENT_COLOR, "#a78bfa", "#6366f1"]
        for i, (p, val) in enumerate(sorted_progs):
            f = ctk.CTkFrame(top_card, fg_color="transparent")
            f.pack(fill="x", padx=20, pady=5)
            ctk.CTkLabel(f, text=p, font=get_font(13, True)).pack(side="left")
            ctk.CTkLabel(f, text=f"{val} Students", text_color=TEXT_MUTED).pack(side="right")
            bar = ctk.CTkProgressBar(top_card, progress_color=colors_list[i], fg_color="#2A1F3D", height=8)
            bar.pack(fill="x", padx=20, pady=(0, 15))
            bar.set(min(val / 50, 1.0))

        dist_card = DepthCard(self.right_panel, fg_color=PANEL_COLOR, corner_radius=15, border_width=2, border_color=BORDER_COLOR)
        dist_card.pack(fill="both", expand=True)
        ctk.CTkLabel(dist_card, text="College Program Distribution", font=get_font(13, True)).pack(anchor="w", padx=20, pady=15)
        self.create_donut_chart(dist_card)

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
            self.delete_program()
        ctk.CTkButton(btn_frame, text="Edit", command=_edit, fg_color=ACCENT_COLOR).pack(side="left", expand=True, fill="x", padx=(0,6))
        ctk.CTkButton(btn_frame, text="Delete", command=_delete, fg_color="#c41e3a").pack(side="left", expand=True, fill="x", padx=(6,0))
        ctk.CTkButton(dlg, text="Cancel", command=dlg.destroy).pack(pady=(6,0))

    def filter_table(self, query):
        rows = []
        for idx, p in enumerate(self.controller.programs, 1):
            if (query in p.get('name', '').lower() or 
                query in p.get('code', '').lower() or
                query in p.get('college', '').lower()):
                student_count = len([s for s in self.controller.students if s.get('program') == p['code']])
                rows.append((idx, p['code'], p['name'], p['college'], student_count))
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

    def add_program(self):
        modal = ctk.CTkToplevel(self)
        modal.title("Add Program")
        screen_height = modal.winfo_screenheight()
        height = min(400, int(screen_height * 0.6))
        modal.geometry(f"500x{height}")
        modal.attributes('-topmost', True)
        
        modal.update_idletasks()
        x = (modal.winfo_screenwidth() // 2) - (modal.winfo_width() // 2)
        y = (modal.winfo_screenheight() // 2) - (modal.winfo_height() // 2)
        modal.geometry(f"500x{height}+{x}+{y}")
        
        form_frame = ctk.CTkFrame(modal, fg_color="transparent")
        form_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(form_frame, text="New Program", font=get_font(16, True)).pack(pady=(0, 20))
        
        ctk.CTkLabel(form_frame, text="Program Code", font=FONT_BOLD).pack(anchor="w")
        code_entry = ctk.CTkEntry(form_frame, placeholder_text="e.g., BSCS", height=40)
        code_entry.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(form_frame, text="Program Name", font=FONT_BOLD).pack(anchor="w")
        name_entry = ctk.CTkEntry(form_frame, placeholder_text="Program Name", height=40)
        name_entry.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(form_frame, text="College", font=FONT_BOLD).pack(anchor="w")
        college_values = [c['code'] for c in self.controller.colleges]
        if len(college_values) > 10:
            college_widget = SmartSearchEntry(form_frame, college_values, placeholder="Select College", height=40)
            if college_values:
                college_widget.insert(0, college_values[0])
        else:
            college_widget = ctk.CTkOptionMenu(form_frame, values=college_values, height=40)
            college_widget.set(college_values[0] if college_values else "")
        college_widget.pack(fill="x", pady=(0, 20))
        
        def save():
            code = code_entry.get().strip()
            name = name_entry.get().strip()
            college = college_widget.get()
            
            if not all([code, name, college]):
                messagebox.showerror("Error", "Please fill all fields")
                return
            
            if any(p['code'] == code for p in self.controller.programs):
                messagebox.showerror("Error", "Program code already exists")
                return

            new_prog = {'code': code, 'name': name, 'college': college}
            ok, msg = validate_program(new_prog)
            if not ok:
                messagebox.showerror("Error", msg)
                return
            
            self.controller.programs.append(new_prog)
            save_csv('program', self.controller.programs)
            self.refresh_table()
            try:
                for w in self.right_panel.winfo_children():
                    w.destroy()
                dist_card = DepthCard(self.right_panel, fg_color=PANEL_COLOR, corner_radius=15, border_width=2, border_color=BORDER_COLOR)
                dist_card.pack(fill="both", expand=True)
                ctk.CTkLabel(dist_card, text="College Program Distribution", font=get_font(13, True)).pack(anchor="w", padx=20, pady=15)
                self.create_donut_chart(dist_card)
                try:
                    self._refresh_all_sidebars()
                except Exception:
                    pass
            except Exception:
                pass
            modal.destroy()
            messagebox.showinfo("Success", "Program added successfully!")
        
        ctk.CTkButton(form_frame, text="Save Program", command=save, height=40,
                     fg_color=ACCENT_COLOR, text_color="black", font=FONT_BOLD).pack(fill="x")

    def show_context_menu_program(self, event):
        item = self.tree.identify('item', event.x, event.y)
        if not item:
            return
        
        self.tree.selection_set(item)
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="Edit", command=lambda: self.on_row_select(None))
        menu.add_command(label="Delete", command=self.delete_program)
        
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()
    
    def delete_program(self):
        selection = self.tree.selection()
        if not selection:
            return
        
        selected_item = selection[0]
        row_data = self.tree.item(selected_item)['values']
        prog_code = row_data[1]
        
        program = next((p for p in self.controller.programs if p['code'] == prog_code), None)
        if not program:
            messagebox.showerror("Error", "Program not found")
            return
        
        if messagebox.askyesno("Confirm Delete", f"Delete {prog_code}?"):
            self.controller.programs.remove(program)
            save_csv('program', self.controller.programs)
            self.refresh_table()
            try:
                self.refresh_sidebar()
                self._refresh_all_sidebars()
            except Exception:
                pass
            messagebox.showinfo("Success", "Program deleted successfully!")

    def on_row_select(self, event):
        selection = self.tree.selection()
        if not selection:
            return
        
        selected_item = selection[0]
        row_data = self.tree.item(selected_item)['values']
        prog_code = row_data[1]
        
        program = next((p for p in self.controller.programs if p['code'] == prog_code), None)
        if not program:
            return
        
        edit_window = ctk.CTkToplevel(self)
        edit_window.title("Edit Program")
        edit_window.geometry("450x350")
        edit_window.attributes('-topmost', True)
        
        edit_window.update_idletasks()
        x = (edit_window.winfo_screenwidth() // 2) - (edit_window.winfo_width() // 2)
        y = (edit_window.winfo_screenheight() // 2) - (edit_window.winfo_height() // 2)
        edit_window.geometry(f"+{x}+{y}")
        
        form_frame = ctk.CTkFrame(edit_window, fg_color="transparent")
        form_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(form_frame, text=f"Edit Program - {prog_code}", font=get_font(16, True)).pack(pady=(0, 20))
        
        ctk.CTkLabel(form_frame, text="Program Code", font=FONT_BOLD).pack(anchor="w")
        code_entry = ctk.CTkEntry(form_frame, height=40)
        code_entry.insert(0, program['code'])
        code_entry.configure(state="disabled")
        code_entry.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(form_frame, text="Program Name", font=FONT_BOLD).pack(anchor="w")
        name_entry = ctk.CTkEntry(form_frame, height=40)
        name_entry.insert(0, program['name'])
        name_entry.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(form_frame, text="College", font=FONT_BOLD).pack(anchor="w")
        college_values = [c['code'] for c in self.controller.colleges]
        if len(college_values) > 10:
            college_widget = SmartSearchEntry(form_frame, college_values, placeholder="Select College", height=40)
            college_widget.insert(0, program['college'])
        else:
            college_widget = ctk.CTkOptionMenu(form_frame, values=college_values, height=40)
            college_widget.set(program['college'])
        college_widget.pack(fill="x", pady=(0, 20))
        
        button_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        button_frame.pack(fill="x")
        
        def save():
            program['name'] = name_entry.get().strip()
            program['college'] = college_widget.get()
            ok, msg = validate_program(program)
            if not ok:
                messagebox.showerror("Error", msg)
                return
            try:
                save_csv('program', self.controller.programs)
            except Exception:
                messagebox.showerror("Error", "Failed to save program")
                return
            edit_window.destroy()
            self.refresh_table()
            messagebox.showinfo("Success", "Program updated successfully!")
        
        def delete():
            if messagebox.askyesno("Confirm Delete", f"Delete {program['code']}?"):
                self.controller.programs.remove(program)
                save_csv('program', self.controller.programs)
                edit_window.destroy()
                self.refresh_table()
                messagebox.showinfo("Success", "Program deleted successfully!")
        
        ctk.CTkButton(button_frame, text="Save Changes", command=save, height=40,
                     fg_color=ACCENT_COLOR, text_color="black", font=FONT_BOLD).pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkButton(button_frame, text="Delete", command=delete, height=40,
                     fg_color="#c41e3a", font=FONT_BOLD).pack(side="left", fill="x", expand=True, padx=(5, 0))
