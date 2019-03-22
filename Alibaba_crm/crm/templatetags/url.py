from django import template
from django.urls import reverse
from django.http import QueryDict

register = template.Library()

@register.simple_tag()
def reverse_url(request,name,*args,**kwargs):
    base_url = reverse(name,args=args,kwargs=kwargs)
    params = request.GET.urlencode()
    if not params:
        return base_url
    return '{}?{}'.format(base_url,params)

def rev_url(request,name,*args,**kwargs):
    base_url = reverse(name,args=args,kwargs=kwargs)
    url = request.get_full_path()
    qd = QueryDict(mutable=True)
    qd['next'] = url
    return '{}?{}'.format(base_url,qd.urlencode())