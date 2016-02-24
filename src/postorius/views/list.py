# -*- coding: utf-8 -*-
# Copyright (C) 1998-2015 by the Free Software Foundation, Inc.
#
# This file is part of Postorius.
#
# Postorius is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# Postorius is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# Postorius.  If not, see <http://www.gnu.org/licenses/>.

import logging
import csv

from django.http import HttpResponse

from django.contrib import messages
from django.contrib.auth.decorators import (login_required,
                                            user_passes_test)
from django.core.urlresolvers import reverse
from django.forms import formset_factory
from django.shortcuts import render, redirect
from django.template import RequestContext
from django.core.exceptions import ValidationError
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.http import Http404
try:
    from urllib2 import HTTPError
except ImportError:
    from urllib.error import HTTPError

from postorius import utils
from postorius.forms import *
from postorius.auth.decorators import *
from postorius.views.generic import MailingListView


logger = logging.getLogger(__name__)


@login_required
@list_owner_required
def list_members_view(request, list_id, role=None):
    """Display all members of a given list."""
    if role not in ['owner', 'moderator', 'subscriber']:
        return redirect('list_members', list_id, 'subscriber')
    mailing_list = List.objects.get_or_404(fqdn_listname=list_id)
    if request.method == 'POST':
        if role == 'subscriber':
            form = MultipleChoiceForm(request.POST)
            if form.is_valid():
                members = form.cleaned_data['choices']
                for member in members:
                    mailing_list.unsubscribe(member)
                messages.success(request, _('The selected members have been unsubscribed'))
                return redirect('list_members', list_id, role)
        else:
            member_form = MemberForm(request.POST)
            if member_form.is_valid():
                try:
                    getattr(mailing_list, 'add_%s' % role)(member_form.cleaned_data['email'])
                    messages.success(
                        request, _('%(email)s has been added with the role %(role)s.')
                        % {'email': member_form.cleaned_data['email'], 'role': role})
                    return redirect('list_members', list_id, role)
                except HTTPError as e:
                    messages.error(request, _(e.msg))
    else:
        form = MultipleChoiceForm()
        member_form = MemberForm()
    context = {
        'list': mailing_list,
        'role': role,
    }
    if role == 'subscriber':
        context['page_title'] = _('List subscribers')
        if request.GET.get('q'):
            query = context['query'] = request.GET['q']
            if "*" not in query:
                query = '*{}*'.format(query)
            # Proxy the find_members method to insert the query
            method = lambda count, page:  mailing_list.find_members(
                query, count=count, page=page)
        else:
            method = mailing_list.get_member_page
        context['members'] = utils.paginate(
            request, method, count=request.GET.get('count', 25),
            paginator_class=utils.MailmanPaginator)
        context['empty_error'] = _('List has no Subscribers')
        context['count_options'] = [25, 50, 100, 200]
        context['form'] = form
    else:
        context['member_form'] = member_form
        if role == 'owner':
            context['page_title'] = _('List owners')
            context['members'] = mailing_list.owners
            context['form_action'] = _('Add owner')
        elif role == 'moderator':
            context['page_title'] = _('List moderators')
            context['members'] = mailing_list.moderators
            context['empty_error'] = _('List has no moderators')
            context['form_action'] = _('Add moderator')
    return render(request, 'postorius/lists/members.html', context)


@login_required
@list_owner_required
def list_member_options(request, list_id, email):
    template_name = 'postorius/lists/memberoptions.html'
    client = utils.get_client()
    mm_list = List.objects.get_or_404(fqdn_listname=list_id)
    try:
        mm_member = client.get_member(list_id, email)
        member_prefs = mm_member.preferences
    except Mailman404Error:
        return render(request, template_name, {'nolists': 'true'})
    initial_moderation = dict([
        (key, getattr(mm_member, key)) for key in MemberModeration.base_fields
        ])
    if request.method == 'POST':
        if request.POST.get("formname") == 'preferences':
            moderation_form = MemberModeration(initial=initial_moderation)
            preferences_form = UserPreferences(
                request.POST, initial=member_prefs)
            if preferences_form.is_valid():
                if not preferences_form.has_changed():
                    messages.info(request,
                        _("No change to the member's preferences."))
                    return redirect('list_member_options', list_id, email)
                for key in preferences_form.fields.keys():
                    member_prefs[key] = preferences_form.cleaned_data[key]
                try:
                    member_prefs.save()
                except HTTPError as e:
                    messages.error(request, e.msg)
                else:
                    messages.success(request,
                        _("The member's preferences have been updated."))
                    return redirect('list_member_options', list_id, email)
        elif request.POST.get("formname") == 'moderation':
            preferences_form = UserPreferences(initial=member_prefs)
            moderation_form = MemberModeration(
                request.POST, initial=initial_moderation)
            if moderation_form.is_valid():
                if not moderation_form.has_changed():
                    messages.info(request,
                        _("No change to the member's moderation."))
                    return redirect('list_member_options', list_id, email)
                for key in moderation_form.fields.keys():
                    setattr(mm_member, key, moderation_form.cleaned_data[key])
                try:
                    mm_member.save()
                except HTTPError as e:
                    messages.error(request, e.msg)
                else:
                    messages.success(request,
                        _("The member's moderation settings have been updated."))
                    return redirect('list_member_options', list_id, email)
    else:
        preferences_form = UserPreferences(initial=member_prefs)
        moderation_form = MemberModeration(initial=initial_moderation)
    return render(request, template_name, {
        'mm_member': mm_member,
        'list': mm_list,
        'preferences_form': preferences_form,
        'moderation_form': moderation_form,
        })


class ListSummaryView(MailingListView):
    """Shows common list metrics.
    """

    def get(self, request, list_id):
        data =  {'list': self.mailing_list,
                 'userSubscribed': False,
                 'subscribed_address': None}
        if request.user.is_authenticated():
            user_emails = [request.user.email] + request.user.other_emails
            for address in user_emails:
                try:
                    self.mailing_list.get_member(address)
                except ValueError:
                    pass
                else:
                    data['userSubscribed'] = True
                    data['subscribed_address'] = address
                    break # no need to test more addresses
            data['subscribe_form'] = ListSubscribe(user_emails)
        else:
            user_emails = None
        return render(request, 'postorius/lists/summary.html', data)


class ChangeSubscriptionView(MailingListView):
    """Change mailing list subscription
    """

    @method_decorator(login_required)
    def post(self, request, list_id):
        try:
            user_emails = [request.user.email] + request.user.other_emails
            form = ListSubscribe(user_emails, request.POST)
            for address in user_emails:
                try:
                    userMember = self.mailing_list.get_member(address)
                except ValueError:
                    pass
                else:
                    userSubscribed = True
                    old_email = address
                    break # no need to test more addresses
            if form.is_valid():
                email = form.cleaned_data['email']
                if old_email == email:
                    messages.error(request, _('You are already subscribed'))
                else:
                    self.mailing_list.unsubscribe(old_email)
                    self.mailing_list.subscribe(email)
                    messages.success(request, _('Subscription changed to %s') % email)
            else:
                messages.error(request, _('Something went wrong. Please try again.'))
        except MailmanApiError:
            return utils.render_api_error(request)
        except HTTPError as e:
            messages.error(request, e.msg)
        return redirect('list_summary', self.mailing_list.list_id)


class ListSubscribeView(MailingListView):
    """
    view name: `list_subscribe`
    """

    @method_decorator(login_required)
    def post(self, request, list_id):
        """
        Subscribes an email address to a mailing list via POST and
        redirects to the `list_summary` view.
        """
        try:
            user_addresses = [request.user.email] + request.user.other_emails
            form = ListSubscribe(user_addresses, request.POST)
            if form.is_valid():
                email = request.POST.get('email')
                response = self.mailing_list.subscribe(
                    email, pre_verified=True, pre_confirmed=True)
                if type(response) == dict and response.get('token_owner') == \
                        'moderator':
                    messages.success(
                        request, _('Your subscription request has been submitted and is '
                        'waiting for moderator approval.'))
                else:
                    messages.success(request, _('You are subscribed to %s.') %
                                     self.mailing_list.fqdn_listname)
            else:
                messages.error(request, _('Something went wrong. Please try again.'))
        except MailmanApiError:
            return utils.render_api_error(request)
        except HTTPError as e:
            messages.error(request, e.msg)
        return redirect('list_summary', self.mailing_list.list_id)


class ListUnsubscribeView(MailingListView):

    """Unsubscribe from a mailing list."""

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        email = request.POST['email']
        try:
            self.mailing_list.unsubscribe(email)
            messages.success(request, _('%s has been unsubscribed from this list.') % email)
        except MailmanApiError:
            return utils.render_api_error(request)
        except ValueError as e:
            messages.error(request, e)
        return redirect('list_summary', self.mailing_list.list_id)


@login_required
@list_owner_required
def list_mass_subscribe(request, list_id):
    mailing_list = utils.get_client().get_list(list_id)
    if request.method == 'POST':
        form = ListMassSubscription(request.POST)
        if form.is_valid():
            for email in form.cleaned_data['emails']:
                try:
                    validate_email(email)
                    mailing_list.subscribe(
                        address=email, pre_verified=True, pre_confirmed=True, pre_approved=True)
                    messages.success(request,
                                     _('The address %(address)s has been subscribed to %(list)s.') %
                                     {'address':email, 'list': mailing_list.fqdn_listname})
                except MailmanApiError:
                    return utils.render_api_error(request)
                except HTTPError as e:
                    messages.error(request, e)
                except ValidationError:
                    messages.error(request, _('The email address %s is not valid.') % email)
    else:
        form = ListMassSubscription()
    return render(request, 'postorius/lists/mass_subscribe.html',
                  {'form': form, 'list': mailing_list},
                  context_instance=RequestContext(request))


class ListMassRemovalView(MailingListView):

    """Class For Mass Removal"""

    @method_decorator(login_required)
    @method_decorator(list_owner_required)
    def get(self, request, *args, **kwargs):
        form = ListMassRemoval()
        return render(request, 'postorius/lists/mass_removal.html',
                      {'form': form, 'list': self.mailing_list},
                      context_instance=RequestContext(request))

    @method_decorator(list_owner_required)
    def post(self, request, *args, **kwargs):
        form = ListMassRemoval(request.POST)
        if not form.is_valid():
            messages.error(request, _('Please fill out the form correctly.'))
        else:
            for email in form.cleaned_data['emails']:
                try:
                    validate_email(email)
                    self.mailing_list.unsubscribe(email.lower())
                    messages.success(request,
                                    _('The address %(address)s has been unsubscribed from %(list)s.') %
                                     {'email': email, 'list': self.mailing_list.fqdn_listname})
                except MailmanApiError:
                    return utils.render_api_error(request)
                except (HTTPError, ValueError) as e:
                    messages.error(request, e)
                except ValidationError:
                    messages.error(request, _('The email address %s is not valid.') % email)
        return redirect('mass_removal', self.mailing_list.list_id)


def _perform_action(message_ids, action):
    for message_id in message_ids:
        action(message_id)

@login_required
@list_moderator_required
def list_moderation(request, list_id):
    mailing_list = utils.get_client().get_list(list_id)
    if request.method == 'POST':
        form = MultipleChoiceForm(request.POST)
        if form.is_valid():
            message_ids = form.cleaned_data['choices']
            try:
                if 'accept' in request.POST:
                    _perform_action(message_ids, mailing_list.accept_message)
                    messages.success(request, _('The selected messages were accepted'))
                elif 'reject' in request.POST:
                    _perform_action(message_ids, mailing_list.reject_message)
                    messages.success(request, _('The selected messages were rejected'))
                elif 'discard' in request.POST:
                    _perform_action(message_ids, mailing_list.discard_message)
                    messages.success(request, _('The selected messages were discarded'))
            except MailmanApiError:
                return utils.render_api_error(request)
            except HTTPError as e:
                messages.error(request, _('Message could not be found'))
    else:
        form = MultipleChoiceForm()
    held_messages = utils.paginate(
        request, mailing_list.get_held_page,
        count=request.GET.get('count', 20),
        paginator_class=utils.MailmanPaginator)
    context = {
        'list': mailing_list,
        'count_options': [25, 50, 100, 200],
        'held_messages': held_messages,
        'form': form,
        }
    return render(request, 'postorius/lists/held_messages.html', context)


@login_required
@list_owner_required
def csv_view(request, list_id):
    """Export all the subscriber in csv
    """
    mm_lists = []
    try:
        mm_lists = List.objects.get_or_404(fqdn_listname=list_id)
    except MailmanApiError:
        return utils.render_api_error(request)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = (
        'attachment; filename="Subscribers.csv"')

    writer = csv.writer(response)
    if mm_lists:
        for i in mm_lists.members:
            writer.writerow([i.email])

    return response


def _get_choosable_domains(request):
    try:
        domains = Domain.objects.all()
    except MailmanApiError:
        return utils.render_api_error(request)
    choosable_domains = [("", _("Choose a Domain"))]
    for domain in domains:
        choosable_domains.append((domain.mail_host,
                                  domain.mail_host))
    return choosable_domains


@login_required
@user_passes_test(lambda u: u.is_superuser)
def list_new(request, template='postorius/lists/new.html'):
    """
    Add a new mailing list.
    If the request to the function is a GET request an empty form for
    creating a new list will be displayed. If the request method is
    POST the form will be evaluated. If the form is considered
    correct the list gets created and otherwise the form with the data
    filled in before the last POST request is returned. The user must
    be logged in to create a new list.
    """
    mailing_list = None
    if request.method == 'POST':
        choosable_domains = _get_choosable_domains(request)
        form = ListNew(choosable_domains, request.POST)
        if form.is_valid():
            # grab domain
            domain = Domain.objects.get_or_404(
                mail_host=form.cleaned_data['mail_host'])
            # creating the list
            try:
                mailing_list = domain.create_list(
                    form.cleaned_data['listname'])
                mailing_list.add_owner(form.cleaned_data['list_owner'])
                list_settings = mailing_list.settings
                list_settings["description"] = form.cleaned_data['description']
                list_settings["advertised"] = form.cleaned_data['advertised']
                list_settings.save()
                messages.success(request, _("List created"))
                return redirect("list_summary",
                                list_id=mailing_list.list_id)
            # TODO catch correct Error class:
            except HTTPError as e:
                return render(request, 'postorius/errors/generic.html', {'error': e})
    else:
        choosable_domains = _get_choosable_domains(request)
        form = ListNew(choosable_domains,
                       initial={'list_owner': request.user.email})
    return render(request, template, {'form': form})


def list_index(request, template='postorius/index.html'):
    """Show a table of all public mailing lists.
    """
    if request.method == 'POST':
        return redirect("list_summary", list_id=request.POST["list"])
    lists = []
    error = None
    only_public = True
    if request.user.is_superuser:
        only_public = False
    try:
        lists = sorted(List.objects.all(only_public=only_public),
                       key=lambda l: l.fqdn_listname)
        logger.debug(lists)
    except MailmanApiError:
        return utils.render_api_error(request)
    choosable_domains = _get_choosable_domains(request)
    return render(request, template,
            {'count_options': [10, 25, 50, 100, 200], 'error': error,
            'lists': utils.paginate(request, lists, count=request.GET.get('count', 10)),
            'domain_count': len(choosable_domains)})


@login_required
@list_owner_required
def list_delete(request, list_id):
    """Deletes a list but asks for confirmation first.
    """
    try:
        the_list = List.objects.get_or_404(fqdn_listname=list_id)
    except MailmanApiError:
        return utils.render_api_error(request)
    if request.method == 'POST':
        the_list.delete()
        return redirect("list_index")
    else:
        submit_url = reverse('list_delete',
                             kwargs={'list_id': list_id})
        cancel_url = reverse('list_index',)
        return render(request, 'postorius/lists/confirm_delete.html',
                {'submit_url': submit_url, 'cancel_url': cancel_url, 'list': the_list})


@login_required
@list_moderator_required
def accept_held_message(request, list_id, msg_id):
    """Accepts a held message.
    """
    try:
        the_list = List.objects.get_or_404(fqdn_listname=list_id)
        the_list.accept_message(msg_id)
    except MailmanApiError:
        return utils.render_api_error(request)
    except HTTPError as e:
        messages.error(request, e.msg)
        return redirect('list_held_messages', the_list.list_id)
    messages.success(request, _('The message has been accepted.'))
    return redirect('list_held_messages', the_list.list_id)


@login_required
@list_moderator_required
def discard_held_message(request, list_id, msg_id):
    """Discards a held message.
    """
    try:
        the_list = List.objects.get_or_404(fqdn_listname=list_id)
        the_list.discard_message(msg_id)
    except MailmanApiError:
        return utils.render_api_error(request)
    except HTTPError as e:
        messages.error(request, e.msg)
        return redirect('list_held_messages', the_list.list_id)
    messages.success(request, _('The message has been discarded.'))
    return redirect('list_held_messages', the_list.list_id)


@login_required
@list_moderator_required
def defer_held_message(request, list_id, msg_id):
    """Defers a held message for a later decision.
    """
    try:
        the_list = List.objects.get_or_404(fqdn_listname=list_id)
        the_list.defer_message(msg_id)
    except MailmanApiError:
        return utils.render_api_error(request)
    except HTTPError as e:
        messages.error(request, e.msg)
        return redirect('list_held_messages', the_list.list_id)
    messages.success(request, _('The message has been deferred.'))
    return redirect('list_held_messages', the_list.list_id)


@login_required
@list_moderator_required
def reject_held_message(request, list_id, msg_id):
    """Rejects a held message.
    """
    try:
        the_list = List.objects.get_or_404(fqdn_listname=list_id)
        the_list.reject_message(msg_id)
    except MailmanApiError:
        return utils.render_api_error(request)
    except HTTPError as e:
        messages.error(request, e.msg)
        return redirect('list_held_messages', the_list.list_id)
    messages.success(request, _('The message has been rejected.'))
    return redirect('list_held_messages', the_list.list_id)


@login_required
@list_moderator_required
def list_subscription_requests(request, list_id):
    """Shows a list of held messages.
    """
    try:
        m_list = List.objects.get_or_404(fqdn_listname=list_id)
    except MailmanApiError:
        return utils.render_api_error(request)
    return render(request, 'postorius/lists/subscription_requests.html',{'list': m_list})


@login_required
@list_moderator_required
def handle_subscription_request(request, list_id, request_id, action):
    """
    Handle a subscription request. Possible actions:
        - accept
        - defer
        - reject
        - discard
    """
    confirmation_messages = {
        'accept': _('The request has been accepted.'),
        'reject': _('The request has been rejected.'),
        'discard': _('The request has been discarded.'),
        'defer': _('The request has been defered.'),
    }
    try:
        m_list = List.objects.get_or_404(fqdn_listname=list_id)
        # Moderate request and add feedback message to session.
        m_list.moderate_request(request_id, action)
        messages.success(request, confirmation_messages[action])
    except MailmanApiError:
        return utils.render_api_error(request)
    except HTTPError as e:
        if e.code == 409:
            messages.success(request,
                _('The request was already moderated: %s') % e.reason)
        else:
            messages.error(request,
                _('The request could not be moderated: %s') % e.reason)
    return redirect('list_subscription_requests', m_list.list_id)


SETTINGS_SECTION_NAMES = (
    ('list_identity', _('List Identity')),
    ('automatic_responses', _('Automatic Responses')),
    ('alter_messages', _('Alter Messages')),
    ('digest', _('Digest')),
    ('message_acceptance', _('Message Acceptance')),
    ('archiving', _('Archiving')),
    ('subscription_policy', _('Subscription Policy')),
)

SETTINGS_FORMS = {
    'list_identity': ListIdentityForm,
    'automatic_responses': ListAutomaticResponsesForm,
    'alter_messages': AlterMessagesForm,
    'digest': DigestSettingsForm,
    'message_acceptance': MessageAcceptanceForm,
    'archiving': ArchiveSettingsForm,
    'subscription_policy': ListSubscriptionPolicyForm,
}


@login_required
@list_owner_required
def list_settings(request, list_id=None, visible_section=None,
                  template='postorius/lists/settings.html'):
    """
    View and edit the settings of a list.
    The function requires the user to be logged in and have the
    permissions necessary to perform the action.

    Use /<NAMEOFTHESECTION>/<NAMEOFTHEOPTION>
    to show only parts of the settings
    <param> is optional / is used to differ in between section and option might
    result in using //option
    """
    if visible_section is None:
        visible_section = 'list_identity'
    try:
        form_class = SETTINGS_FORMS[visible_section]
    except KeyError:
        raise Http404('No such settings section')
    try:
        m_list = List.objects.get_or_404(fqdn_listname=list_id)
        list_settings = m_list.settings
    except (MailmanApiError, HTTPError):
        return utils.render_api_error(request)
    # List settings are grouped an processed in different forms.
    if request.method == 'POST':
        form = form_class(request.POST, mlist=m_list)
        if form.is_valid():
            try:
                for key in form.fields.keys():
                    if key in form_class.mlist_properties:
                        setattr(m_list, key, form.cleaned_data[key])
                    else:
                        list_settings[key] = form.cleaned_data[key]
                list_settings.save()
                messages.success(request, _('The settings have been updated.'))
            except HTTPError as e:
                messages.error(request, _('An error occured: %s') % e.reason)
            return redirect('list_settings', m_list.list_id, visible_section)
    else:
        form = form_class(initial=dict(list_settings), mlist=m_list)

    return render(request, template, {
        'form': form,
        'section_names': SETTINGS_SECTION_NAMES,
        'list': m_list,
        'visible_section': visible_section,
        })

@login_required
@list_owner_required
def remove_role(request, list_id=None, role=None, address=None,
                template='postorius/lists/confirm_remove_role.html'):
    """Removes a list moderator or owner."""
    try:
        the_list = List.objects.get_or_404(fqdn_listname=list_id)
    except MailmanApiError:
        return utils.render_api_error(request)

    redirect_on_success = redirect('list_members', the_list.list_id, role)

    roster = getattr(the_list, '{}s'.format(role))
    if address not in roster:
        messages.error(request,
            _('The user %(email)s is not in the %(role)s group')
            % {'email': address, 'role': role})
        return redirect('list_members', the_list.list_id, role)

    if role == 'owner':
        if len(roster) == 1:
            messages.error(request, _('Removing the last owner is impossible'))
            return redirect('list_members', the_list.list_id, role)
        # the user may not have a other_emails property if it's a superuser
        user_addresses = set([request.user.email]) | \
            set(getattr(request.user, 'other_emails', []))
        if address in user_addresses:
            # The user is removing themselves, redirect to the list info page
            # because they won't have access to the members page anyway.
            redirect_on_success = redirect('list_summary', the_list.list_id)

    if request.method == 'POST':
        try:
            the_list.remove_role(role, address)
        except MailmanApiError:
            return utils.render_api_error(request)
        except HTTPError as e:
            messages.error(
                request, _('The user could not be removed: %(msg)s')
                % {'msg': e.msg})
            return redirect('list_members', the_list.list_id, role)
        messages.success(request, _('The user %(address)s has been removed from the %(role)s group.')
                         % {'address': address, 'role': role})
        return redirect_on_success
    return render(request, template,
            {'role': role, 'address': address, 'list_id': the_list.list_id})


@login_required
@list_owner_required
def remove_all_subscribers(request, list_id):

    """Empty the list by unsubscribing all members."""

    try:
        mlist = List.objects.get_or_404(fqdn_listname=list_id)
        if len(mlist.members) == 0:
            messages.error(request, _('No member is subscribed to the list currently.'))
            return redirect('mass_removal', mlist.list_id)
        if request.method == 'POST':
            try:
                for names in mlist.members:
                    mlist.unsubscribe(names.email)
                messages.success(request, _('All members have been unsubscribed from the list.'))
                return redirect('list_members', mlist.list_id)
            except Exception as e:
                messages.error(request, e)
        return render(request, 'postorius/lists/confirm_removeall_subscribers.html',
                {'list': mlist})
    except MailmanApiError:
        return utils.render_api_error(request)


@login_required
@list_owner_required
def list_bans(request, list_id):
    """
    Ban or unban email addresses.
    """
    # Get the list and cache the archivers property.
    m_list = List.objects.get_or_404(fqdn_listname=list_id)
    ban_list = m_list.bans

    # Process form submission.
    if request.method == 'POST':
        if 'add' in request.POST:
            addban_form = ListAddBanForm(request.POST)
            if addban_form.is_valid():
                try:
                    ban_list.add(addban_form.cleaned_data['email'])
                    messages.success(
                        request, _('The email {} has been banned.'.format(
                        addban_form.cleaned_data['email'])))
                except HTTPError as e:
                    messages.error(
                        request, _('An error occured: %s') % e.reason)
                except ValueError as e:
                    messages.error(request, _('Invalid data: %s') % e)
                return redirect('list_bans', list_id)
        elif 'del' in request.POST:
            try:
                ban_list.remove(request.POST['email'])
                messages.success(
                    request, _('The email {} has been un-banned.'.format(
                    request.POST['email'])))
            except HTTPError as e:
                messages.error(request, _('An error occured: %s') % e.reason)
            except ValueError as e:
                messages.error(request, _('Invalid data: %s') % e)
            return redirect('list_bans', list_id)
            addban_form = ListAddBanForm()
    else:
        addban_form = ListAddBanForm()
    return render(request, 'postorius/lists/bans.html', {
         'list': m_list,
         'addban_form': addban_form,
         })


@login_required
@list_owner_required
def list_header_matches(request, list_id):
    """
    View and edit the list's header matches.
    """
    m_list = List.objects.get_or_404(fqdn_listname=list_id)
    header_matches = m_list.header_matches
    HeaderMatchFormset = formset_factory(
        ListHeaderMatchForm, extra=1, can_delete=True, can_order=True,
        formset=ListHeaderMatchFormset)
    initial_data = [
        dict([
            (key, getattr(hm, key)) for key in ListHeaderMatchForm.base_fields
        ]) for hm in header_matches]

    # Process form submission.
    if request.method == 'POST':
        formset = HeaderMatchFormset(request.POST, initial=initial_data)
        if formset.is_valid():
            if not formset.has_changed():
                return redirect('list_header_matches', list_id)
            # Purge the existing header_matches
            header_matches.clear()
            # Add the ones in the form
            def form_order(f):
                # If ORDER is None (new header match), add it last.
                return f.cleaned_data.get('ORDER') or len(formset.forms)
            errors = []
            for form in sorted(formset, key=form_order):
                if 'header' not in form.cleaned_data:
                    # The new header match form was not filled
                    continue
                if form.cleaned_data.get('DELETE'):
                    continue
                try:
                    header_matches.add(
                        header=form.cleaned_data['header'],
                        pattern=form.cleaned_data['pattern'],
                        action=form.cleaned_data['action'],
                        )
                except HTTPError as e:
                    errors.append(e)
            for e in errors:
                messages.error(
                    request, _('An error occured: %s') % e.reason)
            if not errors:
                messages.success(request,
                    _('The header matches were successfully modified.'))
            return redirect('list_header_matches', list_id)
    else:
        formset = HeaderMatchFormset(initial=initial_data)
    # Adapt the last form to create new matches
    form_new = formset.forms[-1]
    form_new.fields['header'].widget.attrs['placeholder'] = _('New header')
    form_new.fields['pattern'].widget.attrs['placeholder'] = _('New pattern')
    del form_new.fields['ORDER']
    del form_new.fields['DELETE']

    return render(request, 'postorius/lists/header_matches.html', {
         'list': m_list,
         'formset': formset,
         })
