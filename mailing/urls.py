from django.conf.urls import re_path

from mailing.views import unsubscribe, render_mail

app_name = 'mailing'
urlpatterns = [
    re_path(r'^unsubscribe/$', unsubscribe, name='unsubscribe'),
    re_path(r'^render/mail/$', render_mail, name='render_mail'),
]