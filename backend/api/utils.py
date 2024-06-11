import os
from collections import defaultdict

from django.utils import baseconv
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from foodgram.settings import PDF_DIR
from foodgram.constants import (
    FONT, FONT_PATH, FONT_BOLD, FONT_BOLD_PATH,
    BODY_FONT_SIZE, HEADER_FONT_SIZE, HEADER,
    START_Y, MARGIN_X, BODY_LINE_SPACING, HEADER_LINE_SPACING
)


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

    file_name = f'Корзина_пользователя_{user.username}.pdf'
    file_path = os.path.join(PDF_DIR, file_name)

    pdf_canvas = canvas.Canvas(file_path, pagesize=letter)
    pdfmetrics.registerFont(TTFont(FONT, FONT_PATH))
    pdfmetrics.registerFont(TTFont(FONT_BOLD, FONT_BOLD_PATH))

    pdf_canvas.setFont(FONT_BOLD, HEADER_FONT_SIZE)
    y = START_Y
    pdf_canvas.drawString(
        MARGIN_X, y, HEADER
    )
    y -= HEADER_LINE_SPACING

    pdf_canvas.setFont(FONT, BODY_FONT_SIZE)
    serial_number = 0
    for ingredient, amount in ingredients_dict.items():
        serial_number += 1
        pdf_canvas.drawString(
            MARGIN_X, y,
            f'{serial_number}. {ingredient.name}: '
            f'{amount} {ingredient.measurement_unit}'
        )
        y -= BODY_LINE_SPACING

    pdf_canvas.save()
    return file_name


def generate_short_link(recipe_id):
    """
    Метод генерирует короткую ссылку на рецепт.
    """

    short_string = baseconv.base62.encode(recipe_id)
    return short_string
