import logging


from django.conf import settings
from django.utils.translation import gettext as _
from mailman.client import Client
from urllib2 import HTTPError


logger = logging.getLogger(__name__)


def mailmanweb(request):
    """Add template variables to context.
    """
    # extend_template (no page header/footer when requested via AJAX)
    if request.is_ajax():
        extend_template = "mailman-django/base_ajax.html"        
    else:        
        extend_template = "mailman-django/base.html"

    return {
        'MAILMAN_THEME': settings.MAILMAN_THEME,
        'extend_template': extend_template,
        }
