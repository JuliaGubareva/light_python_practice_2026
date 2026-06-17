import os
import sys
import time

# --- Этап 1 и 2: Рекурсивный обход и сбор метаданных ---
def get_files_recursive(folder_path):
    """Рекурсивно собирает все файлы в папке и подпапках."""
    files_info = []
    try:
        items = os.listdir(folder_path)
    except OSError:
        return files_info  # Если нет доступа, возвращаем пустой список

    for item in items:
        item_path = folder_path + "/" + item  # Ручная конкатенация путей
        try:
            stat_info = os.stat(item_path)
            is_dir = stat_info.st_mode & 0o40000  # Проверка, что это папка (0o40000 — флаг для папки в Unix)
            if is_dir:
                files_info.extend(get_files_recursive(item_path))
            else:
                # Собираем метаданные вручную
                file_size = stat_info.st_size
                file_modified = time.ctime(stat_info.st_mtime)
                files_info.append({
                    'path': item_path,
                    'size': file_size,
                    'modified': file_modified
                })
        except OSError:
            continue  # Пропускаем файлы/папки, к которым нет доступа
    return files_info

# --- Этап 3: Поиск дубликатов ---
def calculate_file_hash(file_path):
    """Считает простой хэш (контрольная сумма)."""
    file_hash = 0
    try:
        with open(file_path, 'rb') as f:
            while True:
                chunk = f.read(8192)  # Читаем файл частями
                if not chunk:
                    break
                file_hash = sum(chunk) + file_hash  # Сумма всех байтов
    except OSError:
        return "0"  # Если файл недоступен, возвращаем дефолтное значение
    return str(file_hash)

def find_duplicates(files_info):
    """Находит дубликаты файлов по хэшу."""
    hash_to_files = {}
    for file in files_info:
        file_hash = calculate_file_hash(file['path'])
        if file_hash not in hash_to_files:
            hash_to_files[file_hash] = []
        hash_to_files[file_hash].append(file['path'])
    # Оставляем только группы с 2+ файлами
    duplicates = {}
    for h, paths in hash_to_files.items():
        if len(paths) > 1:
            duplicates[h] = paths
    return duplicates

# --- Этап 4: Сравнение папок ---
def get_relative_paths(files_info, base_path):
    """Преобразует абсолютные пути в относительные."""
    relative_paths = set()
    base_length = len(base_path)
    for file in files_info:
        rel_path = file['path'][base_length + 1:]  # Убираем base_path и разделитель
        relative_paths.add(rel_path)
    return relative_paths

def compare_folders(source_path, backup_path):
    """Сравнивает исходную папку и бэкап."""
    source_files = get_files_recursive(source_path)
    backup_files = get_files_recursive(backup_path)

    source_relative = get_relative_paths(source_files, source_path)
    backup_relative = get_relative_paths(backup_files, backup_path)

    missing_in_backup = source_relative - backup_relative
    extra_in_backup = backup_relative - source_relative

    return {
        'missing_in_backup': missing_in_backup,
        'extra_in_backup': extra_in_backup
    }

# --- Вывод результатов ---
def print_files_info(files_info):
    """Выводит информацию о файлах."""
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

# --- Основная функция ---
def main():
    if len(sys.argv) < 2:
        print("Ошибка: не указан путь к папке.")
        print("Использование:")
        print("  Для сканирования: python main.py <путь_к_папке>")
        print("  Для сравнения: python main.py <путь_к_исходной_папке> <путь_к_бэкапу>")
        return

    if len(sys.argv) == 2:
        # Режим сканирования (этапы 1-3)
        folder_path = sys.argv[1]
        if not os.path.isdir(folder_path):
            print(f"Ошибка: папка '{folder_path}' не существует.")
            return
        print(f"Сканирую папку: {folder_path}")
        files_info = get_files_recursive(folder_path)
        print_files_info(files_info)
        duplicates = find_duplicates(files_info)
        print("\nДубликаты:")
        print_duplicates(duplicates)
    elif len(sys.argv) == 3:
        # Режим сравнения (этап 4)
        source_path = sys.argv[1]
        backup_path = sys.argv[2]
        if not os.path.isdir(source_path):
            print(f"Ошибка: папка '{source_path}' не существует.")
            return
        if not os.path.isdir(backup_path):
            print(f"Ошибка: папка '{backup_path}' не существует.")
            return
        print(f"Сравниваю папки: {source_path} и {backup_path}")
        results = compare_folders(source_path, backup_path)
        print_comparison_results(results)

if __name__ == "__main__":
    main()