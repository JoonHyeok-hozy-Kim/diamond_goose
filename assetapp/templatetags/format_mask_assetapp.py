from django import template
from django.contrib.humanize.templatetags.humanize import intcomma
from django.utils.text import Truncator

register = template.Library()


def currency_usd(amount):
    if isinstance(amount, str):
        return amount
    amount = round(float(amount), 2)
    return "$%s%s" % (intcomma(int(amount)), ("%0.2f" % amount)[-3:])


def currency_krw(amount):
    if isinstance(amount, str):
        return amount
    amount = round(float(amount))
    return "￦%s" % (intcomma(int(amount)))


def percentage_rate_format(amount):
    if isinstance(amount, str):
        return amount
    amount = round(float(amount*100), 2)
    result = "%s%s" % (intcomma(int(amount)), ("%0.2f" % amount)[-3:])
    result += '%'
    return result

def asset_name_omit(asset_name):
    return Truncator(asset_name).chars(31)

def int_number(amount):
    if amount is None:
        return '0'
    if isinstance(amount, str):
        return amount
    amount = round(float(amount))
    return "%s" % (intcomma(int(amount)))

def split_ratio_format(amount):
    if isinstance(amount, str):
        return amount
    if amount > 1:
        return '1 : {}'.format(int(amount))
    elif amount == 0:
        return '-'
    else:
        reverse = round(pow(amount, -1))
        return '{} : 1'.format(reverse)


register.filter('currency_usd', currency_usd)
register.filter('currency_krw', currency_krw)
register.filter('percentage_rate_format', percentage_rate_format)
register.filter('intcomma', intcomma)
register.filter('asset_name_omit', asset_name_omit)
register.filter('int_number', int_number)
register.filter('split_ratio_format', split_ratio_format)
