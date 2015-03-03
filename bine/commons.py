# -*- coding: UTF-8 -*-

from datetime import date


def calculate_age(born):
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))


def get_category(birthday):
    age = calculate_age(birthday)

    if 0 <= age <= 7:
        category = "유아(0~7세)"
    elif 8 <= age <= 13:
        category = "어린이(초등)"

    return category