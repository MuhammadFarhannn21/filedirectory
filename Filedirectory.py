import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import shutil
from datetime import datetime

class FileExplorer:
    def __init__(self, master):
        self.master = master
        self.master.title("File Explorer Canggih")
        self.master.geometry("800x600")

        self.current_path = os.getcwd()
        self.history = [self.current_path]
        self.history_index = 0

        self.setup_ui()
        self.refresh_list()

    def setup_ui(self):
        # Frame utama
        main_frame = ttk.Frame(self.master, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Toolbar
        toolbar = ttk.Frame(main_frame)
        toolbar.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(toolbar, text="⬅", command=self.go_back, width=3).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="➡", command=self.go_forward, width=3).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="⬆", command=self.go_up, width=3).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="🔄", command=self.refresh_list, width=3).pack(side=tk.LEFT, padx=2)

        self.path_var = tk.StringVar()
        self.path_var.set(self.current_path)
        path_entry = ttk.Entry(toolbar, textvariable=self.path_var, width=70)
        path_entry.pack(side=tk.LEFT, padx=5)
        path_entry.bind("<Return>", lambda e: self.go_to_path())

        ttk.Button(toolbar, text="Buka", command=self.go_to_path).pack(side=tk.LEFT, padx=2)

        # Treeview untuk menampilkan file dan folder
        self.tree = ttk.Treeview(main_frame, columns=("Size", "Type", "Date Modified"), selectmode="browse")
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.tree.heading("#0", text="Nama", anchor=tk.W)
        self.tree.heading("Size", text="Ukuran", anchor=tk.W)
        self.tree.heading("Type", text="Tipe", anchor=tk.W)
        self.tree.heading("Date Modified", text="Tanggal Modifikasi", anchor=tk.W)

        self.tree.column("#0", width=300, minwidth=200)
        self.tree.column("Size", width=100, minwidth=80)
        self.tree.column("Type", width=100, minwidth=80)
        self.tree.column("Date Modified", width=150, minwidth=100)

        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.bind("<Double-1>", self.on_double_click)
        self.tree.bind("<Return>", self.on_double_click)

        # Menu konteks
        self.context_menu = tk.Menu(self.master, tearoff=0)
        self.context_menu.add_command(label="Buka", command=self.open_item)
        self.context_menu.add_command(label="Salin", command=self.copy_item)
        self.context_menu.add_command(label="Potong", command=self.cut_item)
        self.context_menu.add_command(label="Tempel", command=self.paste_item)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Hapus", command=self.delete_item)
        self.context_menu.add_command(label="Ubah nama", command=self.rename_item)

        self.tree.bind("<Button-3>", self.show_context_menu)

    def refresh_list(self):
        self.tree.delete(*self.tree.get_children())
        try:
            for item in os.listdir(self.current_path):
                full_path = os.path.join(self.current_path, item)
                size = os.path.getsize(full_path)
                modified_time = os.path.getmtime(full_path)
                modified_date = datetime.fromtimestamp(modified_time).strftime("%Y-%m-%d %H:%M:%S")
                
                if os.path.isdir(full_path):
                    self.tree.insert("", "end", text=item, values=("", "Folder", modified_date), tags=('folder',))
                else:
                    file_type = os.path.splitext(item)[1]
                    self.tree.insert("", "end", text=item, values=(f"{size:,} bytes", file_type, modified_date), tags=('file',))
            
            self.tree.tag_configure('folder', foreground='blue')
            self.tree.tag_configure('file', foreground='black')
        except PermissionError:
            messagebox.showerror("Error", "Tidak memiliki izin untuk mengakses direktori ini.")

        self.path_var.set(self.current_path)

    def go_to_path(self):
        new_path = self.path_var.get()
        if os.path.exists(new_path) and os.path.isdir(new_path):
            self.current_path = new_path
            self.add_to_history(new_path)
            self.refresh_list()
        else:
            messagebox.showerror("Error", "Path tidak valid atau bukan direktori.")

    def on_double_click(self, event):
        item = self.tree.selection()[0]
        item_text = self.tree.item(item, "text")
        new_path = os.path.join(self.current_path, item_text)
        if os.path.isdir(new_path):
            self.current_path = new_path
            self.add_to_history(new_path)
            self.refresh_list()
        else:
            os.startfile(new_path)

    def go_back(self):
        if self.history_index > 0:
            self.history_index -= 1
            self.current_path = self.history[self.history_index]
            self.refresh_list()

    def go_forward(self):
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.current_path = self.history[self.history_index]
            self.refresh_list()

    def go_up(self):
        parent_dir = os.path.dirname(self.current_path)
        if parent_dir != self.current_path:
            self.current_path = parent_dir
            self.add_to_history(parent_dir)
            self.refresh_list()

    def add_to_history(self, path):
        self.history = self.history[:self.history_index + 1]
        self.history.append(path)
        self.history_index = len(self.history) - 1

    def show_context_menu(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def open_item(self):
        self.on_double_click(None)

    def copy_item(self):
        item = self.tree.selection()[0]
        item_text = self.tree.item(item, "text")
        self.clipboard = os.path.join(self.current_path, item_text)
        self.clipboard_action = "copy"

    def cut_item(self):
        item = self.tree.selection()[0]
        item_text = self.tree.item(item, "text")
        self.clipboard = os.path.join(self.current_path, item_text)
        self.clipboard_action = "cut"

    def paste_item(self):
        if hasattr(self, 'clipboard') and os.path.exists(self.clipboard):
            dest = os.path.join(self.current_path, os.path.basename(self.clipboard))
            if self.clipboard_action == "copy":
                if os.path.isdir(self.clipboard):
                    shutil.copytree(self.clipboard, dest)
                else:
                    shutil.copy2(self.clipboard, dest)
            elif self.clipboard_action == "cut":
                shutil.move(self.clipboard, dest)
            self.refresh_list()

    def delete_item(self):
        item = self.tree.selection()[0]
        item_text = self.tree.item(item, "text")
        path = os.path.join(self.current_path, item_text)
        if messagebox.askyesno("Konfirmasi", f"Apakah Anda yakin ingin menghapus '{item_text}'?"):
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
            self.refresh_list()

    def rename_item(self):
        item = self.tree.selection()[0]
        old_name = self.tree.item(item, "text")
        new_name = simpledialog.askstring("Ubah nama", "Masukkan nama baru:", initialvalue=old_name)
        if new_name:
            old_path = os.path.join(self.current_path, old_name)
            new_path = os.path.join(self.current_path, new_name)
            os.rename(old_path, new_path)
            self.refresh_list()

if __name__ == "__main__":
    root = tk.Tk()
    app = FileExplorer(root)
    root.mainloop()