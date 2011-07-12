# -*- coding: utf-8 -*-
# Copyright (C) 1998-2010 by the Free Software Foundation, Inc.
#
# This file is part of GNU Mailman.
#
# GNU Mailman is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# GNU Mailman is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# GNU Mailman.  If not, see <http://www.gnu.org/licenses/>.

from django.http import HttpResponse, HttpResponseRedirect
from django.template import Context, loader, RequestContext
from django.shortcuts import render_to_response, redirect
from django.core.urlresolvers import reverse
from django.utils.translation import gettext as _
import re
from mailman.client import Client
from forms import *
from settings import API_USER, API_PASS
import sys #Error handing info

def login_required(fn):
    """
    Function (decorator) making sure the user has to log in before 
    they can continue. 
    To use it, add @login_required above the function that requires a 
    user to be logged in. The function requiring login will 
    automatically be added as an argument in the call.
    """
    def _login_decorator(*args, **kwargs):
        """
        Inner decorator to require a user to login. This inner 
        function gets access to the arguments of the function demanding
        login to be processed. 
        The function checks that a valid user name and password has 
        been provided and when this is the case the user gets 
        redirected to the original function.
        """
        # If the user is already logged in, let them continue directly.
        request = args[0]
        try:
            if request.session['member_id']:
                return fn(*args, **kwargs)
        except:
            pass
        template = 'mailman-django/login.html'
        # Authenticate the user
        # This is just a mockup since the authenticate functionality in 
        # the rest server is still missing.
        # TODO: implement real authenticate when possible
        valid_users = {"james@example.com": "james",
                       "katie@example.com": "katie",
                       "kevin@example.com": "kevin"}
        if request.method == 'POST':
            form = Login(request.POST)
            if form.is_valid():
                if request.POST["addr"] in valid_users.keys():
                    if request.POST["psw"] == valid_users[request.POST["addr"]]:
                        # TODO: change this to a better id when possible
                        request.session['member_id'] = request.POST["addr"]
                        # make sure to "reset" the method before continuing
                        request.method = 'GET'
                        return fn(*args, **kwargs)
            message = "Your username and password didn't match."
        else:
            message = ""
        return render_to_response(template, {'form': Login(), 
                                             'message': message})
    return _login_decorator

@login_required
def domains(request, template = 'mailman-django/domains.html'):
    message=""
    if request.method == 'POST':
        form = DomainNew(request.POST)
        try:
            c = Client('http://localhost:8001/3.0', API_USER, API_PASS)
        except Exception, e:
            return HttpResponse(e)
        if form.is_valid():
            mail_host = form.cleaned_data['mail_host']
            web_host = form.cleaned_data['web_host']
            description = form.cleaned_data['description']
            try:
                domain = c.create_domain(mail_host,web_host,description)
            except Exception, e:
                message=e
    else:
        try:
            c = Client('http://localhost:8001/3.0', API_USER, API_PASS)
        except Exception, e: 
            return HttpResponse(e)
        form = DomainNew()  
    try:
        existing_domains = c.domains
       
    except Exception, e: 
        return HttpResponse(e)
        
    return render_to_response(template, {'form': form,
                                        'domains':existing_domains,
                                        'message':message,
                                        },context_instance=RequestContext(request))        

@login_required
def administration(request, template = 'mailman-django/lists/new.html'):
    """
    Administration dashboard used for Menu navigation
    """
    
    return render_to_response('mailman-django/errors/generic.html', 
                                  {'message':  "This Site is in preperation."})#TODO

@login_required
def list_new(request, template = 'mailman-django/lists/new.html'):
    """
    Add a new mailing list. 
    If the request to the function is a GET request an empty form for 
    creating a new list will be displayed. If the request method is 
    POST the form will be evaluated. If the form is considered
    correct the list gets created and otherwise the form with the data
    filled in before the last POST request is returned. The user must
    be logged in to create a new list.
    """
    if request.method == 'POST':
        try:
            c = Client('http://localhost:8001/3.0', API_USER, API_PASS)
        except Exception, e:
            return HttpResponse(e)
        choosable_domains = [("",_("Choose a Domain"))]
        for domain in c.domains:
            choosable_domains.append((domain.email_host,domain.email_host))
        form = ListNew(choosable_domains,request.POST)

        if form.is_valid():
            #connect and grab domain
            try:
                c = Client('http://localhost:8001/3.0', API_USER, API_PASS)    
            except Exception, e:
                return HttpResponse(e)
            domain = c.get_domain(form.cleaned_data['mail_host'])
            #creating the list
            try:
                mailing_list = domain.create_list(form.cleaned_data['listname'])
            except Exception, e:
                form._errors["NON_FIELD_ERRORS"]=forms.util.ErrorList() 
                form._errors["NON_FIELD_ERRORS"].append(e)
            #saving settings
            settings = mailing_list.settings
            """
            settings["description"] = form.cleaned_data['description']
            #settings["owner_address"] = form.cleaned_data['list_owner'] #TODO: Readonly
            #settings["???"] = form.cleaned_data['list_type'] #TODO not found in REST
            #settings["???"] = form.cleaned_data['languages'] #TODO not found in REST
            settings.save()"""
            try:
                return render_to_response('mailman-django/lists/created.html', 
                                          {'fqdn_listname': settings['fqdn_listname']}
                                          ,context_instance=RequestContext(request))
            except Exception, e:
                return HttpResponse(e)
    else:
        try:
            c = Client('http://localhost:8001/3.0', API_USER, API_PASS)
        except Exception, e:
            return HttpResponse(e)
        choosable_domains = [("",_("Choose a Domain"))]
        for domain in c.domains:
            choosable_domains.append((domain.email_host,domain.email_host))
        form = ListNew(choosable_domains)
        
    return render_to_response(template, {'form': form},context_instance=RequestContext(request))


def list_index(request, template = 'mailman-django/lists/index.html'):
    """Show a table of all mailing lists.
    """
    if request.method == 'POST':
        return redirect("/lists/"+request.POST["list"])
        
    else:
        try:
            c = Client('http://localhost:8001/3.0', API_USER, API_PASS)
        except Exception, e:
            return render_to_response('mailman-django/errors/generic.html', 
                                      {'message':  "Unexpected error:"+ e.message},context_instance=RequestContext(request))

        try:
            lists = c.lists
            return render_to_response(template, {'lists': lists},context_instance=RequestContext(request))
        except Exception, e:
            return render_to_response('mailman-django/errors/generic.html', 
                                      {'message':  "Unexpected error:"+ e.message},context_instance=RequestContext(request))


def list_subscriptions(request, fqdn_listname = None, 
              template = 'mailman-django/lists/subscriptions.html',option="",*args, **kwargs):
    """
    Display the information there is available for a list. This 
    function also enables subscribing or unsubscribing a user to a 
    list. For the latter two different forms are available for the 
    user to fill in which are evaluated in this function.
    """
    try:
        c = Client('http://localhost:8001/3.0', API_USER, API_PASS)
        the_list = c.get_list(fqdn_listname)
    except Exception, e:
        return HttpResponse(e)
    if option:
        if option == "subscribe":
            form_subscribe = ListSubscribe()
        if option == "unsubscribe":
            form_unsubscribe = ListUnsubscribe()
    else:
        form_subscribe = None
        form_unsubscribe = None        
        
    if request.method == 'POST':
        form = False
        # The form enables both subscribe and unsubscribe. As a result
        # we must find out which was the case.
        action = request.POST.get('name', '')
        
        if action == "subscribe":
            form = ListSubscribe(request.POST)
            if form.is_valid():
                # the form was valid so try to subscribe the user
                fqdn_listname = form.cleaned_data['listname']
                try:
                    response = the_list.subscribe(address=form.cleaned_data['email'],real_name=form.cleaned_data.get('real_name', ''))
                    return HttpResponseRedirect(reverse('list_subscriptions'))
                except Exception, e:
                    return HttpResponse(e)
            else:
                form_subscribe = ListSubscribe(request.POST)
                form_unsubscribe = ListUnsubscribe(initial = {'fqdn_listname': fqdn_listname, 'name' : 'unsubscribe'})       
        elif action == "unsubscribe":
            form = ListUnsubscribe(request.POST)
            if form.is_valid():
                #the form was valid so try to unsubscribe the user
                try:
                    response = the_list.unsubscribe(address=email)
                    return render_to_response('mailman-django/lists/unsubscribed.html', 
                                              {'fqdn_listname': fqdn_listname},context_instance=RequestContext(request))
                except Exception, e:
                    return HttpResponse(e)     
            else:
                form_subscribe = ListSubscribe(initial = {'fqdn_listname': fqdn_listname, 'name' : 'subscribe'})
                form_unsubscribe = ListUnsubscribe(request.POST)

    else:
        # the request was a GET request so set the two forms to empty
        # forms
        form_subscribe = ListSubscribe(initial = {'fqdn_listname': fqdn_listname, 
                                             'name' : 'subscribe'})
        form_unsubscribe = ListUnsubscribe(initial = {'fqdn_listname': fqdn_listname, 
                                                 'name' : 'unsubscribe'})
    listinfo = c.get_list(fqdn_listname)#TODO
    return render_to_response(template, {'form_subscribe': form_subscribe,
                                         'form_unsubscribe': form_unsubscribe,
                                         'fqdn_listname': fqdn_listname,
                                         'listinfo': listinfo}
                                         ,context_instance=RequestContext(request))

@login_required
def list_delete(request, fqdn_listname = None, 
                template = 'mailman-django/lists/index.html'):
    """
    Delete a list by providing the full list name including domain.
    """

    # create a connection to Mailman and get the list
    try:
        c = Client('http://localhost:8001/3.0', API_USER, API_PASS)
        the_list = c.get_list(fqdn_listname)
    except Exception, e:
        return HttpResponse(e)
    the_list.delete()
    # let the user return to the list index page
    try:
        lists = c.lists
        return redirect("/lists/")
    except Exception, e:
        return render_to_response('mailman-django/errors/generic.html', 
                                  {'message':  "Unexpected error:"+ str(e)}
                                  ,context_instance=RequestContext(request))

#@login_required #debug
def list_settings(request, fqdn_listname = None, 
                  template = 'mailman-django/lists/settings.html'):
    """
    View and edit the settings of a list.
    The function requires the user to be logged in and have the 
    permissions necessary to perform the action.
    
    Use ?section=<NAMEOFTHESECTION>
    or ?option=<NAMEOFTHEOPTION>
    to show only parts of the settings
    """
    message = ""
    #check for GET values
    try:   visible_section=request.GET["section"]
    except:visible_section=None
    try:   visible_option=request.GET["option"]
    except:visible_option=None
    
    #Create the Connection
    try:
        c = Client('http://localhost:8001/3.0', API_USER, API_PASS)
        the_list = c.get_list(fqdn_listname)
    except Exception, e:
        return HttpResponse(e)
    #Save a Form Processed by POST  
    if request.method == 'POST':
        form = ListSettings(visible_section,visible_option,data=request.POST)
        form.truncate()
        if form.is_valid():
            settings = the_list.settings
            for key in form.fields.keys():
                settings[key] = form.cleaned_data[key]
                settings.save()    
            message = _("The list has been updated.")
        else:
            message = _("Validation Error - The list has not been updated.")
    
    else:#Provide a form with existing values
        #create form and process layout into form.layout
        form = ListSettings(visible_section,visible_option,data=None)
        #create a Dict of all settings which are used in the form
        used_settings={}
        for section in form.layout:
            for option in section[1:]:
                used_settings[option] = the_list.settings[option]
        #recreate the form using the settings
        form = ListSettings(visible_section,visible_option,data=used_settings)
        form.truncate()
                
        
    return render_to_response(template, {'form': form,
                                         'message': message,
                                         'fqdn_listname': the_list.settings['fqdn_listname'],
                                         'visible_option':visible_option,
                                         'visible_section':visible_section,
                                         }
                                         ,context_instance=RequestContext(request))

@login_required
def mass_subscribe(request, fqdn_listname = None, 
                   template = 'mailman-django/lists/mass_subscribe.html'):
    """
    Mass subscribe users to a list.
    This functions is part of the settings for a list and requires the
    user to be logged in to perform the action.
    """
    message = ""
    try:
        c = Client('http://localhost:8001/3.0', API_USER, API_PASS)
        the_list = c.get_list(fqdn_listname)
    except Exception, e:
        return HttpResponse(e)
    if request.method == 'POST':
        form = ListMassSubscription(request.POST)
        if form.is_valid():
            try:
                # The emails to subscribe should each be provided on a
                # separate line so get each of them.
                emails = request.POST["emails"].splitlines()
                for email in emails:
                    # very simple test if email address is valid
                    parts = email.split('@')
                    if len(parts) == 2 and '.' in parts[1]: #TODO - move check to clean method of the form - see example in django docs
                        try:
                            the_list.subscribe(address=email, real_name="")
                            message = "The mass subscription was successful."
                        except Exception, e:
                            form._errors["NON_FIELD_ERRORS"]=forms.util.ErrorList() 
                            form._errors["NON_FIELD_ERRORS"].append(e)       
                    else:
                        # At least one email address wasn't valid so 
                        # overwrite the success message and ask them to
                        # try again.
                        message = "Please enter valid email addresses."
            except Exception, e:
                return HttpResponse(e)
    else:
        # A request to view the page was send so return the form to
        # mass subscribe users.
        form = ListMassSubscription()
    return render_to_response(template, {'form': form,
                                         'message': message,
                                         'fqdn_listname': the_list.settings['fqdn_listname']}
                                         ,context_instance=RequestContext(request))

@login_required
def user_settings(request, member = None, tab = "user",
                  template = 'mailman-django/user_settings.html'):
    """
    Change the user or the membership settings.
    The user must be logged in to be allowed to change any settings.
    TODO: * add CSS to display tabs
          * add missing functionality in REST server and client and 
            change to the correct calls here
    """
    message = ""
    membership_lists = []
    fqdn_listname = ""
    try:
        c = Client('http://localhost:8001/3.0', API_USER, API_PASS)
        user_object = c.get_user(member)
        # address_choices for the 'address' field must be a list of 
        # tuples of length 2
        address_choices = [[addr, addr] for addr in user_object.get_email_addresses()]
    except Exception, e:
        return HttpResponse(e)
    if request.method == 'POST':
        # The form enables both user and member settings. As a result
        # we must find out which was the case.
        if tab == "membership":
            form = MembershipSettings(request.POST)
            if form.is_valid():
                member_object = c.get_member(member, request.GET["list"])
                member_object.update(request.POST)
                message = "The membership settings have been updated."
        else:
            # the post request came from the user tab
            # the 'address' field need choices as a tuple of length 2
            addr_choices = [[request.POST["address"], request.POST["address"]]]
            form = UserSettings(addr_choices, request.POST)
            if form.is_valid(): 
                user_object.update(request.POST)
                # to get the full list of addresses we need to 
                # reinstantiate the form with all the addresses
                # TODO: should return the correct settings from the DB,
                # not just the address_choices (add mock data to _User 
                # class and make the call with 'user_object.info')
                form = UserSettings(address_choices)
                message = "The user settings have been updated."

    else:
        if tab == "membership":
            fqdn_listname = request.GET.get("list", "")
            if fqdn_listname:
                member_object = c.get_member(member, fqdn_listname)
                # TODO: add delivery_mode and deliver_status from a 
                # list of tuples at one point, currently we hard code
                # them in forms.py
                # instantiate the form with the correct member info
                form = MembershipSettings(member_object.info)
            else:
                form = None
                membership_lists = user_object.get_lists()
        else:
            # TODO: should return the correct settings from the DB,
            # not just the address_choices (add mock data to _User 
            # class and make the call with 'user_object.info') The 'language'
            # field must also be added as a list of tuples with correct
            # values (is currently hard coded in forms.py).
            form = UserSettings(address_choices)

    return render_to_response(template, {'form': form,
                                         'tab': tab,
                                         'fqdn_listname': fqdn_listname,
                                         'membership_lists': membership_lists,
                                         'message': message,
                                         'member': member}
                                         ,context_instance=RequestContext(request))

def logout(request):
    """
    Let the user logout.
    Some functions requires the user to be logged in to perform the
    actions. After the user is done, logging out is possible to avoid
    others having rights they should not have.
    """
    try:
        del request.session['member_id']
    except KeyError:
        pass
    return list_index(request, template = 'mailman-django/lists/index.html')
