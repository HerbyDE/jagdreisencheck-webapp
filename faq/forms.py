from django.forms import forms, models, widgets

from faq.models import FaqInstance, FaqAnswer


class FaqInstanceForm(models.ModelForm):

    class Meta:
        model = FaqInstance
        fields = ['name', 'highlighted']


class FaqAnswerForm(models.ModelForm):

    class Meta:
        model = FaqAnswer
        fields = ['text']
        widgets = {
            'text': widgets.Textarea(attrs={'rows': 3})
        }