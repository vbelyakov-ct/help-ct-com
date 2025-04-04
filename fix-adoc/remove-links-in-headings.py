import os
import re

def process_file(filepath):
    """
    Обрабатывает файл: ищет строки с двумя или более знаками "=" и словом "link",
    удаляет "link" и все символы после него в таких строках.

    Args:
        filepath (str): Путь к файлу.
    """
    try:
        with open(filepath, 'r+', encoding='utf-8') as f:
            lines = f.readlines()
            updated_lines = []
            file_changed = False
            for line in lines:
                if re.search(r'={2,}.*link', line, re.IGNORECASE):
                    # Найдена строка, соответствующая критериям
                    updated_line = re.sub(r'(={2,}.*?)link.*', r'\1', line, flags=re.IGNORECASE)
                    updated_lines.append(updated_line)
                    file_changed = True
                else:
                    updated_lines.append(line)

            if file_changed:
                f.seek(0)
                f.writelines(updated_lines)
                f.truncate()
                print(f"Файл '{filepath}' был изменен.")
            else:
                print(f"Файл '{filepath}' не был изменен.")

    except FileNotFoundError:
        print(f"Ошибка: Файл '{filepath}' не найден.")
    except Exception as e:
        print(f"Ошибка при обработке файла '{filepath}': {e}")

def process_folder(folder_path):
    """
    Обрабатывает все файлы в указанной папке.

    Args:
        folder_path (str): Путь к папке.
    """
    if not os.path.isdir(folder_path):
        print(f"Ошибка: Указанный путь '{folder_path}' не является папкой.")
        return

    for filename in os.listdir(folder_path):
        filepath = os.path.join(folder_path, filename)
        if os.path.isfile(filepath):
            process_file(filepath)

if __name__ == "__main__":
    folder_to_process = input("Введите путь к папке, которую нужно обработать: ")
    process_folder(folder_to_process)
    print("Обработка завершена.")
