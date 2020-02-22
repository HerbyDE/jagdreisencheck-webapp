from ckeditor.fields import RichTextField
from cms.models.pluginmodel import CMSPlugin
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import ugettext_lazy as _
from filer.fields.image import FilerImageField
from sorl.thumbnail import get_thumbnail

from cms_plugin_directory.helpers import get_templates, BTN_TYPE_LIST


# Create your models here.
class ContainerConfig(CMSPlugin):
    container_type = models.CharField(verbose_name=_('Container Type'), null=True, blank=False,
                                      choices=[
                                          ('container', _('Regular Container')),
                                          ('container-fluid', _('Fluid Container'))
                                      ], max_length=35)
    margin_top = models.CharField(verbose_name=_('Top Margin'), max_length=7, null=True, blank=True)
    margin_bottom = models.CharField(verbose_name=_('Bottom Margin'), max_length=7, null=True, blank=True)


class RowConfig(CMSPlugin):
    margin_top = models.CharField(verbose_name=_('Top Margin'), max_length=7, null=True, blank=True)
    margin_bottom = models.CharField(verbose_name=_('Bottom Margin'), max_length=7, null=True, blank=True)


class ColumnConfig(CMSPlugin):
    width = models.CharField(verbose_name=_('Width'), max_length=7, null=True, blank=False, choices=[
        ('1', '1/12'),
        ('2', '2/12'),
        ('3', '3/12'),
        ('4', '4/12'),
        ('5', '5/12'),
        ('6', '6/12'),
        ('7', '7/12'),
        ('8', '8/12'),
        ('9', '9/12'),
        ('10', '10/12'),
        ('11', '11/12'),
        ('12', '12/12'),
    ])


class CardConfig(CMSPlugin):
    headline = models.CharField(verbose_name=_('Headline'), max_length=50, null=True)
    body = RichTextField(verbose_name=_('Card Body'), blank=True, null=True)
    link = models.CharField(verbose_name=_('Forward URL'), null=True, blank=False, max_length=150)
    btn_type = models.CharField(verbose_name=_('Template'), choices=BTN_TYPE_LIST, max_length=25, default='success')
    btn_block = models.BooleanField(verbose_name=_('Display Button as Block'), default=False)
    link_text = models.CharField(verbose_name=_('Link Text'), max_length=35, null=True)
    template = models.CharField(verbose_name=_('Template'), choices=get_templates('cards/'), max_length=150)
    image = FilerImageField(verbose_name=_('Top Image'), null=True, blank=True, related_name="card_image",
                            on_delete=models.SET_NULL)

    def get_thumb(self):
        im = get_thumbnail(self.image, '350x198', crop='center', quality=70)
        return im.url

    def __str__(self):
        return u"%s: %s" % (self.id, self.headline)
    
    
class BlogThumbnailListConfig(CMSPlugin):
    num_objects = models.IntegerField(verbose_name=_('Number of entries'), max_length=1, default=3)
