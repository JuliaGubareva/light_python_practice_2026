import os
import sys
from datetime import datetime

def get_files_recursive(folder_path):
    """Рекурсивно собирает все файлы в папке и подпапках."""
    files_info = []
    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        if os.path.isdir(item_path):
            # Рекурсивно обрабатываем подпапку
            files_info.extend(get_files_recursive(item_path))
        elif os.path.isfile(item_path):
            # Собираем данные о файле
            file_size = os.path.getsize(item_path)
            file_modified = datetime.fromtimestamp(os.path.getmtime(item_path)).strftime('%Y-%m-%d %H:%M:%S')
            files_info.append({
                'path': item_path,
                'size': file_size,
                'modified': file_modified
            })
    return files_info

def print_files_info(files_info):
    """Выводит информацию о файлах в консоль."""
    for file in files_info:
        print(f"Путь: {file['path']}")
        print(f"Размер: {file['size']} байт")
        print(f"Дата изменения: {file['modified']}")
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
    print_files_info(files_info)

if __name__ == "__main__":
    main()