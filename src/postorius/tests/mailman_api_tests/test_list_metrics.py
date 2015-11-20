from __future__ import (
    absolute_import, division, print_function, unicode_literals)


import six
import logging


from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import Client, SimpleTestCase
from django.test.utils import override_settings
from six.moves.urllib_error import HTTPError
from six.moves.urllib_parse import quote

from postorius.utils import get_client
from postorius.tests import MM_VCR, API_CREDENTIALS


logger = logging.getLogger(__name__)
vcr_log = logging.getLogger('vcr')
vcr_log.setLevel(logging.WARNING)



@override_settings(**API_CREDENTIALS)
class TestListMetrics(SimpleTestCase):

    @MM_VCR.use_cassette('test_list_metrics.yaml')
    def setUp(self):
        self.mm_client = get_client()
        self.client = Client()
        try:
            self.domain = self.mm_client.create_domain('example.org')
        except HTTPError:
            self.domain = self.mm_client.get_domain('example.org')
        self.domain.create_list('test')
        self.test_list = self.mm_client.get_list('test@example.org')
        User.objects.filter(username='su').delete()
        self.superuser = User.objects.create_superuser(
            'su', 'su@example.com', 'pwd')

    @MM_VCR.use_cassette('test_list_metrics.yaml')
    def test_metrics_page_not_accessible_to_anonymous(self):
        url = reverse('list_metrics', args=['test@example.org'])
        response = self.client.get(url)
        if "%40" not in url: # Django < 1.8
            url = quote(url)
        expected_redirect = "http://testserver%s?next=%s" % (
            settings.LOGIN_URL, url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["location"], expected_redirect)

    @MM_VCR.use_cassette('test_list_metrics.yaml')
    def test_metrics_page_contains_metrics(self):
        self.client.login(username='su', password='pwd')
        response = self.client.get(reverse('list_metrics', args=['test@example.org']))
        self.assertEqual(response.status_code, 200)

    @MM_VCR.use_cassette('test_list_metrics.yaml')
    def tearDown(self):
        self.superuser.delete()
        self.test_list.delete()
        self.mm_client.delete_domain('example.org')
