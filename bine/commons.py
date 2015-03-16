# -*- coding: UTF-8 -*-
from calendar import timegm
from datetime import timedelta, date
from datetime import datetime
import os
from time import gmtime, strftime

from rest_framework_jwt.settings import api_settings
from rest_framework_jwt.utils import jwt_payload_handler, jwt_encode_handler


def auth_response_payload_handler(token, user=None):
    if user.photo:
        photo_url = user.photo.url
    else:
        photo_url = ''

    return {
        'token': token,
        'user': {'id': user.id, 'fullname': user.fullname, 'sex': user.sex, 'photo': photo_url},
    }


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