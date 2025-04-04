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

def add_headers(filepath):
    """
    Ищет строки вида "[[hN_...]]" и добавляет соответствующее количество "="
    в начало следующей непустой строки.

    Args:
        filepath: Путь к файлу.
    """
    try:
        with open(filepath, 'r+', encoding='utf-8') as f:
            lines = f.readlines()
            f.seek(0)
            f.truncate()
            i = 0
            while i < len(lines):
                line = lines[i]
                match = re.match(r'\[\[h(\d+)_.+\]\]', line)
                if match:
                    header_level = int(match.group(1))
                    if i + 1 < len(lines) and lines[i + 1].strip():  # Проверяем следующую строку на существование и непустоту
                        lines[i + 1] = "=" * header_level + " " + lines[i + 1].lstrip()
                f.write(line)
                i += 1
    except Exception as e:
        print(f"Ошибка при обработке заголовков в файле {filepath}: {e}")

def merge_short_lines(filepath):
    """
    Ищет строки, начинающиеся с "==" - "=====", за которыми следует пробел
    и затем строка с одним словом на следующей строке, и переносит это слово.

    Args:
        filepath: Путь к файлу.
    """
    try:
        with open(filepath, 'r+', encoding='utf-8') as f:
            lines = f.readlines()
            f.seek(0)
            f.truncate()
            new_lines = []
            i = 0
            while i < len(lines):
                line = lines[i].rstrip()  # Удаляем лишние пробелы в конце текущей строки
                match = re.match(r'^={2,5} .+', line)

                if match and i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    next_line_words = next_line.split()
                    if len(next_line_words) == 1:
                        new_lines.append(line + " " + next_line + "\n")
                        i += 2  # Пропускаем обе строки, так как они объединены
                        continue
                new_lines.append(lines[i])
                i += 1

            f.writelines(new_lines)

    except Exception as e:
        print(f"Ошибка при объединении строк в файле {filepath}: {e}")

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
