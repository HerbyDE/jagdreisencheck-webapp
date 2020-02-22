from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings


# Create your models here.
class SlideShow(models.Model):
    name = models.CharField(verbose_name=_('Slideshow Title'), max_length=75, blank=False, null=True)
    target_model = models.CharField(verbose_name=_('Associated Model'), max_length=150, blank=False, null=True)
    identifier = models.CharField(verbose_name=_('Model Identifier'), max_length=30, blank=False, null=True)

    date_created = models.DateTimeField(verbose_name=_('Date Created'), auto_now_add=True)
    date_modified = models.DateTimeField(verbose_name=_('Date Modified'), blank=True, null=True)
    owner = models.ForeignKey(verbose_name=_('Owning User'), to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                              null=True)

    class Meta:
        unique_together = ('target_model', 'identifier')

    def __str__(self):
        return self.name


class Image(models.Model):
    width = models.IntegerField(verbose_name=_('Image Width'), null=True, blank=True)
    height = models.IntegerField(verbose_name=_('Image Height'), null=True, blank=True)
    image = models.ImageField(verbose_name=_('Image File'), upload_to='slideshow/%Y/%m/%d/', blank=True, null=True)
    caption = models.TextField(verbose_name=_('Image caption'), blank=True, null=True)
    slideshow = models.ForeignKey(verbose_name=_('Slideshow'), to=SlideShow, on_delete=models.CASCADE, null=True)
