import os
from duplicates import calculate_file_hash

def get_relative_paths(files_info, base_path):
    """Преобразует абсолютные пути в относительные."""
    relative_paths = set()
    for file in files_info:
        rel_path = os.path.relpath(file['path'], base_path)  # Используем os.path.relpath
        relative_paths.add(rel_path)
    return relative_paths

def compare_files_by_hash(file1_path, file2_path):
    """Сравнивает два файла по хэшу."""
    return calculate_file_hash(file1_path) == calculate_file_hash(file2_path)

def compare_folders(source_path, backup_path, extension=None):
    """
    Сравнивает исходную папку и бэкап.
    Возвращает:
    - missing_in_backup: файлы, которых нет в бэкапе
    - extra_in_backup: файлы, которых нет в исходной папке
    - modified_files: файлы, которые есть в обеих папках, но отличаются по хэшу
    """
    from scanner import get_files_recursive

    source_files = get_files_recursive(source_path, extension)
    backup_files = get_files_recursive(backup_path, extension)

    source_relative = get_relative_paths(source_files, source_path)
    backup_relative = get_relative_paths(backup_files, backup_path)

    # Файлы, которых нет в бэкапе
    missing_in_backup = source_relative - backup_relative

    # Файлы, которых нет в исходной папке
    extra_in_backup = backup_relative - source_relative

    # Файлы, которые есть в обеих папках
    common_files = source_relative & backup_relative

    # Сравниваем файлы по хэшу
    modified_files = set()
    for rel_path in common_files:
        # Находим абсолютные пути
        source_file_path = os.path.join(source_path, rel_path)
        backup_file_path = os.path.join(backup_path, rel_path)

        # Сравниваем хэши
        if not compare_files_by_hash(source_file_path, backup_file_path):
            modified_files.add(rel_path)

    return {
        'missing_in_backup': missing_in_backup,
        'extra_in_backup': extra_in_backup,
        'modified_files': modified_files
    }