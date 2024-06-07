import csv
import os

from django.core.management.base import BaseCommand

from recipes.models import Ingredient

DATA = {
    Ingredient: 'ingredients.csv'
}


def read_csv(name_file):
    """Метод чтения данных из CSV и возвращения списка строк."""
    path = os.path.join('static/data', name_file)
    with open(path, encoding='utf-8') as csv_file:
        reader = csv.reader(csv_file)
        return list(reader)


def load_data(model, name_file):
    """Метод загрузки данных в указанную модель из CSV файла."""
    table = read_csv(name_file)
    for row in table:
        if row:
            name, measurement_unit = row
            model.objects.create(name=name, measurement_unit=measurement_unit)


def del_data():
    """Метод удаления всех записей из указанных таблиц."""
    for model in DATA:
        model.objects.all().delete()


class Command(BaseCommand):
    help = 'Команда для импорта данных из CSV файлов в базу данных'

    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            help='Импортировать все данные из CSV файлов в базу данных'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Удалить все данные из базы данных'
        )

    def handle(self, *args, **options):
        try:
            if options['all']:
                for model, name_file in DATA.items():
                    load_data(model, name_file)
                self.stdout.write(self.style.SUCCESS(
                    'Данные загружены в базу данных.'
                ))
            elif options['clear']:
                del_data()
                self.stdout.write(self.style.SUCCESS(
                    'База данных успешно очищена.'
                ))
            else:
                self.stdout.write(
                    self.style.SQL_KEYWORD(
                        'Используйте команду с ключом, '
                        'список доступных ключей: --help'
                    )
                )
        except Exception as e:
            self.stdout.write(self.style.ERROR(
                'Ошибка загрузки данных: "%s"' % e
            ))
