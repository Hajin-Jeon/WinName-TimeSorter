import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path

def create_gui(start_renaming, start_restoring, load_files):
    root = tk.Tk()
    root.title("파일 이름 변경기")

    folder_label = tk.Label(root, text="폴더 경로:")
    folder_label.grid(row=0, column=0, padx=10, pady=10)
    folder_entry = tk.Entry(root, width=50)
    folder_entry.grid(row=0, column=1, padx=10, pady=10)
    
    file_listbox = tk.Listbox(root, width=50, height=10)
    file_listbox.grid(row=4, column=0, columnspan=3, padx=10, pady=10)
    
    folder_button = tk.Button(root, text="폴더 선택", command=lambda: select_directory(folder_entry, file_listbox, load_files))
    folder_button.grid(row=0, column=2, padx=10, pady=10)

    sort_option = tk.IntVar(value=1)
    tk.Radiobutton(root, text="생성일 기준", variable=sort_option, value=1).grid(row=1, column=0, padx=10, pady=10)
    tk.Radiobutton(root, text="최종 수정일 기준", variable=sort_option, value=2).grid(row=1, column=1, padx=10, pady=10)

    prefix_label = tk.Label(root, text="접두사:")
    prefix_label.grid(row=2, column=0, padx=10, pady=10)
    prefix_entry = tk.Entry(root)
    prefix_entry.grid(row=2, column=1, padx=10, pady=10)

    digits_label = tk.Label(root, text="숫자 자리수 (기본값: 4):")
    digits_label.grid(row=3, column=0, padx=10, pady=10)
    digits_entry = tk.Entry(root)
    digits_entry.grid(row=3, column=1, padx=10, pady=10)
    digits_entry.insert(0, "4")

    start_button = tk.Button(root, text="시작", command=lambda: start_renaming(folder_entry, sort_option, prefix_entry, digits_entry, file_listbox))
    start_button.grid(row=5, column=1, padx=10, pady=10)

    restore_button = tk.Button(root, text="복원", command=lambda: start_restoring(folder_entry, file_listbox))
    restore_button.grid(row=6, column=1, padx=10, pady=10)

    root.mainloop()

def select_directory(folder_entry, file_listbox, load_files):
    directory = filedialog.askdirectory()
    if directory:
        folder_entry.delete(0, tk.END)
        folder_entry.insert(0, directory)
        load_files(directory, file_listbox)

def load_files(directory, file_listbox):
    file_listbox.delete(0, tk.END)
    try:
        files = [f.name for f in Path(directory).iterdir() if f.is_file()]
        for file in files:
            file_listbox.insert(tk.END, file)
    except Exception as e:
        show_errorbox("오류", f"파일을 로드하는 중 오류가 발생했습니다: {e}")

def show_messagebox(title, message):
    messagebox.showinfo(title, message)

def show_errorbox(title, message):
    messagebox.showerror(title, message)
