from functools import wraps
from fpmonitor.models import Node
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse


def test_api(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        return f(*args, **kwargs) if settings.TEST_MODE else HttpResponseRedirect('/index')
    return wrapper


@test_api
@login_required
def create_nodes(request, node_count, status, name=None):
    try:
        for i in range(int(node_count)):
            node_name = "node-%s-%s" % (request.user.username, i) if name is None else name
            Node.create_node(request.user, status=status, name=node_name)
    except Exception as exc:
        print "Exception %s" % exc
        return HttpResponse('NOK', status=500)
    return HttpResponse('OK', status=200)


@test_api
@login_required
def cleanup_nodes(request):
    try:
        nodes = Node.objects.filter(owner=request.user)
        for node in nodes:
            node.delete()
    except Exception as exc:
        return HttpResponse('NOK', status=500)
    return HttpResponse('OK', status=200)


@test_api
@login_required
def test_mode_off(request):
    settings.TEST_MODE = False
    return HttpResponse('OK', status=200)


@login_required
def test_mode_on(request):
    if request.user.is_superuser:
        settings.TEST_MODE = True
    return HttpResponse('OK', status=200)
