from django.http import HttpResponse


def home(request):
    return HttpResponse("OK %s" % request)
