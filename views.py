# -*- coding: utf-8 -*-
from django.http import HttpResponse, HttpResponseRedirect
from django.template import Context, loader
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from django.utils.translation import gettext as _
import re
from mailman_rest_client import MailmanRESTClient, MailmanRESTClientError
from forms import *

def login_required(fn):
    """
    Function (decorator) making sure the user has to log in before 
    they can continue. 
    To use it, add @login_required above the function that requires a 
    user to be logged in. The function requiring login will 
    automatically be added as an argument in the call.
    """
    def _login_decorator(*request, **kwargs):
        """
        Inner decorator to require a user to login. This inner 
        function gets access to the arguments of the function demanding
        login to be processed. 
        The function checks that a valid user name and password has 
        been provided and when this is the case the user gets 
        redirected to the original function.
        """
        # If the user is already logged in, let them continue directly.
        try:
            if request[0].session['member_id']:
                return fn(request[0], **kwargs)
        except:
            pass
        template = 'mailman-django/lists/login.html'
        # Authenticate the user
        # This is just a mockup since the authenticate functionality in 
        # the rest server is still missing.
        # TODO: implement real authenticate when possible
        valid_users = {"james@example.com": "james",
                       "katie@example.com": "katie",
                       "kevin@example.com": "kevin"}
        if request[0].method == 'POST':
            form = Login(request[0].POST)
            if form.is_valid():
                if request[0].POST["address"] in valid_users.keys():
                    if request[0].POST["password"] == valid_users[request[0].POST["address"]]:
                        # TODO: change this to a better id when possible
                        request[0].session['member_id'] = request[0].POST["address"]
                        # make sure to "reset" the method before continuing
                        request[0].method = 'GET'
                        return fn(request[0], **kwargs)
            message = "Your username and password didn't match."
        else:
            message = ""
        return render_to_response(template, {'form': Login(), 
                                             'message': message})
    return _login_decorator

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
        form = ListNew(request.POST)
        if form.is_valid():
            listname = form.cleaned_data['listname']
            try:
                c = MailmanRESTClient('localhost:8001')
            except Exception, e:
                return HttpResponse(e)

            parts = listname.split('@')
            domain = c.get_domain(parts[1])
            if domain.info == 404: # failed to get domain so try 
                                    # creating a new one
                try:
                    domain = c.create_domain(parts[1])
                except MailmanRESTClientError, e: 
                    # I don't think this error can ever appear. -- Anna
                    return HttpResponse(e)
            try:
                response = domain.create_list(parts[0])
                return render_to_response('mailman-django/lists/created.html', 
                                          {'fqdn_listname': response.info['fqdn_listname']})
            except MailmanRESTClientError, e:
                return HttpResponse(e)

    else:
        form = ListNew()

    return render_to_response(template, {'form': form})


def list_index(request, template = 'mailman-django/lists/index.html'):
    """Show a table of all mailing lists.
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
    """
    Display the information there is available for a list. This 
    function also enables subscribing or unsubscribing a user to a 
    list. For the latter two different forms are available for the 
    user to fill in which are evaluated in this function.
    """
    try:
        c = MailmanRESTClient('localhost:8001')
        the_list = c.get_list(fqdn_listname)
    except Exception, e:
        return HttpResponse(e)
    if request.method == 'POST':
        form = False
        # The form enables both subscribe and unsubscribe. As a result
        # we must find out which was the case.
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
                    # the form was valid so try to subscribe the user
                    response = the_list.subscribe(address=email,
                                                real_name=real_name)
                    return HttpResponseRedirect(reverse('list_index'))
                except Exception, e:
                    return HttpResponse(e)
            elif action == "unsubscribe":
                # the form was valid so try to unsubscribe the user
                try:
                    response = the_list.unsubscribe(address=email)
                    template = 'mailman-django/lists/unsubscribed.html'
                    return render_to_response(template, 
                                              {'listname': fqdn_listname})
                except Exception, e:
                    return HttpResponse(e)
        else:
            # the user tried to post an incorrect form so make sure we
            # return the filled in values and let the user try again.
            if action == "subscribe":
                subscribe = ListSubscribe(request.POST)
                unsubscribe = ListUnsubscribe(initial = {'listname': fqdn_listname, 
                                                         'name' : 'unsubscribe'})
            elif action == "unsubscribe":
                subscribe = ListSubscribe(initial = {'listname': fqdn_listname, 
                                                     'name' : 'subscribe'})
                unsubscribe = ListUnsubscribe(request.POST)
    else:
        # the request was a GET request so set the two forms to empty
        # forms
        subscribe = ListSubscribe(initial = {'listname': fqdn_listname, 
                                             'name' : 'subscribe'})
        unsubscribe = ListUnsubscribe(initial = {'listname': fqdn_listname, 
                                                 'name' : 'unsubscribe'})

    listinfo = c.get_list(fqdn_listname)
    return render_to_response(template, {'subscribe': subscribe,
                                         'unsubscribe': unsubscribe,
                                         'fqdn_listname': fqdn_listname,
                                         'listinfo': listinfo})

def list_delete(request, fqdn_listname = None, 
                template = 'mailman-django/lists/index.html'):
    """
    Delete a list by providing the full list name including domain.
    """

    # create a connection to Mailman and get the list
    try:
        c = MailmanRESTClient('localhost:8001')
        the_list = c.get_list(fqdn_listname)
    except Exception, e:
        return HttpResponse(e)
    # get the parts of the list necessary to delete it
    parts = fqdn_listname.split('@')
    domain = the_list.get_domain(parts[1])
    domain.delete_list(parts[0])
    # let the user return to the list index page
    try:
        lists = c.get_lists()
        return render_to_response(template, {'lists': lists})
    except MailmanRESTClientError, e:
        return render_to_response('mailman-django/errors/generic.html', 
                                  {'message': e})

@login_required
def list_settings(request, fqdn_listname = None, 
                  template = 'mailman-django/lists/settings.html'):
    """
    View and edit the settings of a list.
    The function requires the user to be logged in and have the 
    permissions necessary to perform the action.
    """
    message = ""
    try:
        c = MailmanRESTClient('localhost:8001')
        the_list = c.get_list(fqdn_listname)
    except Exception, e:
        return HttpResponse(e)
    if request.method == 'POST':
        form = ListSettings(request.POST)
        if form.is_valid():
            the_list.update_list(request.POST)
            message = "The list has been updated."
    else:
        form = ListSettings(the_list.info)
    return render_to_response(template, {'form': form,
                                         'message': message,
                                         'fqdn_listname': the_list.info['fqdn_listname']})

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
        c = MailmanRESTClient('localhost:8001')
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
                message = "The mass subscription was successful."
                for email in emails:
                    # very simple test if email address is valid
                    parts = email.split('@')
                    if len(parts) == 2 and '.' in parts[1]:
                        the_list.subscribe(address=email, real_name="")
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
                                         'fqdn_listname': the_list.info['fqdn_listname']})
@login_required
def user_settings(request, member = None, 
                  template = 'mailman-django/lists/user_settings.html'):
    """
    Change the user or the membership settings.
    The user must be logged in to be allowed to change any settings.
    TODO: * deal with the actual member and updating the list
          * add CSS to display tabs
          * create a function returning all membership lists for a user
    """
    message = ""
    settings_type = "User "
    membership_forms = []
    # TODO: call function to append all membership lists for a user
    if request.method == 'POST':
        # The form enables both user and member settings. As a result
        # we must find out which was the case.
        tab_type = request.POST.get('name', '')
        if tab_type == "membership":
            membership_forms.append(MembershipSettings(request.POST))
            user_form = UserSettings()
            settings_type = "Membership "
            # TODO: make sure the correct form is evaluated, this is
            # just a temporary solution with one membership list
            if membership_forms[0].is_valid():
                # TODO: add a call to an update function of the member
                # settings HERE, once the member class is created
                message = "The membership settings have been updated."
        else:
            user_form = UserSettings(request.POST)
            membership_forms.append(MembershipSettings())
            if user_form.is_valid(): 
                # TODO: add a call to an update function of the user
                # settings HERE, once the member class is created
                message = "The user settings have been updated."

    else:
        tab_type = "user"
        user_form = UserSettings()
        # TODO: add a call to a function adding all membership forms,
        # this is just a temporary solution until we know what lists
        # the user is subscribed to
        membership_forms.append(MembershipSettings())
        
    return render_to_response(template, {'user_form': user_form,
                                         'membership_forms': membership_forms,
                                         'settings_type': settings_type,
                                         'tab_type': tab_type,
                                         'message': message,
                                         'member': member})

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
