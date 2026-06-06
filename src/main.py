import sys

def main():
    #Проверяем, что пользователь передал путь к папке
    if len(sys.argv) < 2:
        print("Ошибка: не указан путь к папке.")
        print("Использование: python main.py <путь_к_папке>")
        return

    folder_path = sys.argv[1]
    print(f"Указанный путь к папке: {folder_path}")

if __name__ == "__main__":
    main()