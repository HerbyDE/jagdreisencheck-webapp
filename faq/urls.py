# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from django.conf.urls import url
from faq.views import post_question, post_answer, delete_answer, delete_question, edit_answer, edit_question

app_name = 'faq'
urlpatterns = [
    url(r'post/question/$', post_question, name='post_question'),
    url(r'post/answer/$', post_answer, name='post_answer'),
    url(r'edit/question/(?P<instance>.)+/$', edit_question, name='edit_question'),
    url(r'edit/answer/(?P<instance>.)+/$', edit_answer, name='edit_answer'),
    url(r'delete/question/(?P<instance>.)+/$', delete_question, name='delete_question'),
    url(r'delete/answer/(?P<instance>.)+/$', delete_answer, name='delete_answer'),
]
