import os
import re

def replace_nbsp_before_http(folder_path):
    """
    Заменяет неразрывный пробел перед "http" на обычный пробел во всех файлах в указанной папке.

    Args:
        folder_path: Путь к папке, в которой нужно обработать файлы.
    """
    nbsp = '\N{NO-BREAK SPACE}'  # Unicode representation of non-breaking space
    http_pattern = re.compile(rf'{nbsp}(http)', re.IGNORECASE)

    for filename in os.listdir(folder_path):
        filepath = os.path.join(folder_path, filename)
        if os.path.isfile(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()

                modified_content = http_pattern.sub(r' \1', content)

                if modified_content != content:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(modified_content)
                    print(f"В файле '{filename}' заменены неразрывные пробелы.")
                else:
                    print(f"В файле '{filename}' не найдено неразрывных пробелов перед 'http'.")

            except Exception as e:
                print(f"Ошибка при обработке файла '{filename}': {e}")

if __name__ == "__main__":
    folder_to_process = input("Введите путь к папке для обработки: ")
    if os.path.isdir(folder_to_process):
        replace_nbsp_before_http(folder_to_process)
    else:
        print("Указанный путь не является папкой.")
