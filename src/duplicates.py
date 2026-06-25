import hashlib

def calculate_file_hash(file_path):
    """Считает MD5-хэш файла."""
    hasher = hashlib.md5()
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

def compare_files_by_hash(file1_path, file2_path):
    """Сравнивает два файла по хэшу."""
    return calculate_file_hash(file1_path) == calculate_file_hash(file2_path)