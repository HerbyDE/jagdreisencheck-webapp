from django.shortcuts import render, get_object_or_404, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.core.files.storage import FileSystemStorage
from django.forms import modelformset_factory
from django.apps import apps

from slideshow.models import SlideShow, Image
from slideshow.forms import CreateSlideShowForm, CreateImageInstanceForm, BaseImgInstanceFormSet

from accounts.models import CorporateProfile, CompanyName

# Create your views here.


@login_required
def handle_slideshow(request):

    m_str = request.GET.get('model').split('.')
    model = apps.get_model(app_label=m_str[0], model_name=m_str[1])
    template = "slideshow/handle-slideshow.html"

    try:
        profile = CorporateProfile.objects.get(admin=request.user)
        company = CompanyName.objects.get(pk=profile.company_name.pk)
    except CorporateProfile.DoesNotExist:
        return HttpResponseRedirect("/")

    try:
        instance = model.objects.get(pk=request.GET.get('identifier'))

        if instance.company != company:
            return HttpResponseRedirect(request.GET.get('next'))

    except model.DoesNotExist:
        return HttpResponseRedirect(request.GET.get('next'))

    context = {
        'model': request.GET.get('model'),
        'identifier': request.GET.get('identifier'),
        'object': instance
    }

    try:
        slideshow = SlideShow.objects.get(target_model=request.GET.get('model'), identifier=request.GET.get('identifier'))
        images = Image.objects.filter(slideshow=slideshow)
        ImageFormFactory = modelformset_factory(Image, CreateImageInstanceForm, formset=BaseImgInstanceFormSet,
                                                extra=10 - len(images))
        imageformset = ImageFormFactory(queryset=Image.objects.filter(slideshow=slideshow))
        showform = CreateSlideShowForm(instance=slideshow)

        context['showform'] = showform
        context['imageform'] = imageformset

    except SlideShow.DoesNotExist:
        ImageFormFactory = modelformset_factory(Image, CreateImageInstanceForm, formset=BaseImgInstanceFormSet, extra=10)
        imageformset = ImageFormFactory(queryset=Image.objects.none())
        showform = CreateSlideShowForm()

        context['showform'] = showform
        context['imageform'] = imageformset

    if request.method == "POST":

        try:
            slideshow = SlideShow.objects.get(target_model=request.GET.get('model'),
                                              identifier=request.GET.get('identifier'))
            imageformset = ImageFormFactory(data=request.POST, files=request.FILES,
                                            queryset=Image.objects.filter(slideshow=slideshow))
            showform = CreateSlideShowForm(data=request.POST, instance=slideshow)

            context['showform'] = showform
            context['imageform'] = imageformset

        except SlideShow.DoesNotExist:
            imageformset = ImageFormFactory(data=request.POST, files=request.FILES, queryset=Image.objects.none())
            showform = CreateSlideShowForm(data=request.POST)

            context['showform'] = showform
            context['imageform'] = imageformset

        if showform.is_valid() and imageformset.is_valid():
            show = showform.save(commit=False)
            show.target_model = request.POST.get('target_model')
            show.identifier = request.POST.get('identifier')
            show.owner = request.user

            try:
                show.save()
                images = []
                qs = Image.objects.filter(slideshow=show)

                qs.delete()

                for image in imageformset.cleaned_data:

                    if image and image['image'] and not image['clear_image']:
                        img = Image(image=image['image'], caption=image['caption'], slideshow=show)
                        img.save()
                        images.append(img)

                if len(images) == 0 and len(qs) == 0:
                    showform.errors['image'] = _('Please add at least one image.')
                    show.delete()

                context['showform'] = CreateSlideShowForm(instance=show)
                context['imageform'] = ImageFormFactory(queryset=Image.objects.filter(slideshow=show))

                return HttpResponseRedirect(request.GET.get('next', instance.get_absolute_url))

            except IntegrityError:
                showform.errors['duplicate'] = _('A slideshow for this instance already exists.')

    return render(request=request, context=context, template_name=template)