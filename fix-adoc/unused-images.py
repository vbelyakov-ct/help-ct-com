#!/usr/bin/env python3
"""
Скрипт для поиска неиспользуемых изображений в AsciiDoc файлах
и перемещения их в папку extra.
"""

import os
import re
import shutil
from pathlib import Path
import argparse


def find_image_references(pages_dir):
    """
    Ищет все ссылки на изображения в .adoc файлах
    Возвращает множество имен файлов изображений, которые используются
    """
    used_images = set()

    # Регулярные выражения для поиска ссылок на изображения в AsciiDoc
    patterns = [
        r'image::([^[\]]+)\[',  # image::path/file.png[alt text]
        r'image:([^[\]]+)\[',   # image:path/file.png[alt text] (inline)
        r'link:([^[\]]+\.(?:png|jpg|jpeg|gif|svg|webp|bmp|tiff|ico))',  # link:image.png
        r'include::([^[\]]+\.(?:png|jpg|jpeg|gif|svg|webp|bmp|tiff|ico))',  # include::image.png
    ]

    for adoc_file in Path(pages_dir).rglob('*.adoc'):
        try:
            with open(adoc_file, 'r', encoding='utf-8') as f:
                content = f.read()

            for pattern in patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    # Извлекаем только имя файла из пути
                    image_name = os.path.basename(match)
                    used_images.add(image_name)

        except Exception as e:
            print(f"Ошибка при чтении файла {adoc_file}: {e}")

    return used_images


def find_all_images(images_dir):
    """
    Находит все файлы изображений в указанной папке
    """
    image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.bmp', '.tiff', '.tif', '.ico', '.avif', '.heic'}
    all_images = set()

    for file_path in Path(images_dir).rglob('*'):
        if file_path.is_file() and file_path.suffix.lower() in image_extensions:
            all_images.add(file_path.name)

    return all_images


def move_unused_images(images_dir, unused_images, extra_dir, dry_run=False):
    """
    Перемещает неиспользуемые изображения в папку extra
    """
    if not unused_images:
        print("Неиспользуемых изображений не найдено.")
        return

    # Создаем папку extra если её нет
    if not dry_run:
        os.makedirs(extra_dir, exist_ok=True)

    moved_count = 0

    for image_name in unused_images:
        # Ищем файл в папке images (может быть в подпапках)
        for image_path in Path(images_dir).rglob(image_name):
            if image_path.is_file():
                destination = Path(extra_dir) / image_name

                # Если файл с таким именем уже есть в extra, добавляем суффикс
                counter = 1
                original_destination = destination
                while destination.exists():
                    stem = original_destination.stem
                    suffix = original_destination.suffix
                    destination = original_destination.parent / f"{stem}_{counter}{suffix}"
                    counter += 1

                if dry_run:
                    print(f"[DRY RUN] Переместил бы: {image_path} -> {destination}")
                else:
                    try:
                        shutil.move(str(image_path), str(destination))
                        print(f"Перемещено: {image_path} -> {destination}")
                        moved_count += 1
                    except Exception as e:
                        print(f"Ошибка при перемещении {image_path}: {e}")
                break

    if not dry_run:
        print(f"\nВсего перемещено файлов: {moved_count}")


def main():
    parser = argparse.ArgumentParser(
        description="Находит неиспользуемые изображения в AsciiDoc файлах и перемещает их в папку extra"
    )
    parser.add_argument("--pages", default="pages",
                        help="Папка с .adoc файлами (по умолчанию: pages)")
    parser.add_argument("--images", default="images",
                        help="Папка с изображениями (по умолчанию: images)")
    parser.add_argument("--extra", default="extra",
                        help="Папка для неиспользуемых изображений (по умолчанию: extra)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Показать что будет перемещено, но не выполнять действия")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Подробный вывод")

    args = parser.parse_args()

    # Проверяем существование папок
    if not os.path.exists(args.pages):
        print(f"Ошибка: папка {args.pages} не существует")
        return 1

    if not os.path.exists(args.images):
        print(f"Ошибка: папка {args.images} не существует")
        return 1

    print(f"Поиск ссылок на изображения в папке: {args.pages}")
    used_images = find_image_references(args.pages)

    if args.verbose:
        print(f"Найдено используемых изображений: {len(used_images)}")
        for img in sorted(used_images):
            print(f"  - {img}")

    print(f"\nПоиск всех изображений в папке: {args.images}")
    all_images = find_all_images(args.images)

    if args.verbose:
        print(f"Найдено всех изображений: {len(all_images)}")
        for img in sorted(all_images):
            print(f"  - {img}")

    # Находим неиспользуемые изображения
    unused_images = all_images - used_images

    print(f"\nНеиспользуемые изображения ({len(unused_images)}):")
    for img in sorted(unused_images):
        print(f"  - {img}")

    if unused_images:
        if args.dry_run:
            print(f"\n=== РЕЖИМ СИМУЛЯЦИИ ===")

        move_unused_images(args.images, unused_images, args.extra, args.dry_run)

        if args.dry_run:
            print(f"\nДля реального выполнения запустите без --dry-run")

    return 0


if __name__ == "__main__":
    exit(main())