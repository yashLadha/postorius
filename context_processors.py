#WEB List selector → TODO → MOVE to Context Processors
        try:    
            web_host = request.META["HTTP_HOST"].split(":")#TODO Django DEV only !
            web_host = web_host[0]
        except: 
            web_host = request.META["HTTP_HOST"]               
        d = c.get_domain(None,web_host)
        domainname= d.email_host
        domain_lists = []
        for list in c.lists:
            if list.host_name == domainname:
                domain_lists.append(list)
                
                
                
                LISTS: domains
                
                
return [(lists,domain....



