import os
import time

def get_files_recursive(folder_path, extension=None):
    """Рекурсивно собирает все файлы в папке и подпапках."""
    files_info = []
    try:
        items = os.listdir(folder_path)
    except OSError:
        return files_info

    for item in items:
        item_path = os.path.join(folder_path, item)  # Используем os.path.join
        try:
            stat_info = os.stat(item_path)
            is_dir = stat_info.st_mode & 0o40000  # Проверка, что это папка
            if is_dir:
                files_info.extend(get_files_recursive(item_path, extension))
            else:
                # Проверяем расширение файла, если оно указано
                if extension and not item.endswith(f".{extension}"):
                    continue  # Пропускаем файлы с другим расширением
                file_size = stat_info.st_size
                file_modified = time.ctime(stat_info.st_mtime)
                files_info.append({
                    'path': item_path,
                    'size': file_size,
                    'modified': file_modified
                })
        except OSError:
            continue
    return files_info