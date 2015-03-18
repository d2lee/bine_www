# -*- coding: UTF-8 -*-
from calendar import timegm
from datetime import timedelta, date
from datetime import datetime
import os
from time import gmtime, strftime

from django.utils import timezone
from rest_framework_jwt.settings import api_settings
from rest_framework_jwt.utils import jwt_payload_handler, jwt_encode_handler


def auth_response_payload_handler(token, user, request):
    if user.photo:
        photo_url = user.photo.url
    else:
        photo_url = ''

    return {
        'token': token,
        'user': {'id': user.id, 'fullname': user.fullname, 'sex': user.sex, 'photo': photo_url,
                 'last_login_on': user.last_login_on},
    }


def calculate_age(born):
    today = date.today()
    # return today.year - born.year - ((today.month, today.day) < (born.month, born.day))
    return today.year - born.year + 1


def convert_birthday_to_age_level(birthday):
    age = calculate_age(birthday)
    age_level = 1 << (age - 1)

    return age_level


def convert_category_to_age_level(category):
    level_table = {'어린이(초등)': 8064, '유아0~7세': 127}

    # 매칭되는 것이 없으면 어른 것으로 간주
    if category:
        category = category.strip()

    age_level = level_table.get(category, 1040384)

    return age_level


def get_this_week_range():
    today = timezone.now()
    year, week, dow = today.isocalendar()

    start_date = today - timedelta(dow - 1)  # assume that the first day of week is Monday
    end_date = start_date + timedelta(6)
    return start_date, end_date


def get_file_name(instance, filename):
    time = gmtime()
    path = strftime("note/%Y/%m/%d/", time)
    new_file_name = strftime("%Y%m%d-%X", time) + "-" + instance.user.username + os.path.splitext(filename)[1]
    return os.path.join(path, new_file_name)


def date_to_iso_string(date_obj):
    return date_obj.isoformat()


# It's for testing purpose
def login_without_password(user):
    payload = jwt_payload_handler(user)  # Include original issued at time for a brand new token,
    # to allow token refresh
    if api_settings.JWT_ALLOW_REFRESH:
        payload['orig_iat'] = timegm(
            datetime.utcnow().utctimetuple()
        )

    return {
        'token': jwt_encode_handler(payload),
        'user': user
    }