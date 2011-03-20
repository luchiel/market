from django.shortcuts import render_to_response
from django.template import RequestContext


def direct_to_template(request, *args, **kwargs):
    if 'context_instance' not in kwargs:
        kwargs['context_instance'] = RequestContext(request)
    return render_to_response(*args, **kwargs)
