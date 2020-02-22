from django.shortcuts import render, HttpResponseRedirect, get_object_or_404
from django.core.mail import EmailMultiAlternatives
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.contrib import messages

from faq.forms import FaqInstanceForm, FaqAnswerForm
from faq.models import FaqInstance, FaqAnswer



# Create your views here.
def overview(request, parent = None):
    pass


def post_question(request):

    if request.method == "POST":
        form = FaqInstanceForm(request.POST)
        if form.is_valid():
            form = form.save(commit=False)
            form.user = request.user
            form.date_created = timezone.now()
            form.model = request.POST.get('model')
            form.identifier = request.POST.get('identifier')

            form.save()

            messages.success(request=request, message=_('Question added successfully.'))
            return HttpResponseRedirect(request.POST.get('redirect', '/'))
        else:

            messages.error(request=request, message=_('There was an error creating the question!'))
            return HttpResponseRedirect(request.POST.get('redirect', '/'))


def post_answer(request):
    if request.method == "POST":
        form = FaqAnswerForm(request.POST)
        if form.is_valid():
            form = form.save(commit=False)
            form.user = request.user
            form.date_created = timezone.now()
            form.model = request.POST.get('model')
            form.identifier = request.POST.get('identifier')
            form.question = get_object_or_404(FaqInstance, pk=request.POST.get('identifier'))

            form.save()
            
            messages.success(request=request, message=_('Answer added successfully.'))
            return HttpResponseRedirect(request.POST.get('redirect', '/'))
        else:

            messages.error(request=request, message=_('There was an error creating the answer!'))
            return HttpResponseRedirect(request.POST.get('redirect', '/'))


def edit_question(request, instance):
    if request.method == 'POST':
        form = FaqInstanceForm(request.POST, instance=FaqInstance.objects.get(pk=instance))
        if form.is_valid():
            form.save()

            messages.success(request=request, message=_('Question updated successfully.'))
            return HttpResponseRedirect(request.POST.get('redirect', '/'))
        else:

            messages.error(request=request, message=_('There was an error updating the question!'))
            return HttpResponseRedirect(request.POST.get('redirect', '/'))


def edit_answer(request, instance):
    if request.method == 'POST':
        form = FaqAnswerForm(request.POST, instance=FaqAnswer.objects.get(pk=instance))
        if form.is_valid():
            form.save()

            messages.success(request=request, message=_('Answer updated successfully.'))
            return HttpResponseRedirect(request.POST.get('redirect', '/'))
        else:

            messages.error(request=request, message=_('There was an error updating the answer!'))
            return HttpResponseRedirect(request.POST.get('redirect', '/'))

    return HttpResponseRedirect(request.POST.get('redirect', '/'))


def delete_question(request, instance):
    if request.method == 'POST':
        FaqInstance.objects.get(pk=instance).delete()
        messages.success(request=request, message=_('Question deleted.'))
        return HttpResponseRedirect(request.POST.get('redirect', '/'))


def delete_answer(request, instance):
    if request.method == 'POST':
        FaqAnswer.objects.get(pk=instance).delete()
        messages.success(request=request, message=_('Answer deleted.'))
        return HttpResponseRedirect(request.POST.get('redirect', '/'))
