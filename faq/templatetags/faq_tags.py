from django import template

from faq.forms import FaqInstanceForm, FaqAnswerForm
from faq.models import FaqInstance, FaqAnswer


register = template.Library()


@register.inclusion_tag('faq/jagdreisencheck/create-question-form.html', takes_context=True)
def create_question_form(context, model, identifier):
    form = FaqInstanceForm()

    context['form'] = form
    context['model'] = model
    context['identifier'] = identifier

    return context


@register.inclusion_tag('faq/jagdreisencheck/answer-question-form.html', takes_context=True)
def answer_question_form(context, identifier, parent):
    form = FaqAnswerForm()

    context['form'] = form
    context['identifier'] = identifier
    context['parent'] = parent

    return context


@register.inclusion_tag('faq/jagdreisencheck/render-questions.html', takes_context=True)
def render_questions(context, model, identifier):
    questions = FaqInstance.objects.filter(model=model, identifier=identifier).order_by("-date_created")

    context['questions'] = questions
    context['qe_form'] = FaqInstanceForm
    context['aw_form'] = FaqAnswerForm

    return context