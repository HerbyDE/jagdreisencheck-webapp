import os

from django.apps import apps
from django.conf import settings
from django.contrib.contenttypes.models import ContentType


def get_app_list():
    cfg_list = list()
    for cfg in apps.get_app_configs():
        cfg_list.append((cfg.name, cfg.name))

    return cfg_list


def get_model_list():
    model_list = list()
    for m in ContentType.objects.filter(app_label='travelling'):
        model_list.append(m.name)

    for m in ContentType.objects.filter(app_label='accounts'):
        model_list.append(m.name)

    return model_list


def get_templates():
    try:
        path = settings.SEARCH_TEMPLATE_PATH
    except AttributeError or ValueError or NotImplementedError:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates/', 'search/')

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
