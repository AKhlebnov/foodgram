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
