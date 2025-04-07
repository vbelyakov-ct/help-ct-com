import os
import re

def process_files(folder_path):
    """
    Ищет в файлах в заданной папке фразы "link:" без пробела,
    удаляет "link:" и все, что идет после, оставляя только слово перед "link:".
    Обрабатывает только строки, где перед "link:" нет пробела, переноса строки
    и "link:" не находится в начале строки.
    После этого применяет функции для добавления заголовков, объединения строк и удаления нежелательных символов.

    Args:
        folder_path: Путь к папке, в которой нужно обработать файлы.
    """
    for filename in os.listdir(folder_path):
        filepath = os.path.join(folder_path, filename)
        if os.path.isfile(filepath):
            process_file(filepath)
            add_headers(filepath)
            merge_short_lines(filepath)
            remove_unwanted_lines(filepath)

def process_file(filepath):
    """
    Обрабатывает один файл: ищет и заменяет нужные фразы с "link:".

    Args:
        filepath: Путь к файлу.
    """
    try:
        with open(filepath, 'r+', encoding='utf-8') as f:
            lines = f.readlines()
            f.seek(0)
            f.truncate()
            for line in lines:
                modified_line = re.sub(r'(?<![\s])(\w+)link:.*', r'\1', line)
                f.write(modified_line)
    except Exception as e:
        print(f"Ошибка при обработке файла {filepath}: {e}")





def remove_unwanted_lines(filepath):
    """
    Удаляет строки, содержащие три и более подряд символов ~ или ^.

    Args:
        filepath: Путь к файлу.
    """
    try:
        with open(filepath, 'r+', encoding='utf-8') as f:
            lines = f.readlines()
            f.seek(0)
            f.truncate()
            for line in lines:
                if not re.search(r'~{3,}|\^{3,}', line):
                    f.write(line)
    except Exception as e:
        print(f"Ошибка при удалении нежелательных строк в файле {filepath}: {e}")

if __name__ == "__main__":
    folder_to_process = input("Введите путь к папке, в которой нужно обработать файлы: ")
    if os.path.isdir(folder_to_process):
        process_files(folder_to_process)
        print("Обработка файлов завершена.")
    else:
        print("Указанный путь не является папкой.")
