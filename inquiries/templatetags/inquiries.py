from ast import literal_eval

from django import template

from jagdreisencheck.lists import *
from inquiries.forms import ChangeInquiryStatusForm

register = template.Library()


@register.inclusion_tag(filename='inquiries/company/change-inquiry-state.html', takes_context=True)
def change_inquiry_state_of_trip(context, trip):

    form = ChangeInquiryStatusForm(instance=trip)

    context['form'] = form
    context['trip'] = trip

    return context


@register.simple_tag()
def get_db_list(val, selector):
    
    if len(val) == 0:
        return val
    
    if type(val) == str:
        lit = literal_eval(val)
    else:
        lit = val
        
    res = []
    
    for kl in lit:
        for ks, vs in eval(selector):
            if kl == ks:
                res.append({'pk': kl, 'name': vs})
    
    return res
