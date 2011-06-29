from mailman.client import Client
from settings import API_USER, API_PASS

def lists_of_domain(request):
    """ This function is a wrapper to render a list of all 
    available List registered to the current request URL
    """ 
    #get the URL
    try:    
        web_host = request.META["HTTP_HOST"].split(":")#TODO Django DEV only !
        web_host = web_host[0]
    except: 
        web_host = request.META["HTTP_HOST"]   
    #querry the Domain object
    c = Client('http://localhost:8001/3.0', API_USER, API_PASS)
    d = c.get_domain(None,web_host)
    #workaround LP:802971
    domainname= d.email_host
    domain_lists = []
    for list in c.lists:
        if list.host_name == domainname:
            domain_lists.append(list)
    #return a Dict with the key used in templates
    return {"lists":domain_lists}
