from django.contrib.auth.models import User

ADAM_USERNAME = 'alice'
ADAM_EMAIL = 'alice@wonderland.hu'
ADAM_PASSWORD = 'Alice'


def create_adam():
    user = User.objects.create_user(username=ADAM_USERNAME, password=ADAM_PASSWORD, email=ADAM_EMAIL)
    user.first_name = 'Adam'
    user.is_active = True
    user.is_staff = False
    user.save()
    return user


def login_adam(testcase):
    login = testcase.client.login(username=ADAM_USERNAME, password=ADAM_PASSWORD)
    testcase.failUnless(login, 'Could not log in')
