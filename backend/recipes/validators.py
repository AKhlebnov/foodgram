import re

from django.core.exceptions import ValidationError


def validate_custom_string(value):
    """
    Валидация строки на наличие только букв, цифр, дефисов и подчеркиваний.
    """

    if not re.match(r'^[-a-zA-Z0-9_]+$', value):
        raise ValidationError(
            'Значение может содержать только '
            'буквы, цифры, дефисы и подчеркивания.'
        )


def validate_cooking_time(value):
    """
    Валидация числа, должно быть больше 0.
    """
    if value <= 0:
        raise ValidationError('Время приготовления должно быть больше 0')


def validate_amount(value):
    """
    Валидация ингредиентов, должно быть больше 0.
    """
    if value <= 0:
        raise ValidationError('Количество ингредиента должно быть больше 0')
