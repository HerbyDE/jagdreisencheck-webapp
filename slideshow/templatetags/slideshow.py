from django.template import Context, Library, Template

from slideshow.models import SlideShow, Image


register = Library()


@register.inclusion_tag('slideshow/add-slideshow.html', takes_context=True)
def add_slideshow_btn(context, model, identifier):
    context['model_str'] = model
    context['identifier'] = identifier

    return context


@register.inclusion_tag('slideshow/show-slideshow.html', takes_context=True)
def show_slideshow(context, model, identifier):
    try:
        context['slideshow'] = SlideShow.objects.get(target_model=model, identifier=identifier)
        context['images'] = Image.objects.filter(slideshow=context['slideshow'])
    except SlideShow.DoesNotExist:
        pass

    return context

