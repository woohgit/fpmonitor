import uuid

from fpmonitor.models import Node
from django.contrib.auth.models import User

ADAM_USERNAME = 'adam'
ADAM_EMAIL = 'adam@adam.hu'
ADAM_PASSWORD = 'adamka'
EVA_USERNAME = 'eva'
EVA_EMAIL = 'eva@adam.hu'
EVA_PASSWORD = 'evacska'


def create_adam():
    user = User.objects.create_user(username=ADAM_USERNAME, password=ADAM_PASSWORD, email=ADAM_EMAIL)
    user.first_name = 'Adam'
    user.is_active = True
    user.is_staff = False
    user.save()
    return user


def create_eva():
    user = User.objects.create_user(username=EVA_USERNAME, password=EVA_PASSWORD, email=EVA_EMAIL)
    user.first_name = 'Eva'
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
