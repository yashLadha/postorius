from mailman.client import Client
from mailmanweb.settings import API_USER, API_PASS, MAILMAN_THEME
from django.utils.translation import gettext as _
from urllib2 import HTTPError

def lists_of_domain(request):
    """ This function is a wrapper to render a list of all 
    available List registered to the current request URL
    """ 
    domain_lists = []
    domainname = None
    message = ""
    if "HTTP_HOST" in request.META.keys() :#TODO only lists of current domains if possible
        #get the URL
        web_host = ('http://%s' % request.META["HTTP_HOST"].split(":")[0])
        domainname = "unregistered Domain"
        #querry the Domain object
        try:
            c = Client('http://localhost:8001/3.0', API_USER, API_PASS)
        except AttributeError, e:
            message="REST API not found / Offline"
        try:            
    	    d = c.get_domain(web_host=web_host)
    	    #workaround LP:802971 - only lists of the current domain #todo a8
	    domainname= d.mail_host
	    for list in c.lists:
	        if list.mail_host == domainname:
		    domain_lists.append(list)
        except HTTPError, e:
	    domain_lists = c.lists
	    message = str(e.code) + _(" - Accesing from an unregistered Domain - showing all lists")

    #return a Dict with the key used in templates
    return {"lists":domain_lists,"domain":domainname, "message":message}
    
def render_MAILMAN_THEME(request):
    """ This function is a wrapper to render the Mailman Theme Variable from Settings
    """
    return {"MAILMAN_THEME":MAILMAN_THEME}

def extend_ajax(request):
    """ This function checks if the request was made using AJAX
    Using Ajax template_extend will base_ajax.html else it will be base.html
    """
    if request.is_ajax():
        extend_template = "mailman-django/base_ajax.html"        
    else:        
        extend_template = "mailman-django/base.html"
    return {"extend_template":extend_template}        
