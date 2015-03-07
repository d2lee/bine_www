# -*- coding: UTF-8 -*-

from datetime import date, timedelta
from datetime import datetime


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


def get_this_week_range():
    today = datetime.today()
    year, week, dow = date.isocalendar()

    start_date = today - timedelta(dow - 1)  # assume that the first day of week is Monday
    end_date = start_date + timedelta(6)
    return start_date, end_date