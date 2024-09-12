import json
from datetime import timedelta

from django import template

register = template.Library()


@register.filter
def mul(value, arg):
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return ""


@register.filter
def div(value, arg):
    try:
        return float(value) / float(arg)
    except (ValueError, TypeError):
        return ""


@register.filter
def vat_value(value):
    try:
        return round(float(value) - (float(value) / float(1.23)), 2)
    except (ValueError, TypeError):
        return ""


@register.filter
def date_add(value, days):
    try:
        if days is None:
            return value
        return value + timedelta(days=int(days))
    except (ValueError, TypeError):
        return value


@register.filter
def json_loads(value):
    try:
        return json.loads(value)
    except (ValueError, TypeError):
        return []


@register.filter
def multiply(value, arg):
    """Mnożnik dla wartości w szablonie"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return value
