from mailman.client import Client
from settings import API_USER, API_PASS
from django.utils.translation import gettext as _
from urllib2 import HTTPError

def lists_of_domain(request):
    """ This function is a wrapper to render a list of all 
    available List registered to the current request URL
    """ 
    domain_lists = []
    message = ""
    if "HTTP_HOST" in request.META.keys() :#TODO only lists of current domains if possible
        #get the URL
        web_host = request.META["HTTP_HOST"].split(":")[0]
        #querry the Domain object
        try:
            c = Client('http://localhost:8001/3.0', API_USER, API_PASS)
            d = c.get_domain(None,web_host)
            #workaround LP:802971
            domainname= d.email_host
            for list in c.lists:
                if list.host_name == domainname:
                    domain_lists.append(list)
        except HTTPError, e:
            domain_lists = c.lists
            message = str(e.code) + _(" - Accesing from an unregistered Domain - showing all lists")

    #return a Dict with the key used in templates
    return {"lists":domain_lists, "message":message}
