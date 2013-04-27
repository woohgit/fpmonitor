from functools import wraps
from fpmonitor.models import Node
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse


def test_api(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if settings.TEST_MODE:
            return f(*args, **kwargs)
        else:
            return HttpResponseRedirect('/index')
    return wrapper


@test_api
@login_required
def create_nodes(request, node_count):
    try:
        for i in range(int(node_count)):
            name = "node-%s-%s" % (request.user.username, i)
            Node.create_node(request.user, name)
    except Exception as exc:
        print "Hiba %s" % exc
    return HttpResponse('OK', 200)


@test_api
@login_required
def cleanup_nodes(request):
    try:
        nodes = Node.objects.filter(owner=request.user)
        for node in nodes:
            node.delete()
    except Exception as exc:
        print "Hiba %s" % exc
    return HttpResponse('OK', 200)
