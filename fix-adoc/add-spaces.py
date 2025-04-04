import os

def replace_sequence_in_files(folder_path):
    """
    Заменяет последовательность символов "]/h" на "] / h" во всех файлах в указанной папке.

    Args:
        folder_path: Путь к папке, в которой нужно обработать файлы.
    """
    if not os.path.isdir(folder_path):
        print(f"Ошибка: Указанный путь '{folder_path}' не является папкой.")
        return

    for filename in os.listdir(folder_path):
        filepath = os.path.join(folder_path, filename)
        if os.path.isfile(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as file:
                    content = file.read()

                modified_content = content.replace("]/h", "] / h")

                with open(filepath, 'w', encoding='utf-8') as file:
                    file.write(modified_content)

                print(f"Обработан файл: {filename}")
            except Exception as e:
                print(f"Ошибка при обработке файла {filename}: {e}")

if __name__ == "__main__":
    folder_to_process = input("Введите путь к папке, в которой нужно заменить текст: ")
    replace_sequence_in_files(folder_to_process)
    print("Обработка файлов завершена.")
