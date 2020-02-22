from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from jagdreisencheck.custom_fields import ListField


# Create your models here.
class FaqInstance(models.Model):
    name = models.CharField(verbose_name=_('Question Title'), max_length=150, null=True, blank=False)
    user = models.ForeignKey(verbose_name=_('Author'), to=settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                             null=True)
    tags = ListField(verbose_name=_('Tags'), blank=True, null=True)
    date_created = models.DateTimeField(verbose_name=_('Date Posted'), auto_now_add=True)
    date_modified = models.DateTimeField(verbose_name=_('Date Posted'), blank=True, null=True)

    # Model Config
    model = models.CharField(verbose_name=_('Associated Model'), blank=False, null=False, max_length=50)
    identifier = models.CharField(verbose_name=_('Instance ID'), blank=False, null=False, max_length=50)

    # Verification & Highlighting
    highlighted = models.BooleanField(verbose_name=_('Highlighted'), default=False)
    verified = models.BooleanField(verbose_name=_('Verified by the owner'), default=False)


class FaqAnswer(models.Model):
    text = models.TextField(verbose_name=_('Answer'), max_length=1000)
    user = models.ForeignKey(verbose_name=_('Author'), to=settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                             null=True)
    date_created = models.DateTimeField(verbose_name=_('Date Posted'), auto_now_add=True)
    date_modified = models.DateTimeField(verbose_name=_('Date Posted'), blank=True, null=True)
    question = models.ForeignKey(verbose_name=_('Question'), to=FaqInstance, on_delete=models.CASCADE, null=True)
