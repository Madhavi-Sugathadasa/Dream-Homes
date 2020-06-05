from django import template
from django.conf import settings

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def add_attr(field, css):
    attrs = {}
    definition = css.split(',')

    for d in definition:
        if ':' not in d:
            attrs['class'] = d
        else:
            key, val = d.split(':')
            attrs[key] = val

    return field.as_widget(attrs=attrs)

@register.filter
def currency_symbol(amount):
    return getattr(settings, "CURRENCY_SYMBOL", None) + "{:.2f}".format(amount)

@register.filter()
def to_int(value):
    return int(value)

@register.filter
def num_format(num):
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    # add more suffixes if you need them
    return '%.1f%s' % (num, ['', 'K', 'M'][magnitude])



    