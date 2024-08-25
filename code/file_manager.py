import json
import uuid
from pathlib import Path
import win32file
import win32con
import pywintypes

# timestamp
def get_timestamps(filepath):
    stat = filepath.stat()
    creation_time = win32file.GetFileTime(win32file.CreateFile(str(filepath), win32con.GENERIC_READ, win32con.FILE_SHARE_READ, None, win32con.OPEN_EXISTING, win32con.FILE_ATTRIBUTE_NORMAL, None))[0]
    return {
        'creation_time': creation_time,
        'modification_time': stat.st_mtime,
        'access_time': stat.st_atime
    }

def set_timestamps(filepath, timestamps):
    handle = win32file.CreateFile(str(filepath), win32con.GENERIC_WRITE, win32con.FILE_SHARE_WRITE, None, win32con.OPEN_EXISTING, win32con.FILE_ATTRIBUTE_NORMAL, None)
    win32file.SetFileTime(handle, timestamps['creation_time'], pywintypes.Time(timestamps['access_time']), pywintypes.Time(timestamps['modification_time']))
    handle.close()

# save as temporary name
def rename_to_temp(files):
    temp_names = {}
    timestamps = {}

    for file in files:
        temp_name = str(uuid.uuid4()) + file.suffix  # 무작위 임시 이름 생성
        temp_path = file.with_name(temp_name)

        # 파일의 타임스탬프 저장
        timestamps[str(temp_path)] = get_timestamps(file)

        # 임시 이름으로 변경
        temp_names[str(temp_path)] = str(file.name)  # 임시 이름과 원래 이름 저장
        file.rename(temp_path)

    return temp_names, timestamps

# save as target name
def rename_to_final(temp_names, timestamps, directory, number_format, prefix, backup_file):
    backup_data = {}

    for index, temp_name in enumerate(temp_names.keys()):
        temp_path = Path(temp_name)
        number = format(index + 1, number_format)
        new_name = f"{prefix}{number}{temp_path.suffix}"
        new_path = temp_path.with_name(new_name)

        backup_data[str(new_path)] = temp_names[str(temp_path)]  # original name
        temp_path.rename(new_path)

        set_timestamps(new_path, timestamps[str(temp_path)])

    with open(backup_file, "w") as f:
        json.dump(backup_data, f)

def restore_files(directory, backup_file):
    if not backup_file.exists():
        return None, "복원할 백업 데이터가 없습니다."

    with open(backup_file, "r") as f:
        backup_data = json.load(f)

    restored_files = []
    failed_files = []

    new_backup_data = {}

    temp_names = {}
    timestamps = {}

    for new_name, old_name in backup_data.items():
        new_path = Path(directory) / new_name
        if new_path.exists():
            temp_name = str(uuid.uuid4()) + new_path.suffix
            temp_path = new_path.with_name(temp_name)

            timestamps[str(temp_path)] = get_timestamps(new_path)

            temp_names[str(temp_path)] = old_name
            new_path.rename(temp_path)

    for temp_name, old_name in temp_names.items():
        temp_path = Path(temp_name)
        old_path = Path(directory) / old_name

        try:
            temp_path.rename(old_path)
            set_timestamps(old_path, timestamps[str(temp_path)])
            restored_files.append(old_name)
        except Exception as e:
            failed_files.append(f"{temp_name} -> {old_name}: {e}")

    with open(backup_file, "w") as f:
        json.dump(new_backup_data, f)

    return restored_files, failed_files
