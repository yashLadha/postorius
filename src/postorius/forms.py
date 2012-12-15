# -*- coding: utf-8 -*-
# Copyright (C) 2012 by the Free Software Foundation, Inc.
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

from django import forms
from django.core.validators import validate_email
from django.utils.translation import gettext as _
from fieldset_forms import FieldsetForm


class DomainNew(FieldsetForm):
    """
    Form field to add a new domain
    """
    mail_host = forms.CharField(
        label=_('Mail Host'),
        error_messages={'required': _('Please a domain name'),
                        'invalid': _('Please enter a valid domain name.')},
        required=True)
    web_host = forms.CharField(
        label=_('Web Host'),
        error_messages={'required': _('Please a domain name'),
                        'invalid': _('Please enter a valid domain name.')},
        required=True)
    description = forms.CharField(
        label=_('Description'),
        required=False)
    info = forms.CharField(
        label=_('Information'),
        required=False)

    def clean_mail_host(self):
        mail_host = self.cleaned_data['mail_host']
        try:
            validate_email('mail@' + mail_host)
        except:
            raise forms.ValidationError(_("Enter a valid Mail Host"))
        return mail_host

    def clean_web_host(self):
        web_host = self.cleaned_data['web_host']
        try:
            validate_email('mail@' + web_host)
        except:
            raise forms.ValidationError(_("Please enter a valid Web Host"))
        return web_host

    class Meta:
        """
        Class to handle the automatic insertion of fieldsets and divs.

        To use it: add a list for each wished fieldset. The first item in
        the list should be the wished name of the fieldset, the following
        the fields that should be included in the fieldset.
        """
        layout = [["Please enter Details",
                   "mail_host",
                   "web_host",
                   "description"]]


class NewOwnerForm(forms.Form):
    """Add a list owner."""
    owner_email = forms.EmailField(
        label=_('Email Address'),
        error_messages={
            'required': _('Please enter an email adddress.'),
            'invalid': _('Please enter a valid email adddress.')})


class NewModeratorForm(forms.Form):
    """Add a list moderator."""
    moderator_email = forms.EmailField(
        label=_('Email Address'),
        error_messages={
            'required': _('Please enter an email adddress.'),
            'invalid': _('Please enter a valid email adddress.')})


class ListNew(FieldsetForm):
    """
    Form fields to add a new list. Languages are hard coded which should
    be replaced by a REST lookup of available languages.
    """
    listname = forms.CharField(
        label=_('List Name'),
        required=True,
        error_messages={'required': _('Please enter a name for your list.'),
                        'invalid': _('Please enter a valid list name.')})
    mail_host = forms.ChoiceField()
    list_owner = forms.EmailField(
        label=_('Inital list owner address'),
        error_messages={
            'required': _("Please enter the list owner's email address.")},
        required=True)
    advertised = forms.ChoiceField(
        widget=forms.RadioSelect(),
        label=_('Advertise this list?'),
        error_messages={
            'required': _("Please choose a list type.")},
        required=True,
        choices=(
            (True, _("Advertise this list in list index")),
            (False, _("Hide this list in list index"))))
    description = forms.CharField(
        label=_('Description'),
        required=True)

    def __init__(self, domain_choices, *args, **kwargs):
        super(ListNew, self).__init__(*args, **kwargs)
        self.fields["mail_host"] = forms.ChoiceField(
            widget=forms.Select(),
            label=_('Mail Host'),
            required=True,
            choices=domain_choices,
            error_messages={'required': _("Choose an existing Domain."),
                            'invalid': "ERROR-todo_forms.py"})
        if len(domain_choices) < 2:
            self.fields["mail_host"].help_text=_(
                "Site admin has not created any domains")
            #if len(choices) < 2:
            #    help_text=_("No domains available: " +
            #                "The site admin must create new domains " +
            #                "before you will be able to create a list")
                            

    def clean_listname(self):
        try:
            validate_email(self.cleaned_data['listname'] + '@example.net')
        except:
            raise forms.ValidationError(_("Please enter a valid listname"))
        return self.cleaned_data['listname']

    class Meta:
        """
        Class to handle the automatic insertion of fieldsets and divs.

        To use it: add a list for each wished fieldset. The first item in
        the list should be the wished name of the fieldset, the following
        the fields that should be included in the fieldset.
        """
        layout = [["List Details",
                   "listname",
                   "mail_host",
                   "list_owner",
                   "description",
                   "advertised"], ]


class ListSubscribe(FieldsetForm):
    """Form fields to join an existing list.
    """
    email = forms.EmailField(
        label=_('Your email address'),
        widget=forms.HiddenInput(),
        error_messages={'required': _('Please enter an email address.'),
                        'invalid': _('Please enter a valid email address.')})
    display_name = forms.CharField(label=_('Your name (optional)'),
                                   required=False)


class ListUnsubscribe(FieldsetForm):
    """Form fields to leave an existing list.
    """
    email = forms.EmailField(
        label=_('Your email address'),
        widget=forms.HiddenInput(),
        error_messages={
            'required': _('Please enter an email address.'),
            'invalid': _('Please enter a valid email address.')})


class ListSettings(FieldsetForm):
    """Form fields dealing with the list settings.
    """
    choices = ((True, _('Yes')), (False, _('No')))
    list_name = forms.CharField(
        label=_('List Name'),
        required=False)
    host_name = forms.CharField(
        label=_('Domain host name'),
        required=False)
    fqdn_listname = forms.CharField(
        label=_('Fqdn listname'),
        required=False)
    include_list_post_header = forms.TypedChoiceField(
        coerce=lambda x: x == 'True',
        choices=((True, _('Yes')), (False, _('No'))),
        widget=forms.RadioSelect,
        required=False,
        label= _('Include list post header'))
    include_rfc2369_headers = forms.TypedChoiceField(
        coerce=lambda x: x == 'True',
        choices=((True, _('Yes')), (False, _('No'))),
        widget=forms.RadioSelect,
        required=False,
        label= _('Include RFC2369 headers'))
    autorespond_choices = (
        ("none", _("No automatic response")),
        ("respond_and_discard", _("Respond and discard message")),
        ("respond_and_continue", _("Respond and continue processing")))
    autorespond_owner = forms.ChoiceField(
        choices=autorespond_choices,
        widget=forms.RadioSelect,
        label=_('Autorespond to list owner'))
    autoresponse_owner_text = forms.CharField(
        label=_('Autoresponse owner text'),
        widget=forms.Textarea(),
        required=False)
    autorespond_postings = forms.ChoiceField(
        choices=autorespond_choices,
        widget=forms.RadioSelect,
        label=_('Autorespond postings'))
    autoresponse_postings_text = forms.CharField(
        label=_('Autoresponse postings text'),
        widget=forms.Textarea(),
        required=False)
    autorespond_requests = forms.ChoiceField(
        choices=autorespond_choices,
        widget=forms.RadioSelect,
        label=_('Autorespond requests'))
    autoresponse_request_text = forms.CharField(
        label=_('Autoresponse request text'),
        widget=forms.Textarea(),
        required=False)
    autoresponse_grace_period = forms.CharField(
        label=_('Autoresponse grace period'))
    bounces_address = forms.EmailField(
        label=_('Bounces Address'),
        required=False)
    advertised = forms.TypedChoiceField(
        coerce=lambda x: x == 'True',
        choices=((True, _('Yes')), (False, _('No'))),
        widget=forms.RadioSelect,
        label=_('Advertise the existance of this list?'),
        help_text=('Choose whether to include this list on the list of all lists'))
    filter_content = forms.TypedChoiceField(
        coerce=lambda x: x == 'True',
        choices=((True, _('Yes')), (False, _('No'))),
        widget=forms.RadioSelect,
        required=False,
        label=_('Filter content'))
    collapse_alternatives = forms.TypedChoiceField(
        coerce=lambda x: x == 'True',
        choices=((True, _('Yes')), (False, _('No'))),
        widget=forms.RadioSelect,
        required=False,
        label=_('Collapse alternatives'))
    convert_html_to_plaintext = forms.TypedChoiceField(
        coerce=lambda x: x == 'True',
        choices=((True, _('Yes')), (False, _('No'))),
        widget=forms.RadioSelect,
        required=False,
        label=_('Convert html to plaintext'))
    action_choices = (
        ("hold", _("Hold for moderator")),
        ("reject", _("Reject (with notification)")),
        ("discard", _("Discard (no notification)")),
        ("accept", _("Accept")),
        ("defer", _("Defer")))
    default_member_action = forms.ChoiceField(
        widget=forms.RadioSelect(),
        label=_('Default action to take when a member posts to the list: '),
        error_messages={
            'required': _("Please choose a default member action.")},
        required=True,
        choices=action_choices)
    default_nonmember_action = forms.ChoiceField(
        widget=forms.RadioSelect(),
        label=_('Default action to take when a non-member posts to the'
                'list: '),
        error_messages={
            'required': _("Please choose a default non-member action.")},
        required=True,
        choices=action_choices)
    description = forms.CharField(
        label=_('Description'),
        widget=forms.Textarea())
    digest_size_threshold = forms.DecimalField(
        label=_('Digest size threshold'),
    )
    digest_last_sent_at = forms.IntegerField(
        label=_('Digest last sent at'),
        error_messages={
            'invalid': _('Please provide an integer.')},
        required=False)
    generic_nonmember_action = forms.IntegerField(
        label=_('Generic nonmember action'),
        error_messages={
            'invalid': _('Please provide an integer.')
        }
    )
    mail_host = forms.CharField(
        label=_('Mail Host'),
        error_messages={'required': _('Please a domain name'),
                        'invalid': _('Please enter a valid domain name.')},
        required=True)
    next_digest_number = forms.IntegerField(
        label=_('Next digest number'),
        error_messages={
            'invalid': _('Please provide an integer.'),
        },
        required=False,
    )
    no_reply_address = forms.EmailField(
        label=_('No reply address'),
        required=False,
    )
    posting_pipeline = forms.CharField(
        label=_('Pipeline'),
    )
    post_id = forms.IntegerField(
        label=_('Post ID'),
        error_messages={
            'invalid': _('Please provide an integer.'),
        },
        required=False,
    )
    display_name = forms.CharField(
        label=_('Display name'),
    )
    subject_prefix = forms.CharField(
        label=_('Subject prefix'),
    )
    reply_goes_to_list = forms.ChoiceField(
        label=_('Reply goes to list'),
        widget=forms.Select(),
        error_messages={
            'required': _("Please choose a reply-to action.")},
        choices=(
            ("no_munging", _("No Munging")),
            ("point_to_list", _("Reply goes to list")),
            ("explicit_header", _("Explicit Reply-to header set"))))
    request_address = forms.EmailField(
        label=_('Request address'),
        required=False)
    send_welcome_message = forms.TypedChoiceField(
        coerce=lambda x: x == 'True',
        choices=((True, _('Yes')), (False, _('No'))),
        widget=forms.RadioSelect,
        required=False,
        label=_('Send welcome message'))
    scheme = forms.CharField(
        label=_('Scheme'),
        required=False)
    acceptable_aliases = forms.CharField(
        widget=forms.Textarea(),
        label=_("Acceptable aliases"),
        required=False)
    admin_immed_notify = forms.BooleanField(
        widget=forms.RadioSelect(choices=choices),
        required=False,
        label=_('Admin immed notify'))
    admin_notify_mchanges = forms.BooleanField(
        widget=forms.RadioSelect(choices=choices),
        required=False,
        label=_('Admin notify mchanges'))
    administrivia = forms.BooleanField(
        widget=forms.RadioSelect(choices=choices),
        required=False,
        label=_('Administrivia'))
    anonymous_list = forms.TypedChoiceField(
        coerce=lambda x: x == 'True',
        choices=((True, _('Yes')), (False, _('No'))),
        widget=forms.RadioSelect,
        required=False,
        label=_('Anonymous list'))
    created_at = forms.IntegerField(
        label=_('Created at'),
        widget=forms.HiddenInput(),
        required=False)
    join_address = forms.EmailField(
        label=_('Join address'),
        required=False)
    last_post_at = forms.IntegerField(
        label=_('Last post at'),
        required=False)
    leave_address = forms.EmailField(
        label=_('Leave address'),
        required=False)
    owner_address = forms.EmailField(
        label=_('Owner Address'),
        required=False)
    posting_address = forms.EmailField(
        label=_('Posting Address'),
        required=False)
    #Descriptions used in the Settings Overview Page
    section_descriptions = {
        "List Identity": _("Basic identity settings for the list"),
        "Automatic Responses": _("All options for Autoreply"),
        "Alter Messages": _("Settings that modify member messages"),
        "Digest": _("Digest-related options"),
        "Message Acceptance": _("Options related to accepting messages")}

    def clean_acceptable_aliases(self):
        data = self.cleaned_data['acceptable_aliases']
        return data.splitlines()

    def __init__(self, visible_section, visible_option, *args, **kwargs):
        super(ListSettings, self).__init__(*args, **kwargs)
        # if settings:
        #    raise Exception(settings) # debug
        if visible_option:
            options = []
            for option in self.layout:
                options += option[1:]
            if visible_option in options:
                self.layout = [["", visible_option]]
        if visible_section:
            sections = []
            for section in self.layout:
                sections.append(section[0])
            if visible_section in sections:
                for section in self.layout:
                    if section[0] == visible_section:
                        self.layout = [section]
        try:
            if data:
                for section in self.layout:
                    for option in section[1:]:
                        self.fields[option].initial = settings[option]
        except:
            pass  # empty form

    def truncate(self):
        """
        truncates the form to have only those fields which are in self.layout
        """
        # delete form.fields which are not in the layout
        used_options = []
        for section in self.layout:
            used_options += section[1:]

        for key in self.fields.keys():
            if not(key in used_options):
                del self.fields[key]

    class Meta:
        """Class to handle the automatic insertion of fieldsets and divs.

        To use it: add a list for each wished fieldset. The first item in
        the list should be the wished name of the fieldset, the following
        the fields that should be included in the fieldset.
        """
        # just a really temporary layout to see that it works. -- Anna
        layout = [
            ["List Identity", "display_name", "mail_host", "description",
             "advertised"], # tko - need to add subject_prefix here
            ["Automatic Responses", "autorespond_owner",
             "autoresponse_owner_text", "autorespond_postings",
             "autoresponse_postings_text", "autorespond_requests",
             "autoresponse_request_text", "autoresponse_grace_period",
             "send_welcome_message", "admin_immed_notify",
             "admin_notify_mchanges"],
            ["Alter Messages", "filter_content", "collapse_alternatives",
             "convert_html_to_plaintext", "anonymous_list",
             "include_rfc2369_headers", "reply_goes_to_list",
             "posting_pipeline"], #tko - removed include_list_post_header
            ["Digest", "digest_size_threshold"],
            ["Message Acceptance", "acceptable_aliases", "administrivia",
             "default_nonmember_action", "default_member_action"]]


class Login(FieldsetForm):
    """Form fields to let the user log in.
    """
    user = forms.EmailField(
        label=_('Email address'),
        error_messages={'required': _('Please enter an email address.'),
                        'invalid': _('Please enter a valid email address.')},
        required=True)
    password = forms.CharField(
        label=_('Password'),
        widget=forms.PasswordInput,
        error_messages={'required': _('Please enter your password.'),
                        'invalid': _('Please enter a valid password.')},
        required=True)

    class Meta:
        """
        Class to define the name of the fieldsets and what should be
        included in each.
        """
        layout = [["Login", "user", "password"]]


class ListMassSubscription(FieldsetForm):
    """Form fields to masssubscribe users to a list.
    """
    emails = forms.CharField(
        label=_('Emails to mass subscribe'),
        widget=forms.Textarea,
    )

    class Meta:
        """
        Class to define the name of the fieldsets and what should be
        included in each.
        """
        layout = [["Mass subscription", "emails"]]


class MembershipSettings(FieldsetForm):
    """Form handling the membership settings.
    """
    choices = ((True, _('Yes')), (False, _('No')))
    acknowledge_posts = forms.BooleanField(
        widget=forms.RadioSelect(choices=choices),
        required=False,
        label=_('Acknowledge posts'))
    hide_address = forms.BooleanField(
        widget=forms.RadioSelect(choices=choices),
        required=False,
        label=_('Hide address'))
    receive_list_copy = forms.BooleanField(
        widget=forms.RadioSelect(choices=choices),
        required=False,
        label=_('Receive list copy'))
    receive_own_postings = forms.BooleanField(
        widget=forms.RadioSelect(choices=choices),
        required=False,
        label=_('Receive own postings'))
    delivery_mode = forms.ChoiceField(
        widget=forms.Select(),
        error_messages={
            'required': _("Please choose a mode.")},
        required=False,
        choices=(
            ("", _("Please choose")),
            ("delivery_mode", "some mode...")),
        label=_('Delivery mode'))
    delivery_status = forms.ChoiceField(
        widget=forms.Select(),
        error_messages={
            'required': _("Please choose a status.")},
        required=False,
        choices=(
            ("", _("Please choose")),
            ("delivery_status", "some status...")),
        label=_('Delivery status'))

    class Meta:
        """
        Class to define the name of the fieldsets and what should be
        included in each.
        """
        layout = [["Membership Settings", "acknowledge_posts", "hide_address",
                   "receive_list_copy", "receive_own_postings",
                   "delivery_mode", "delivery_status"]]


class UserNew(FieldsetForm):
    """
    Form field to add a new user
    """
    display_name = forms.CharField(
        label=_('User Name'),
        required=True,
        error_messages={'required': _('Please enter a display name.'),
                        'invalid': _('Please enter a valid display name.')})
    email = forms.EmailField(
        label=_("User's email address"),
        error_messages={
            'required': _("Please enter the user's email address.")},
        required=True)
    password = forms.CharField(
        label=_('Password'),
        required=True,
        error_messages={'required': _('Please enter a password.')},
        widget=forms.PasswordInput(render_value=False))
    password_repeat = forms.CharField(
        label=_('Repeat password'),
        required=True,
        error_messages={'required': _('Please repeat the password.')},
        widget=forms.PasswordInput(render_value=False))

    def clean(self):
        cleaned_data = self.cleaned_data 
        password = cleaned_data.get("password")
        password_repeat = cleaned_data.get("password_repeat")
        if password != password_repeat:
            raise forms.ValidationError("Passwords must be identical.")

        return cleaned_data


class UserSettings(FieldsetForm):
    """Form handling the user settings.
    """
    def __init__(self, address_choices, *args, **kwargs):
        """
        Initialize the user settings with a field 'address' where
        the values are set dynamically in the view.
        """
        super(UserSettings, self).__init__(*args, **kwargs)
        self.fields['address'] = forms.ChoiceField(
            choices=(address_choices),
            widget=forms.Select(),
            error_messages={'required': _("Please choose an address.")},
            required=True,
            label=_('Default email address'))

    id = forms.IntegerField(
        label=_('ID'),
        initial=9,
        widget=forms.HiddenInput(),
        required=False,
        error_messages={
            'invalid': _('Please provide an integer ID.')})
    mailing_list = forms.CharField(
        label=_('Mailing list'),
        widget=forms.HiddenInput(),
        required=False)
    display_name = forms.CharField(
        label=_('Display name'),
        required=False)
    preferred_language = forms.ChoiceField(
        label=_('Default/Preferred language'),
        widget=forms.Select(),
        error_messages={
            'required': _("Please choose a language.")},
        required=False,
        choices=(
            ("", _("Please choose")),
            ("English (USA)", "English (USA)")))
    password = forms.CharField(
        label=_('Change password'),
        widget=forms.PasswordInput,
        required=False,
        error_messages={'required': _('Please enter your password.'),
                        'invalid': _('Please enter a valid password.')})
    conf_password = forms.CharField(
        label=_('Confirm password'),
        widget=forms.PasswordInput,
        required=False,
        error_messages={'required': _('Please enter your password.'),
                        'invalid': _('Please enter a valid password.')})

    class Meta:
        """
        Class to define the name of the fieldsets and what should be
        included in each.
        """
        layout = [["User settings", "display_name", "password",
                   "conf_password", "preferred_language", "address"]]


class ListDeleteForm(forms.Form):
    list_name = forms.EmailField(widget=forms.HiddenInput())
