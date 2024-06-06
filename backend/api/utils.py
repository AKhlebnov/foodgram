import os
import pprint
from collections import defaultdict

from django.utils import baseconv
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from foodgram.settings import PDF_DIR


def generate_shopping_cart_pdf(recipes, user):
    """
    Метод генерирует PDF-файл с списком ингредиентов для корзины покупок.
    """

    ingredients_dict = defaultdict(float)

    for recipe in recipes:
        recipe_ingredients = recipe.recipe_ingredients.all()
        for recipe_ingredient in recipe_ingredients:
            ingredient = recipe_ingredient.ingredient
            ingredients_dict[ingredient] += recipe_ingredient.amount

    pprint.pprint(ingredients_dict)

    file_name = f'Корзина_пользователя_{user.username}.pdf'
    file_path = os.path.join(PDF_DIR, file_name)

    pdf_canvas = canvas.Canvas(file_path, pagesize=letter)
    pdfmetrics.registerFont(TTFont('DejaVu', 'fonts/DejaVuSans.ttf'))
    pdfmetrics.registerFont(TTFont('DejaVu-Bold', 'fonts/DejaVuSans-Bold.ttf'))

    pdf_canvas.setFont('DejaVu-Bold', 16)
    y = 750
    pdf_canvas.drawString(
        100, y, 'Список ингредиентов:'
    )
    y -= 30

    pdf_canvas.setFont('DejaVu', 12)
    serial_number = 0
    for ingredient, amount in ingredients_dict.items():
        serial_number += 1
        pdf_canvas.drawString(
            100, y,
            f'{serial_number}. {ingredient.name}: '
            f'{amount} {ingredient.measurement_unit}'
        )
        y -= 20

    pdf_canvas.save()
    return file_name


def generate_short_link(recipe_id):
    """
    Метод генерирует короткую ссылку на рецепт.
    """

    short_string = baseconv.base62.encode(recipe_id)
    return short_string
