from datetime import datetime
from fpmonitor.models import AlertingChain, Node
import json

from consts import *

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.db import IntegrityError
from django.utils import timezone


def home(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/index')
    else:
        return HttpResponseRedirect('/login')


@login_required
def index(request):
    node_list = Node.objects.filter(owner=request.user)
    return render(request, 'index.html', {'username': request.user.username, 'node_list': node_list, 'test_mode': settings.TEST_MODE})


def user_login(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    else:
        try:
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponseRedirect('/index')
                else:
                    return render(request, 'login.html', {'error': True, 'inactive_login': True})
            else:
                return render(request, 'login.html', {'error': True, 'failed_login': True})
        except Exception as e:
            return HttpResponse("NOK %s %s" % (request, e), status=402)


def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/login')


@csrf_exempt
def receive_data(request):
    try:
        data = json.loads(request.POST.get('data'))
        owner = User.objects.get(pk=int(data['node_user_id']))
        try:
            node = Node.create_node(owner, data['node_name'])
        except IntegrityError:
            node = Node.objects.get(name=data['node_name'], owner=owner)
        node.kernel_version = data['kernel']
        node.uptime = data['uptime']
        node.os_type = data['system'] if data['system'] != "Darwin" else "MacOS X"
        node.os_version = data['distribution']
        node.loadavg_5 = data['loadavg'][0]
        node.loadavg_10 = data['loadavg'][1]
        node.loadavg_15 = data['loadavg'][2]
        node.memory_usage = int(data['memory_usage'])
        node.last_sync = timezone.now()
        node.save()
        return HttpResponse("OK %s" % data, status=200)
    except Exception as e:
        return HttpResponse("NOK %s %s" % (e, data), status=200)


@csrf_exempt
@login_required
def api_node_maintenance(request):
    try:
        node_id = request.POST['id']
        mode = False if request.POST['mode'] == 'true' else True
        node = Node.objects.get(pk=node_id, owner=request.user)
        node.maintenance_mode = mode
        node.save()
        return HttpResponse('OK')
    except Exception as e:
        return HttpResponse('NOK %s' % e, status=200)


@login_required
def show_node(request, node_id):
    try:
        node = Node.objects.get(pk=node_id)
        if node.owner != request.user:
            return HttpResponseRedirect('/index')
        else:
            address = request.POST.get('address')
            if address:
                AlertingChain.create_alerting_chain(node, address)
            return render(request, 'node.html', {'node': node, 'test_mode': settings.TEST_MODE})
    except Exception as e:
        return HttpResponseRedirect('/index')


@login_required
def delete_node(request, node_id):
    result = Node.delete_node(node_id, request)
    return HttpResponseRedirect('/index')


@login_required
def delete_address(request, address_id):
    try:
        AlertingChain.delete_alerting_chain(request.user, address_id)
        if request.META["HTTP_REFERER"]:
            return HttpResponseRedirect(request.META["HTTP_REFERER"])
        else:
            return HttpResponseRedirect('/index')
    except:
        return HttpResponseRedirect('/index')
