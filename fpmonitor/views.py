from fpmonitor.models import Node

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render


def home(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/index')
    else:
        return HttpResponseRedirect('/login')


@login_required
def index(request):
    node_list = Node.objects.filter(owner=request.user)
    return render(request, 'index.html', {'username': request.user.username, 'node_list': node_list})


def user_login(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    else:
        username = request.POST['username']
        password = request.POST['password']
        try:
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponseRedirect('/index')
                else:
                    return render(request, 'login.html', {'error': True, 'inactive_login': True})
            else:
                return render(request, 'login.html', {'error': True, 'failed_login': True})

                # TODO: wooh - invalid login
        except Exception as e:
            return HttpResponse("NOK %s" % request, 402)


def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/login')
