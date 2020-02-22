from django.forms import forms, models, BooleanField
from django.utils.translation import ugettext_lazy as _

from slideshow.models import SlideShow, Image


class CreateSlideShowForm(models.ModelForm):

    class Meta:
        model = SlideShow
        fields = ['name']


class CreateImageInstanceForm(models.ModelForm):
    clear_image = BooleanField(required=False, label=_('Delete File'))

    class Meta:
        model = Image
        fields = ['image', 'caption']


class BaseImgInstanceFormSet(models.BaseModelFormSet):
    pass
