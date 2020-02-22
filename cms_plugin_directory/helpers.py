import os

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

BTN_TYPE_LIST = (
    ('success', _('Green Button')),
    ('danger', _('Red Button')),
    ('darkblue', _('Dark Blue Button')),
    ('light', _('Lightgray Button')),
    ('info', _('Lightblue Button')),
)


def get_templates(plugin_template_path):
    try:
        path = settings.SEARCH_TEMPLATE_PATH
    except AttributeError or ValueError or NotImplementedError:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates/', 'cms_plugin_templates/',
                            plugin_template_path)

    files = list()
    for file in os.listdir(path=path):
        n = file.split(sep='_')
        name = ''
        for e in n:
            if name == '':
                name = e.capitalize()
            else:
                name = name + ' ' + str(e.capitalize())

        data = path + file

        files.append((data, name))

    return files
