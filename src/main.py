import sys
import os
from scanner import get_files_recursive
from duplicates import find_duplicates
from comparison import compare_folders, get_relative_paths

def print_files_info(files_info):
    """Выводит информацию о файлах."""
    if not files_info:
        print("Файлы с указанным расширением не найдены.")
        return
    for file in files_info:
        print(f"Путь: {file['path']}")
        print(f"Размер: {file['size']} байт")
        print(f"Дата изменения: {file['modified']}")
        print("-" * 40)

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

def print_comparison_results(results):
    """Выводит результаты сравнения папок."""
    print("\nРазличия между исходной папкой и бэкапом:")
    print("-" * 40)
    if results['missing_in_backup']:
        print("Файлы, которых нет в бэкапе:")
        for file in results['missing_in_backup']:
            print(f"  - {file}")
    else:
        print("Новых или измененных файлов нет.")
    print("-" * 40)
    if results['extra_in_backup']:
        print("Файлы, которых нет в исходной папке:")
        for file in results['extra_in_backup']:
            print(f"  - {file}")
    else:
        print("Удаленных или лишних файлов в бэкапе нет.")
    print("-" * 40)
    if results['modified_files']:
        print("Измененные файлы (отличаются по хэшу):")
        for file in results['modified_files']:
            print(f"  - {file}")
    else:
        print("Измененных файлов нет.")

def main():
    if len(sys.argv) < 2:
        print("Ошибка: не указан путь к папке.")
        print("Использование:")
        print("  Для сканирования: python main.py <путь_к_папке> [--ext <расширение>]")
        print("  Для сравнения: python main.py <путь_к_исходной_папке> <путь_к_бэкапу> [--ext <расширение>]")
        return

    # Парсим аргументы
    extension = None
    args = sys.argv[1:]
    if "--ext" in args:
        ext_index = args.index("--ext")
        if ext_index + 1 < len(args):
            extension = args[ext_index + 1]
            args = args[:ext_index] + args[ext_index + 2:]

    if len(args) == 1:
        # Режим сканирования
        folder_path = args[0]
        if not os.path.isdir(folder_path):
            print(f"Ошибка: папка '{folder_path}' не существует.")
            return
        print(f"Сканирую папку: {folder_path}")
        if extension:
            print(f"Фильтрация по расширению: .{extension}")
        files_info = get_files_recursive(folder_path, extension)
        print_files_info(files_info)
        duplicates = find_duplicates(files_info)
        print("\nДубликаты:")
        print_duplicates(duplicates)
    elif len(args) == 2:
        # Режим сравнения
        source_path = args[0]
        backup_path = args[1]
        if not os.path.isdir(source_path):
            print(f"Ошибка: папка '{source_path}' не существует.")
            return
        if not os.path.isdir(backup_path):
            print(f"Ошибка: папка '{backup_path}' не существует.")
            return
        print(f"Сравниваю папки: {source_path} и {backup_path}")
        if extension:
            print(f"Фильтрация по расширению: .{extension}")
        results = compare_folders(source_path, backup_path, extension)
        print_comparison_results(results)
    else:
        print("Ошибка: неверное количество аргументов.")

if __name__ == "__main__":
    main()