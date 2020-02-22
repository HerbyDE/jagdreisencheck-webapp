import os

from django.shortcuts import render, HttpResponseRedirect
from django.conf import settings

from seotools.models import REGISTRATION_ORIGINS, RegistrationInfoGraphic


# Create your views here.
def render_registration_preamble(request):
    
    try:
        test = eval(os.environ['testsystem'])
    except KeyError:
        test = False
        
    if request.user.is_authenticated and not settings.DEBUG and not test:
        return HttpResponseRedirect("/")
    
    template = 'seotools/registration-preamble.html'
    
    ref = request.GET.get('ref', None)
    
    ctx = dict()
    
    if ref:
        for key, val in REGISTRATION_ORIGINS:
            if ref == key:
                ctx['objects'] = RegistrationInfoGraphic.objects.filter(origin=ref)
                
    else:
                
        ctx['objects'] = RegistrationInfoGraphic.objects.filter(origin='default')
    
    return render(request=request, template_name=template, context=ctx)
    

