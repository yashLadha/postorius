from django.conf import settings

from postorius.tests.mm_setup import setup_mm, teardown_mm, Testobject


test_obj = Testobject()


def setup_module():
    setup_mm(test_obj)


def teardown_module():
    teardown_mm(test_obj)
