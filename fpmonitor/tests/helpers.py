import uuid

from fpmonitor.models import Node
from django.contrib.auth.models import User

ADAM_USERNAME = 'adam'
ADAM_EMAIL = 'adam@adam.hu'
ADAM_PASSWORD = 'adamka'
EVA_USERNAME = 'eva'
EVA_EMAIL = 'eva@adam.hu'
EVA_PASSWORD = 'evacska'
CECIL_USERNAME = 'cecil'
CECIL_PASSWORD = 'cilike'
CECIL_EMAIL = 'cilike@cilus.hu'


def create_adam():
    user = User.objects.create_user(username=ADAM_USERNAME, password=ADAM_PASSWORD, email=ADAM_EMAIL)
    user.first_name = 'Adam'
    user.is_active = True
    user.is_staff = True
    user.is_superuser = True
    user.save()
    return user


def create_eva():
    user = User.objects.create_user(username=EVA_USERNAME, password=EVA_PASSWORD, email=EVA_EMAIL)
    user.first_name = 'Eva'
    user.is_active = False
    user.is_staff = False
    user.save()
    return user


def create_cecil():
    user = User.objects.create_user(username=CECIL_USERNAME, password=CECIL_PASSWORD, email=CECIL_EMAIL)
    user.first_name = 'Cilus'
    user.is_active = True
    user.is_staff = False
    user.save()
    return user


def create_nodes(owner, count=1):
    nodes = []
    for i in range(count):
        nome = uuid.uuid1()
        node = Node.create_node(name=name, owner=owner)
        nodes.append(node)
    return nodes


def login_adam(testcase):
    login = testcase.client.login(username=ADAM_USERNAME, password=ADAM_PASSWORD)
    testcase.failUnless(login, 'Could not log in')


def login_eva(testcase):
    login = testcase.client.login(username=EVA_USERNAME, password=EVA_PASSWORD)
    testcase.failUnless(login, 'Could not log in')


def login_cecil(testcase):
    login = testcase.client.login(username=CECIL_USERNAME, password=CECIL_PASSWORD)
    testcase.failUnless(login, 'Could not log in')


def logout(testcase):
    testcase.client.logout()
