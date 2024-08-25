from pathlib import Path
import sys
from file_manager import rename_to_temp, rename_to_final, restore_files
from gui import create_gui, show_messagebox, show_errorbox, load_files

# exe file path
if getattr(sys, 'frozen', False):
    application_path = Path(sys.executable).parent
else:
    application_path = Path(__file__).parent

backup_file = application_path / "filename_backup.json"

def start_renaming(folder_entry, sort_option, prefix_entry, digits_entry, file_listbox):
    directory = folder_entry.get()
    if not Path(directory).is_dir():
        show_errorbox("오류", "유효한 디렉터리를 입력하세요.")
        return
    
    sort_by = "modification" if sort_option.get() == 2 else "creation"
    prefix = prefix_entry.get()
    digits = digits_entry.get() or "4"

    try:
        number_format = f"0{int(digits)}d"
    except ValueError:
        show_errorbox("오류", "숫자 자리수는 정수여야 합니다.")
        return

    files = [f for f in Path(directory).iterdir() if f.is_file()]


    exe_file = Path(sys.executable) if getattr(sys, 'frozen', False) else None
    files = [f for f in files if f != exe_file and f.name != backup_file.name]

    if sort_by == "creation":
        files.sort(key=lambda f: f.stat().st_ctime)
    else:
        files.sort(key=lambda f: f.stat().st_mtime)

    temp_names, timestamps = rename_to_temp(files)
    rename_to_final(temp_names, timestamps, directory, number_format, prefix, backup_file)
    
    show_messagebox("완료", "파일 이름 변경이 완료되었습니다!")
    load_files(directory, file_listbox)

def start_restoring(folder_entry, file_listbox):
    directory = folder_entry.get()
    if not Path(directory).is_dir():
        show_errorbox("오류", "유효한 디렉터리를 입력하세요.")
        return

    restored_files, failed_files = restore_files(directory, backup_file)
    if restored_files is None:
        show_errorbox("오류", "복원할 백업 데이터가 없습니다.")
        return

    if restored_files:
        show_messagebox("복원 완료", f"다음 파일들이 성공적으로 복원되었습니다:\n{'\n'.join(restored_files)}")
    if failed_files:
        show_errorbox("복원 실패", f"다음 파일들은 복원할 수 없었습니다:\n{'\n'.join(failed_files)}")

    load_files(directory, file_listbox)

if __name__ == "__main__":
    create_gui(start_renaming, start_restoring, load_files)
