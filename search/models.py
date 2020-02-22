from cms.models.pluginmodel import CMSPlugin
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import ugettext_lazy as _

from search.helpers import get_templates


# Create your models here.
class SearchConfig(CMSPlugin):
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    available_to_anonymous = models.BooleanField(default=True,
                                                 verbose_name=_('May unauthenticated users use this search instance?'))
    collect_metrics = models.BooleanField(default=False, verbose_name=_('Collect Metrics'))
    show_help = models.BooleanField(default=False, verbose_name=_('Show Help Texts'))

    def __str__(self):
        return self.name
