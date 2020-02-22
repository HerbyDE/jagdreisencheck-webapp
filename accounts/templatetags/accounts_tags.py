from django import template

from accounts.models import CompanyName

register = template.Library()


@register.filter(name="get_company_name", is_safe=True)
def get_company_name(val):
    try:
        return CompanyName.objects.get(pk=val).name
    except CompanyName.DoesNotExist:
        pass


@register.filter(name='css_class', is_safe=True)
def add_css(field, css):
    try:
        return field.as_widget(attrs={"class": css})
    except AttributeError:
        pass


@register.filter(name='get_pct', is_safe=True)
def percentage(value):
    try:
        return format(value, "%")
    except (ValueError, ZeroDivisionError):
        return "0%"


@register.filter(name='add_attrs', is_safe=True)
def add_attributes(field, attr):
    attrs = attr.split(sep=",")
    attr_dict = dict()

    for e in attrs:
        chunks = e.split(sep=":")
        attr_dict[chunks[0]] = chunks[1]

    return field.as_widget(attrs=attr_dict)
