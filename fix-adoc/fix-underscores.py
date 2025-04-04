import os

def add_backslash_before_underscore_c(folder_path):
    """
    Проходит по всем файлам в указанной папке и добавляет обратный слеш
    перед сочетанием символов "__c".

    Args:
        folder_path (str): Путь к папке, в которой нужно обработать файлы.
    """
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            try:
                with open(file_path, 'r') as f:
                    content = f.read()

                new_content = content.replace("__c", r"\__c")

                if new_content != content:
                    with open(file_path, 'w') as f:
                        f.write(new_content)
                    print(f"В файле '{filename}' добавлено обратный слеш перед '__c'.")
                else:
                    print(f"В файле '{filename}' сочетание '__c' не найдено.")

            except Exception as e:
                print(f"Ошибка при обработке файла '{filename}': {e}")

if __name__ == "__main__":
    folder_to_process = input("Введите путь к папке, которую нужно обработать: ")
    if os.path.isdir(folder_to_process):
        add_backslash_before_underscore_c(folder_to_process)
        print("Обработка завершена.")
    else:
        print("Указанный путь не является папкой.")