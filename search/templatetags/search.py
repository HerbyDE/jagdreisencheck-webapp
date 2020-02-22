from django import template

from search.models import SearchConfig

register = template.Library()


@register.simple_tag
def get_search_instance_name(instance):
    return SearchConfig.objects.get(pk=instance).name
