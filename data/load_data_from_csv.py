import os
import csv

from backend.recipes.models import Ingredient  # Импортируйте модель Ingredient из вашего приложения


def load_data_from_csv(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            name = row['name']
            measurement_unit = row['measurement_unit']
            # Создаем объект Ingredient и сохраняем его в базу данных
            Ingredient.objects.create(
                name=name,
                measurement_unit=measurement_unit)


if __name__ == '__main__':
    # Путь к файлу CSV с данными
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_file_path = os.path.join(BASE_DIR, 'data', 'ingredients.csv')  # Укажите правильный путь к файлу CSV
    load_data_from_csv(csv_file_path)
