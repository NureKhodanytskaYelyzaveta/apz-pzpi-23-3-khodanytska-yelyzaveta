import tkinter as tk
from tkinter import ttk, messagebox
import requests
import threading
import time
from datetime import datetime
from config import COLORS, SERVER_URL, LOCKER_CELLS

class LockerSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("📚 Бібліотечний Поштомат")
        self.root.geometry("1100x800")
        
        self.colors = COLORS
        self.server_url = SERVER_URL
        self.locker_cells = LOCKER_CELLS.copy() 
        self.current_session = {
            "locker_id": None,
            "book_id": None,
            "user_id": None,
            "unlock_time": None
        }
        
        self.setup_styles()
        self.root.configure(bg=self.colors['background'])
        self.setup_ui()
        self.update_status("Вітаємо! Введіть OTP-код для отримання книги", self.colors['text_dark'])
        
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
    
        style.configure('Flat.TButton', 
                        font=('Consolas', 12, 'bold'),
                        foreground=self.colors['text_light'],
                        relief=tk.FLAT,
                        bordercolor=self.colors['primary'],
                        borderwidth=0,
                        padding=(15, 10))
        
        style.map('Flat.TButton',
                  background=[('active', self.colors['primary'])])

        style.configure('Success.Flat.TButton', 
                        background=self.colors['secondary'],
                        foreground=self.colors['text_light'])
        style.map('Success.Flat.TButton',
                  background=[('active', '#2E8B57')])

        style.configure('Light.Flat.TButton', 
                        background=self.colors['grey_light'],
                        foreground=self.colors['text_dark'],
                        font=('Consolas', 12, 'normal'))
        style.map('Light.Flat.TButton',
                  background=[('active', '#D3D3D3')])

        style.configure('Otp.TEntry', 
                        font=('Consolas', 24, 'bold'),
                        fieldbackground=self.colors['grey_light'],
                        foreground=self.colors['primary'],
                        padding=(10, 10),
                        relief=tk.FLAT,
                        borderwidth=0)
        
        style.configure('TCombobox', 
                        fieldbackground=self.colors['grey_light'], 
                        background=self.colors['panel_bg'],
                        foreground=self.colors['text_dark'],
                        font=('Consolas', 11))

        style.configure('Card.TFrame', background=self.colors['panel_bg'], relief='flat')
        
    def setup_ui(self):
        header_frame = tk.Frame(self.root, bg=self.colors['primary'], height=120)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(header_frame, 
                              text="📚 БІБЛІОТЕЧНИЙ ПОШТОМАТ",
                              font=('Consolas', 32, 'bold'),
                              bg=self.colors['primary'],
                              fg=self.colors['text_light'])
        title_label.pack(pady=(15, 0))
        
        subtitle_label = tk.Label(header_frame,
                                  text="Система самостійної видачі книг",
                                  font=('Consolas', 14),
                                  bg=self.colors['primary'],
                                  fg='#A3D8FF')
        subtitle_label.pack(pady=(5, 15))
        
        main_container = tk.Frame(self.root, bg=self.colors['background'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=40, pady=30)
        
        left_column = ttk.Frame(main_container, style='Card.TFrame', padding=25)
        left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 20))
        
        screen_frame = tk.Frame(left_column, bg=self.colors['grey_light'], relief=tk.FLAT, bd=0)
        screen_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        screen_header = tk.Frame(screen_frame, bg=self.colors['primary'], height=50)
        screen_header.pack(fill=tk.X)
        screen_header.pack_propagate(False)
        
        tk.Label(screen_header, text="ІНТЕРАКТИВНИЙ ЕКРАН", 
                 font=('Consolas', 15, 'bold'),
                 bg=self.colors['primary'],
                 fg=self.colors['text_light']).pack(expand=True)
        
        self.status_label = tk.Label(screen_frame,
                                     text="",
                                     font=('Consolas', 18, 'bold'),
                                     bg=self.colors['grey_light'],
                                     fg=self.colors['text_dark'],
                                     justify=tk.CENTER,
                                     wraplength=450,
                                     pady=40)
        self.status_label.pack(fill=tk.BOTH, expand=True)
        
        input_frame = tk.Frame(left_column, bg=self.colors['panel_bg'])
        input_frame.pack(fill=tk.X, pady=(10, 20))
        
        tk.Label(input_frame,
                 text="ВВЕДІТЬ ОДНОРАЗОВИЙ КОД (OTP):",
                 font=('Consolas', 13, 'bold'),
                 bg=self.colors['panel_bg'],
                 fg=self.colors['text_dark']).pack(pady=(0, 10))
        
        self.otp_entry = ttk.Entry(input_frame,
                                   style='Otp.TEntry',
                                   width=8,
                                   justify=tk.CENTER)
        self.otp_entry.pack(pady=(0, 15))
        self.otp_entry.bind('<Return>', lambda e: self.verify_otp())
        
        button_frame = tk.Frame(left_column, bg=self.colors['panel_bg'])
        button_frame.pack(fill=tk.X)
        
        self.verify_btn = ttk.Button(button_frame,
                                     text="ПІДТВЕРДИТИ",
                                     style='Success.Flat.TButton',
                                     width=15,
                                     command=self.verify_otp)
        self.verify_btn.pack(side=tk.LEFT, expand=True, padx=(0, 10))
        
        self.clear_btn = ttk.Button(button_frame,
                                    text="ОЧИСТИТИ",
                                    style='Light.Flat.TButton',
                                    width=15,
                                    command=self.clear_otp)
        self.clear_btn.pack(side=tk.LEFT, expand=True)
        
        self.timer_label = tk.Label(left_column,
                                     text="",
                                     font=('Consolas', 14, 'bold'),
                                     bg=self.colors['panel_bg'],
                                     fg=self.colors['danger'])
        self.timer_label.pack(pady=20)
        
        right_column = tk.Frame(main_container, bg=self.colors['background'])
        right_column.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        cells_header = tk.Frame(right_column, bg=self.colors['text_dark'], height=50)
        cells_header.pack(fill=tk.X)
        cells_header.pack_propagate(False)
        
        tk.Label(cells_header,
                 text="ОГЛЯД КОМІРОК",
                 font=('Consolas', 15, 'bold'),
                 bg=self.colors['text_dark'],
                 fg=self.colors['text_light']).pack(expand=True)
        
        # Контейнер для комірок
        cells_container = tk.Frame(right_column, bg=self.colors['background'])
        cells_container.pack(fill=tk.BOTH, expand=True, pady=20)
        
        self.cell_widgets = {}
        
        for col in range(3):
            cells_container.grid_columnconfigure(col, weight=1, uniform='cell')
        for row in range(2):
            cells_container.grid_rowconfigure(row, weight=1, uniform='cell')
        
        cell_ids = sorted(self.locker_cells.keys())
        for i, cell_id in enumerate(cell_ids):
            row = i // 3
            col = i % 3
            
            cell_frame = tk.Frame(cells_container,
                                  bg=self.colors['panel_bg'],
                                  relief=tk.FLAT,
                                  bd=1,
                                  highlightbackground=self.colors['grey_light'],
                                  highlightthickness=1)
            cell_frame.grid(row=row, column=col, padx=10, pady=30, sticky='nsew')
            
            status_icon = tk.Label(cell_frame,
                                   text="🔒",
                                   font=('Consolas', 30),
                                   bg=self.colors['panel_bg'],
                                   fg=self.colors['primary'])
            status_icon.pack(pady=(25, 10))
            
            cell_id_label = tk.Label(cell_frame,
                                     text=f"КОМІРКА {cell_id}",
                                     font=('Consolas', 14, 'bold'),
                                     bg=self.colors['panel_bg'],
                                     fg=self.colors['text_dark'])
            cell_id_label.pack()

            status_label = tk.Label(cell_frame,
                                    text="ЗАБЛОКОВАНА",
                                    font=('Consolas', 11),
                                    bg=self.colors['panel_bg'],
                                    fg=self.colors['primary'])
            status_label.pack(pady=(5, 20))
            
            self.cell_widgets[cell_id] = {
                'frame': cell_frame,
                'icon': status_icon,
                'id_label': cell_id_label,
                'status': status_label
            }
        
        total_cells = len(cell_ids)
        if total_cells < 6:
            for i in range(total_cells, 6):
                row = i // 3
                col = i % 3
                empty_frame = tk.Frame(cells_container, bg=self.colors['background'])
                empty_frame.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
        
        log_frame = tk.Frame(self.root, bg=self.colors['panel_bg'], relief=tk.FLAT, bd=0)
        log_frame.pack(fill=tk.X, padx=40, pady=(0, 20))
        
        log_header = tk.Frame(log_frame, bg=self.colors['text_dark'], height=30)
        log_header.pack(fill=tk.X)
        log_header.pack_propagate(False)
        
        tk.Label(log_header,
                 text="ЖУРНАЛ СИСТЕМИ",
                 font=('Consolas', 11, 'bold'),
                 bg=self.colors['text_dark'],
                 fg=self.colors['text_light']).pack(expand=True)
        
        self.log_text = tk.Text(log_frame,
                                 height=4,
                                 font=('Consolas', 10),
                                 bg='#2C3E50',
                                 fg='#76F77B', 
                                 state=tk.DISABLED,
                                 relief=tk.FLAT)
        self.log_text.pack(fill=tk.X, pady=(0, 5))
        
        self.create_menu()
        
    def create_menu(self):
        menubar = tk.Menu(self.root, bg=self.colors['panel_bg'], fg=self.colors['text_dark'])
        self.root.config(menu=menubar)
        
        admin_menu = tk.Menu(menubar, tearoff=0, bg=self.colors['panel_bg'], fg=self.colors['text_dark'])
        menubar.add_cascade(label="Управління", menu=admin_menu)
        admin_menu.add_command(label="Відкрити комірку (Адмін)", command=self.admin_unlock_cell)
        admin_menu.add_command(label="Примусово завершити (Адмін)", command=self.admin_force_confirm)
        admin_menu.add_separator()
        admin_menu.add_command(label="Перезавантажити Систему", command=self.reset_system)
        
    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, log_entry)
        
        if int(self.log_text.index('end-1c').split('.')[0]) > 50:
            self.log_text.delete(1.0, 2.0)
            
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        
    def update_status(self, message, color=None):
        if not color:
            color = self.colors['text_dark']
            
        self.status_label.config(text=message, fg=color)
        self.log(message)
        
    def clear_otp(self):
        self.otp_entry.delete(0, tk.END)
        
    def verify_otp(self):
        otp = self.otp_entry.get().strip()
        
        if len(otp) != 6 or not otp.isdigit():
            self.update_status("Помилка: OTP має містити 6 цифр", self.colors['danger'])
            messagebox.showerror("Помилка", "OTP має містити рівно 6 цифр")
            return
        
        self.update_status("Перевірка OTP...", self.colors['primary'])
        self.verify_btn.state(['disabled'])
        self.otp_entry.config(state=tk.DISABLED)
        
        threading.Thread(target=self._verify_otp_async, args=(otp,), daemon=True).start()
        
    def _verify_otp_async(self, otp):
        try:
            response = requests.post(
                f"{self.server_url}/iot/lockers/unlock",
                json={"otp": otp},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                self.current_session.update({
                    "locker_id": data.get('locker_id'),
                    "book_id": data.get('book_id'),
                    "user_id": data.get('user_id'),
                    "unlock_time": time.time()
                })
                
                self.root.after(0, self.unlock_cell, data.get('locker_id'))
            else:
                error_msg = response.json().get('error', 'Невідома помилка')
                self.root.after(0, self.show_error, error_msg)
                
        except requests.exceptions.RequestException as e:
            self.root.after(0, self.show_error, f"Помилка з'єднання: {str(e)}")
            
    def show_error(self, message):
        self.update_status(f"Помилка: {message}", self.colors['danger'])
        messagebox.showerror("Помилка", message)
        self.clear_otp()
        self.otp_entry.config(state=tk.NORMAL)
        self.verify_btn.state(['!disabled'])
        
    def unlock_cell(self, locker_id):
        if locker_id not in self.locker_cells:
            self.show_error(f"Комірка {locker_id} не існує")
            return
        
        self.log(f"Відкриття комірки {locker_id}")
        
        cell = self.cell_widgets[locker_id]
        cell['frame'].config(bg=self.colors['secondary'], highlightbackground=self.colors['secondary'])
        cell['icon'].config(text="🔓", fg=self.colors['text_light'], bg=self.colors['secondary'])
        cell['status'].config(text="ВІДКРИТА - ЗАБЕРІТЬ", fg=self.colors['text_light'], bg=self.colors['secondary'], font=('Consolas', 11, 'bold'))
        
        self.locker_cells[locker_id]['open'] = True
        
        self.update_status(
            f"Комірка {locker_id} відкрита!\nЗаберіть книгу протягом 60 секунд.",
            self.colors['secondary']
        )
        
        self.otp_entry.config(state=tk.DISABLED)
        self.verify_btn.state(['disabled'])
        self.clear_btn.state(['disabled'])

        self.otp_entry.config(state=tk.DISABLED)
        self.verify_btn.state(['disabled'])
        self.clear_btn.state(['disabled'])
        
        self.start_pickup_timer()
        
    def start_pickup_timer(self):
        timeout = 60
        
        def countdown():
            if not self.current_session['unlock_time']:
                return
                
            remaining = timeout - int(time.time() - self.current_session['unlock_time'])
            
            if remaining <= 0:
                self.root.after(0, self.confirm_pickup_dialog)
            else:
                timer_color = self.colors['danger'] if remaining < 10 else self.colors['primary']
                self.timer_label.config(
                    text=f"⏳ Лишилося {remaining} сек на те, аби забрати книгу",
                    fg=timer_color
                )
                self.root.after(1000, countdown)
        
        countdown()
        
    def confirm_pickup_dialog(self):
        result = messagebox.askyesno(
            "Підтвердження",
            "Ви забрали книгу з комірки? Натисніть ТАК, щоб підтвердити позику.",
            icon='question'
        )
        
        if result:
            self.confirm_pickup()
        else:
            self.cancel_pickup()
            
    def confirm_pickup(self):
        locker_id = self.current_session['locker_id']
        
        if not locker_id:
            return
            
        self.update_status("...Підтвердження видачі...", self.colors['primary'])

        threading.Thread(target=self._confirm_pickup_async, daemon=True).start()
        
    def _confirm_pickup_async(self):
        locker_id = self.current_session['locker_id']
        try:
            response = requests.post(
                f"{self.server_url}/iot/lockers/confirm_pickup",
                json={
                    "user_id": self.current_session['user_id'],
                    "book_id": self.current_session['book_id']
                },
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                loan_id = data.get('loan_id')
                due_date = data.get('due_date')
                
                self.root.after(0, lambda: self.update_status(
                    f"🎉 Успішно!\nПозика #{loan_id}\nТермін: {due_date[:10]}\n\nПриємного читання!",
                    self.colors['secondary']
                ))
                
                self.log(f"Книгу видано (Позика #{loan_id})")
                self.root.after(0, self.close_cell, locker_id)
                
                self.root.after(0, lambda: messagebox.showinfo(
                    "Успіх!",
                    f"Книгу видано!\nПозика #{loan_id}\n"
                    f"Повернути до: {due_date[:10]}"
                ))
                
                self.root.after(3000, self.reset_session)
            else:
                error = response.json().get('error', 'Невідома помилка')
                self.root.after(0, self.show_error, error)
                
        except requests.exceptions.RequestException as e:
            self.root.after(0, self.show_error, f"Помилка підтвердження: {str(e)}")
            
    def cancel_pickup(self):
        locker_id = self.current_session['locker_id']
        
        self.log(f"Книгу не забрано з комірки {locker_id}")
        self.update_status("Книгу не забрано. Комірка закривається...", self.colors['danger'])
        
        self.close_cell(locker_id)
        
        messagebox.showwarning(
            "Увага",
            "Книгу не забрано вчасно. Комірка заблокована.\nСпробуйте знову пізніше."
        )
        
        self.root.after(2000, self.reset_session)
        
    def close_cell(self, locker_id):
        self.log(f"Закриття комірки {locker_id}")
        
        if locker_id not in self.cell_widgets:
             self.log(f"Помилка: Віджет для комірки {locker_id} не знайдено.")
             return
             
        cell = self.cell_widgets[locker_id]
        cell['frame'].config(bg=self.colors['panel_bg'], highlightbackground=self.colors['grey_light'])
        cell['icon'].config(text="🔒", fg=self.colors['primary'], bg=self.colors['panel_bg'])
        cell['status'].config(text="ЗАБЛОКОВАНА", fg=self.colors['primary'], bg=self.colors['panel_bg'], font=('Consolas', 11))
        
        self.locker_cells[locker_id]['open'] = False
        self.locker_cells[locker_id]['occupied'] = False
        self.locker_cells[locker_id]['book_id'] = None
        
    def reset_session(self):
        self.current_session = {
            "locker_id": None,
            "book_id": None,
            "user_id": None,
            "unlock_time": None
        }
        
        self.update_status("Вітаємо! Введіть OTP код для отримання книги", self.colors['text_dark'])
        self.timer_label.config(text="")
        self.clear_otp()
        self.otp_entry.config(state=tk.NORMAL)
        self.verify_btn.state(['!disabled'])
        self.clear_btn.state(['!disabled'])
        
    def admin_unlock_cell(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Відкрити комірку (Адмін)")
        dialog.geometry("300x150")
        dialog.configure(bg=self.colors['panel_bg'])
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, 
                 text="Виберіть комірку:",
                 bg=self.colors['panel_bg'],
                 fg=self.colors['text_dark'],
                 font=('Consolas', 11, 'bold')).pack(pady=15)
        
        locker_var = tk.StringVar()
        locker_combo = ttk.Combobox(dialog, 
                                    textvariable=locker_var,
                                    values=list(self.locker_cells.keys()),
                                    state='readonly',
                                    style='TCombobox')
        locker_combo.pack(pady=10)
        
        def unlock():
            locker_id = locker_var.get()
            if locker_id:
                self.current_session['locker_id'] = locker_id
                self.current_session['book_id'] = f"BOOK-{locker_id}"
                self.current_session['user_id'] = "ADMIN-001"
                self.current_session['unlock_time'] = time.time()
                self.unlock_cell(locker_id)
                dialog.destroy()
        
        ttk.Button(dialog,
                   text="Відкрити",
                   command=unlock,
                   style='Flat.TButton',
                   width=10).pack(pady=10)
        
    def admin_force_confirm(self):
        if self.current_session["locker_id"] is None:
            messagebox.showinfo("Інформація", "Немає активної сесії видачі.")
            return
        self.log(f"Адмін: Примусове завершення сесії для комірки {self.current_session['locker_id']}")
        self.confirm_pickup_dialog()

    def reset_system(self):
        for locker_id in self.locker_cells:
            if self.locker_cells[locker_id]['open']:
                self.close_cell(locker_id)
        
        self.reset_session()
        self.log("СИСТЕМА ПЕРЕЗАВАНТАЖЕНА")
        messagebox.showinfo("Система", "Поштомат перезавантажено")