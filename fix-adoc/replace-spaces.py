import os

def rename_files_with_spaces(folder_path):
  """
  Ищет файлы с пробелами в имени в заданной папке и заменяет их на дефисы.

  Args:
    folder_path: Путь к папке, в которой нужно искать файлы.
  """
  for filename in os.listdir(folder_path):
    if " " in filename:
      new_filename = filename.replace(" ", "-")
      old_path = os.path.join(folder_path, filename)
      new_path = os.path.join(folder_path, new_filename)
      os.rename(old_path, new_path)
      print(f"Переименован файл: '{filename}' -> '{new_filename}'")

if __name__ == "__main__":
  folder_path = input("Введите путь к папке: ")
  if os.path.isdir(folder_path):
    rename_files_with_spaces(folder_path)
    print("Обработка завершена.")
  else:
    print("Указанный путь не является папкой.")
