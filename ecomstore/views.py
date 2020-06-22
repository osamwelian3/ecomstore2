from django.shortcuts import render_to_response, render
from django.template import RequestContext


def file_not_found_404(request, *args, **kwargs):
    page_title = 'Page Not Found'
    return render(request, '404.html', locals(), RequestContext(request), status=404)
