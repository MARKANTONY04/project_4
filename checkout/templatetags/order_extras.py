# checkout/templatetags/order_extras.py
from django import template

register = template.Library()


@register.filter
def order_total(lineitems):
    return sum(item.line_total for item in lineitems)
