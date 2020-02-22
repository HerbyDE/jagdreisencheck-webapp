from functools import wraps

from django.conf import settings
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _

from django.shortcuts import HttpResponseRedirect, reverse
import requests


def check_recaptcha(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        request.recaptcha_is_valid = None
        if request.method == 'POST':

            recaptcha_response = request.POST.get('g-recaptcha-response')

            data = {
                'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
                'response': recaptcha_response
            }
            r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
            result = r.json()
            if result['success']:
                request.recaptcha_is_valid = True
            else:
                request.recaptcha_is_valid = False
                messages.error(request, _('Invalid Recaptcha. Please try again.'))
        return view_func(request, *args, **kwargs)

    return _wrapped_view


def login_required_with_params(view_func):
    def decorator(request, *args, **kwargs):
        if request.user.is_authenticated:
            return view_func(request, *args, **kwargs)
        else:
            
            url = reverse('accounts:user_login')
            next = request.path
            params = request.GET.copy()
            url_params = '?'
            
            if not request.GET.get('ref') and request.path == reverse('travelling:create_trip'):
                params['ref'] = 'create_trip'
            
            if len(params) > 0:
        
                idx = 0
                for k, v in params.items():
                    
                    if idx == 0:
                        url_params = '{}{}{}{}'.format(url_params, k, "=", v)
                    else:
                        url_params = '{}{}{}{}{}'.format(url_params, "&", k, "=", v)
                
                    idx += 1

                url_params = '{}{}{}'.format(url_params, "&next=", next)
                
            else:
                url_params = '?next={}'.format(next)
                
            url = '{}{}'.format(url, url_params)
            
            return HttpResponseRedirect(url)
    
    return decorator
