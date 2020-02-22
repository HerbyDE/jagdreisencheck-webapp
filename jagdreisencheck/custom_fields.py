import ast

from django.db import models
from django.forms.widgets import TextInput, Select
from django.utils.translation import ugettext_lazy as _
from django.utils.html import mark_safe
from djmoney.forms.widgets import MoneyWidget
from djmoney.settings import CURRENCY_CHOICES

unicode = str


class ListField(models.TextField):
    description = _('Stores a python list')
    verbose_name = _('List Field')

    def __init__(self, *args, **kwargs):
        super(ListField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if not value:
            value = []

        if isinstance(value, list):
            return value

        if isinstance([value], str):
            res = eval(value)
            return res

        return ast.literal_eval(value)

    def from_db_value(self, value, expression, connection):
        res = self.to_python(value)
        return res

    def get_prep_value(self, value):
        if value is None:
            return value

        return unicode(value)

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return 0x01 if value else 0x00


class JRCMoneyWidget(MoneyWidget):

    def __init__(self, choices=CURRENCY_CHOICES, amount_widget=TextInput, currency_widget=None, default_currency=None,
                 *args, **kwargs):
        self.default_currency = default_currency
        if not currency_widget:
            currency_widget = Select(choices=choices)
        widgets = (amount_widget, currency_widget)
        super(MoneyWidget, self).__init__(widgets, *args, **kwargs)

    def get_context(self, name, value, attrs):
        context = super(JRCMoneyWidget, self).get_context(name, value, attrs)
        if self.is_localized:
            for widget in self.widgets:
                widget.is_localized = self.is_localized
        # value is a list of values, each corresponding to a widget
        # in self.widgets.
        if not isinstance(value, list):
            value = self.decompress(value)

        final_attrs = context['widget']['attrs']
        input_type = final_attrs.pop('type', None)
        id_ = final_attrs.get('id')
        subwidgets = []
        for i, widget in enumerate(self.widgets):
            if input_type is not None:
                widget.input_type = input_type
            widget_name = '%s_%s' % (name, i)
            try:
                widget_value = value[i]
            except IndexError:
                widget_value = None
            if id_:
                widget_attrs = final_attrs.copy()
                widget_attrs['id'] = '%s_%s' % (id_, i)
            else:
                widget_attrs = final_attrs
            subwidgets.append(widget.get_context(widget_name, widget_value, widget_attrs)['widget'])
        context['widget']['subwidgets'] = subwidgets
        return context

    def render(self, name, value, attrs=None, renderer=None):
        """
        Returns this Widget rendered as HTML, as a Unicode string.
        """
        context = self.get_context(name, value, attrs)
        return self._render(template_name='base/components/form-multiwidget/multiwidget.html', context=context, renderer=renderer)
