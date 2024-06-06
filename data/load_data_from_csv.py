import csv
import os
import sys

import django

from backend.recipes.models import Ingredient

# Получаем корневую директорию проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Добавляем корневую директорию в sys.path
sys.path.append(BASE_DIR)

# Устанавливаем настройки Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodgram.settings')
django.setup()


def load_data_from_csv(file_path):
    """
    Функция для загрузки данных из CSV-файла в базу данных.
    """

    with open(file_path, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            name = row[0]
            measurement_unit = row[1]

            Ingredient.objects.create(
                name=name,
                measurement_unit=measurement_unit
            )


if __name__ == '__main__':
    csv_file_path = os.path.join(BASE_DIR, 'data', 'ingredients.csv')
    load_data_from_csv(csv_file_path)
