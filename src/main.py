import os
import sys
import hashlib
from datetime import datetime

def get_files_recursive(folder_path):
    """Рекурсивно собирает все файлы в папке и подпапках."""
    files_info = []
    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        if os.path.isdir(item_path):
            files_info.extend(get_files_recursive(item_path))
        elif os.path.isfile(item_path):
            file_size = os.path.getsize(item_path)
            file_modified = datetime.fromtimestamp(os.path.getmtime(item_path)).strftime('%Y-%m-%d %H:%M:%S')
            files_info.append({
                'path': item_path,
                'size': file_size,
                'modified': file_modified
            })
    return files_info

def calculate_file_hash(file_path, chunk_size=8192):
    """Считает хэш файла (MD5)."""
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        while chunk := f.read(chunk_size):
            hasher.update(chunk)
    return hasher.hexdigest()

def find_duplicates(files_info):
    """Находит дубликаты файлов по хэшу."""
    hash_to_files = {}
    for file in files_info:
        file_hash = calculate_file_hash(file['path'])
        if file_hash not in hash_to_files:
            hash_to_files[file_hash] = []
        hash_to_files[file_hash].append(file['path'])
    # Оставляем только группы с 2+ файлами
    duplicates = {h: paths for h, paths in hash_to_files.items() if len(paths) > 1}
    return duplicates

def print_duplicates(duplicates):
    """Выводит группы дубликатов."""
    if not duplicates:
        print("Дубликатов не найдено.")
        return
    for i, (file_hash, paths) in enumerate(duplicates.items(), 1):
        print(f"Группа {i} (хэш: {file_hash}):")
        for path in paths:
            print(f"  - {path}")
        print("-" * 40)

def main():
    if len(sys.argv) < 2:
        print("Ошибка: не указан путь к папке.")
        print("Использование: python main.py <путь_к_папке>")
        return

    folder_path = sys.argv[1]
    if not os.path.isdir(folder_path):
        print(f"Ошибка: папка '{folder_path}' не существует.")
        return

    print(f"Сканирую папку: {folder_path}")
    files_info = get_files_recursive(folder_path)
    duplicates = find_duplicates(files_info)
    print("\nДубликаты:")
    print_duplicates(duplicates)

if __name__ == "__main__":
    main()