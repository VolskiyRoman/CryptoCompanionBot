import re


def is_valid_phone_number(phone_number):
    pattern = re.compile(r'^\+?\d{9,15}$')
    return bool(re.match(pattern, phone_number.strip()))
