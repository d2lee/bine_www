# -*- coding: UTF-8 -*-

from datetime import timedelta, date
from datetime import datetime
import os
from time import gmtime, strftime


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
    year, week, dow = today.isocalendar()

    start_date = today - timedelta(dow - 1)  # assume that the first day of week is Monday
    end_date = start_date + timedelta(6)
    return start_date, end_date


def get_file_name(instance, filename):
    time = gmtime()
    path = strftime("note/%Y/%m/%d/", time)
    new_file_name = strftime("%Y%m%d-%X", time) + "-" + instance.user.username + os.path.splitext(filename)[1]
    return os.path.join(path, new_file_name)