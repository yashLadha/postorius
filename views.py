# -*- coding: utf-8 -*-
from django.http import HttpResponse, HttpResponseRedirect
from django.template import Context, loader
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from django.utils.translation import gettext as _
import re
from mailman_rest_client import MailmanRESTClient, MailmanRESTClientError
from forms import ListNew, ListSubscribe, ListUnsubscribe


def list_new(request, template = 'mailman-django/lists/new.html'):
    """Show or process form to add a new mailing list
    """
    if request.method == 'POST':
        form = ListNew(request.POST)
        if form.is_valid():
            listname = form.cleaned_data['listname']
            try:
                c = MailmanRESTClient('localhost:8001')
            except Exception, e:
                return HttpResponse(e)

            parts = listname.split('@')
            try:
                r = c.read_domain(parts[1])
            except MailmanRESTClientError, e:
                try:
                    c.create_domain(parts[1])
                except MailmanRESTClientError, e:
                    return HttpResponse(e)

            try:
                response = c.create_list(fqdn_listname=listname)
                return HttpResponseRedirect(reverse('list_index'))
            except MailmanRESTClientError, e:
                return HttpResponse(e)
            
    else:
        form = ListNew()
    
    return render_to_response(template, {'form': form})


def list_index(request, template = 'mailman-django/lists/index.html'):
    """Show a table of all mailing lists
    """
    try:
        c = MailmanRESTClient('localhost:8001')
    except MailmanRESTClientError, e:
        return render_to_response('mailman-django/errors/generic.html', 
                                  {'message': e})

    try:
        lists = c.get_lists()
        return render_to_response(template, {'lists': lists})
    except MailmanRESTClientError, e:
        return render_to_response('mailman-django/errors/generic.html', 
                                  {'message': e})


def list_info(request, fqdn_listname = None, 
              template = 'mailman-django/lists/info.html'):
    """Display list info and/or subscribe or unsubscribe a user to a list
    """
    try:
        c = MailmanRESTClient('localhost:8001')
    except Exception, e:
        return HttpResponse(e)
    if request.method == 'POST':
        form = False
        action = request.POST.get('name', '')
        if action == "subscribe":
            form = ListSubscribe(request.POST)
        elif action == "unsubscribe":
            form = ListUnsubscribe(request.POST)
        if form and form.is_valid():
            listname = form.cleaned_data['listname']
            email = form.cleaned_data['email']
            if action == "subscribe":
                real_name = form.cleaned_data.get('real_name', '')
                try:
                    response = c.subscribe_list(fqdn_listname=listname,
                                                address=email,
                                                real_name=real_name)
                    return HttpResponseRedirect(reverse('list_index'))
                except Exception, e:
                    return HttpResponse(e)
            elif action == "unsubscribe":
                try:
                    response = c.leave_list(fqdn_listname=listname, 
                                            address=email) # doesn't throw error when not subscribed...
                    return render_to_response('mailman-django/lists/unsubscribed.html', 
                                              {'listname': fqdn_listname})
                except Exception, e:
                    return HttpResponse(e)
        else:
            if action == "subscribe":
                subscribe = ListSubscribe(request.POST)
                unsubscribe = ListUnsubscribe(initial = {'listname': fqdn_listname, 
                                                         'name' : 'unsubscribe'})
            elif action == "unsubscribe":
                subscribe = ListSubscribe(initial = {'listname': fqdn_listname, 
                                                     'name' : 'subscribe'})
                unsubscribe = ListUnsubscribe(request.POST)
    else:
        subscribe = ListSubscribe(initial = {'listname': fqdn_listname, 
                                             'name' : 'subscribe'})
        unsubscribe = ListUnsubscribe(initial = {'listname': fqdn_listname, 
                                                 'name' : 'unsubscribe'})

    listinfo = c.read_list(fqdn_listname)

    return render_to_response(template, {'subscribe': subscribe,
                                         'unsubscribe': unsubscribe,
                                         'fqdn_listname': fqdn_listname,
                                         'listinfo': listinfo})
