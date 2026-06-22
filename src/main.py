import os
import sys
import time
import hashlib  # Добавили импорт для работы с MD5-хэшем

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

def calculate_file_hash(file_path):
    """Считает MD5-хэш файла."""
    hasher = hashlib.md5() #!!!
    try:
        with open(file_path, 'rb') as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
        return hasher.hexdigest()  # Возвращаем хэш в виде строки
    except OSError:
        return "0"  # Если файл недоступен, возвращаем дефолтное значение

def find_duplicates(files_info):
    """Находит дубликаты файлов по хэшу."""
    hash_to_files = {}
    for file in files_info:
        file_hash = calculate_file_hash(file['path'])
        if file_hash not in hash_to_files:
            hash_to_files[file_hash] = []
        hash_to_files[file_hash].append(file['path'])
    duplicates = {h: paths for h, paths in hash_to_files.items() if len(paths) > 1}
    return duplicates

def get_relative_paths(files_info, base_path):
    """Преобразует абсолютные пути в относительные."""
    relative_paths = set()
    for file in files_info:
        rel_path = os.path.relpath(file['path'], base_path)  # Используем os.path.relpath
        relative_paths.add(rel_path)
    return relative_paths

def compare_folders(source_path, backup_path, extension=None):
    """Сравнивает исходную папку и бэкап."""
    source_files = get_files_recursive(source_path, extension)
    backup_files = get_files_recursive(backup_path, extension)

    source_relative = get_relative_paths(source_files, source_path)
    backup_relative = get_relative_paths(backup_files, backup_path)

    missing_in_backup = source_relative - backup_relative
    extra_in_backup = backup_relative - source_relative

    return {
        'missing_in_backup': missing_in_backup,
        'extra_in_backup': extra_in_backup
    }

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