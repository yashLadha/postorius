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

from django import forms
from django.core.validators import validate_email
from django.utils.translation import gettext as _
from fieldset_forms import FieldsetForm

#Fieldsets for use within the views
class DomainNew(FieldsetForm):
    """ 
    Form field to add a new domain
    """
    mail_host = forms.CharField(
        label = _('Mail Host'), 
        error_messages = {'required': _('Please a domain name'), 
                          'invalid': _('Please enter a valid domain name.')},
        required = True
    )
    web_host = forms.CharField(
        label = _('Web Host'), 
        error_messages = {'required': _('Please a domain name'), 
                          'invalid': _('Please enter a valid domain name.')},
        required = True
    )
    description = forms.CharField(
        label = _('Description'), 
        required = False
    )
    def clean_mail_host(self):
        mail_host = self.cleaned_data['mail_host']
        try:    validate_email('mail@' + mail_host)
        except: raise forms.ValidationError(_("Please enter a valid Mail Host (mail.example.net)"))
        return mail_host

    def clean_web_host(self):
        web_host = self.cleaned_data['web_host']
        try:    
            validate_email('mail@' + web_host)
        except: 
            raise forms.ValidationError(_("Please enter a valid Web Host (example.net)"))
        return web_host
    
    class Meta:
        """
        Class to handle the automatic insertion of fieldsets and divs.
        
        To use it: add a list for each wished fieldset. The first item in 
        the list should be the wished name of the fieldset, the following 
        the fields that should be included in the fieldset.
        """
        layout = [["Please enter Details","mail_host", "web_host", "description",]]

    
class ListNew(FieldsetForm):
    """
    Form fields to add a new list. Languages are hard coded which should 
    be replaced by a REST lookup of available languages.
    """    
    languages = (("Arabic", "Arabic"),
                 ("Catalan", "Catalan"),
                 ("Chinese (China)", "Chinese (China)"),
                 ("Chinese (Taiwan)", "Chinese (Taiwan)"),
                 ("Croatian", "Croatian"),
                 ("Czech", "Czech"),
                 ("Danish", "Danish"),
                 ("Dutch", "Dutch"),
                 ("English (USA)", "English (USA)"),
                 ("Estonian", "Estonian"),
                 ("Estonian", "Estonian"),
                 ("Euskara", "Euskara"),
                 ("Finnish", "Finnish"),
                 ("French", "French"),
                 ("German", "German"),
                 ("Hungarian", "Hungarian"),
                 ("Interlingua", "Interlingua"),
                 ("Italian", "Italian"),
                 ("Japanese", "Japanese"),
                 ("Korean", "Korean"),
                 ("Lithuanian", "Lithuanian"),
                 ("Norwegian", "Norwegian"),
                 ("Polish", "Polish"),
                 ("Portuguese", "Portuguese"),
                 ("Portuguese (Brazil)",  "Portuguese (Brazil)"),
                 ("Romanian", "Romanian"),
                 ("Russian", "Russian"),
                 ("Serbian", "Serbian"),
                 ("Slovenian", "Slovenian"),
                 ("Spanish (Spain)", "Spanish (Spain)"),
                 ("Swedish", "Swedish"),
                 ("Turkish", "Turkish"),
                 ("Ukrainian", "Ukrainian"),
                 ("Vietnamese", "Vietnamese"))
    listname = forms.CharField(
        label = _('List Name'), 
        required = True,    
        error_messages = {'required': _('Please enter a name for your list.'), 
                          'invalid': _('Please enter a valid list name.')}
        )                         
    list_owner = forms.EmailField(
        label = _('Inital list owner address'),
        error_messages = {
            'required': _("Please enter the list owner's email address."), 
        },
        required = True)
    advertised = forms.ChoiceField(
        widget = forms.RadioSelect(),
        label = _('List Type'), 
        error_messages = {
            'required': _("Please choose a list type."), 
        },
        required = True,
        choices = (
            (True, _("Advertise this list in list index")),
            (False, _("Hide this list in list index")),
        ))

    languages = forms.MultipleChoiceField(
        label = _('Language'),
        widget = forms.CheckboxSelectMultiple(),
        choices = languages,
        required = False)   
    
    description = forms.CharField(
        label = _('Description'),
        required = True)           

    mail_host = forms.ChoiceField()

    def __init__(self,domain_choices, *args, **kwargs):  
        super(ListNew, self).__init__(*args, **kwargs)  
        self.fields["mail_host"] = forms.ChoiceField(
            widget = forms.Select(),
            label = _('Mail Host'),
            required = True, 
            choices = domain_choices,
            error_messages = {'required': _("Choose an existing Domain."),
                              'invalid':"ERROR-todo_forms.py"  }#todo
            )
            
    def clean_listname(self):
        try:    
            validate_email(self.cleaned_data['listname']+'@example.net')
        except: 
            raise forms.ValidationError(_("Please enter a valid listname (my-list-1)"))
        return self.cleaned_data['listname']

    class Meta:
        """
        Class to handle the automatic insertion of fieldsets and divs.
        
        To use it: add a list for each wished fieldset. The first item in 
        the list should be the wished name of the fieldset, the following 
        the fields that should be included in the fieldset.
        """
        layout = [["List Details", "listname", "mail_host", "list_owner", "description", "advertised"],
                  ["Available Languages", "languages"]]

class ListSubscribe(FieldsetForm):
    """Form fields to join an existing list.
    """
    fqdn_listname = forms.EmailField(
        label = '',#_('List Name'), 
        widget = forms.HiddenInput(),
        error_messages = {
            'required': _('Please enter the mailing list address.'), 
            'invalid': _('Please enter a valid email address.')
        })
    email = forms.EmailField(
        label = _('Your email address'), 
        error_messages = {'required': _('Please enter an email address.'), 
                          'invalid': _('Please enter a valid email address.')})
    real_name = forms.CharField(
        label = _('Your name'), 
        required = False,
    )
    name = forms.CharField(
        label = '', #Name of action
        widget = forms.HiddenInput(),
        initial = 'subscribe',
    )
    
    # should add password! TODO
    class Meta:
        """
        Class to handle the automatic insertion of fieldsets and divs.
        
        To use it: add a list for each wished fieldset. The first item in 
        the list should be the wished name of the fieldset, the following 
        the fields that should be included in the fieldset.
        """
        layout = [["Subscribe", "email","real_name","name","fqdn_listname"]]    

class ListUnsubscribe(FieldsetForm):
    """Form fields to leave an existing list.
    """
    fqdn_listname = forms.EmailField(
        label = '',#_('List Name'), 
        widget = forms.HiddenInput(),
        error_messages = {
            'required': _('Please enter the mailing list address.'), 
            'invalid': _('Please enter a valid email address.')
        }
    )
    email = forms.EmailField(
        label = _('Your email address'), 
        error_messages = {
            'required': _('Please enter an email address.'), 
            'invalid': _('Please enter a valid email address.')
        }
    )
    name = forms.CharField(
        label = '', #Name of action
        widget = forms.HiddenInput(),
        initial = 'unsubscribe',
    )
    class Meta:
        """
        Class to handle the automatic insertion of fieldsets and divs.
        
        To use it: add a list for each wished fieldset. The first item in 
        the list should be the wished name of the fieldset, the following 
        the fields that should be included in the fieldset.
        """
        layout = [["Unsubscribe", "email","name","fqdn_listname"]]        

    # should at one point add the password to be required as well! #TODO
class ListSettings(FieldsetForm):
    """Form fields dealing with the list settings.
    """
    choices = ((True, 'Yes'), (False, 'No'),)
    list_name = forms.CharField(
        label = _('List Name'),
        required = False,
    )
    host_name = forms.CharField(
        label = _('Domain host name'),
        required = False,
    )
    fqdn_listname = forms.CharField(
        label = _('Fqdn listname'),
        required = False,
    )
    #id = forms.IntegerField(    # this should probably not be changeable...
        #label = _('ID'),
        #initial = 9,
        #widget = forms.HiddenInput(),
        #required = False,
        #error_messages = {
            #'invalid': _('Please provide an integer ID.')
        #}
    #)
    list_id = forms.CharField(    # this should probably not be changeable...
        label = _('List ID'),
        required = False,
    )
    http_etag = forms.CharField(
        label = _('Http etag'),
        required = False,
    )
    include_list_post_header = forms.BooleanField(
        widget = forms.RadioSelect(choices = choices), 
        required = False,
        label = _('Include list post header'),
    )
    include_rfc2369_headers = forms.BooleanField(
        widget = forms.RadioSelect(choices = choices), 
        required = False,
        label = _('Include RFC2369 headers'),
    )
    autorespond_owner = forms.BooleanField(
        label = _('Autorespond owner'),
    )
    autoresponse_owner_text = forms.CharField(
        label = _('Autoresponse owner text'),
    )
    autorespond_postings = forms.BooleanField(
        label = _('Autorespond postings'),
    )
    autoresponse_postings_text = forms.CharField(
        label = _('Autoresponse postings text'),
    )
    autorespond_requests = forms.BooleanField(
        label = _('Autorespond requests'),
    )
    autoresponse_request_text = forms.CharField(
        label = _('Autoresponse request text'),
    )
    autoresponse_grace_period = forms.CharField(#TODO - either different type or different Validator !
        label = _('Autoresponse grace period'),
    )
    bounces_address = forms.EmailField(
        label = _('Bounces Address'),
        required = False,
    )
    #ban_list = forms.CharField(
        #label = _('Ban list'),
        #widget = forms.Textarea
    #)
    #bounce_info_stale_after = forms.CharField(
        #label = _('Bounce info stale after'),
    #)
    #bounce_matching_headers = forms.CharField(
        #label = _('Bounce matching headers'),
    #)
    #bounce_notify_owner_on_disable = forms.BooleanField(
        #widget = forms.RadioSelect(choices = choices), 
        #required = False,
        #label = _('Bounce notify owner on disable'),
    #)
    #bounce_notify_owner_on_removal = forms.BooleanField(
        #widget = forms.RadioSelect(choices = choices), 
        #required = False,
        #label = _('Bounce notify owner on removal'),
    #)
    #bounce_processing = forms.BooleanField(
        #widget = forms.RadioSelect(choices = choices), 
        #required = False,
        #label = _('Bounce processing'),
    #)
    #bounce_score_threshold = forms.IntegerField(
        #label = _('Bounce score threshold'),
        #error_messages = {
            #'invalid': _('Please provide an integer.')
        #}
    #)
    #bounce_score_threshold = forms.IntegerField(
        #label = _('Bounce score threshold'),
        #error_messages = {
            #'invalid': _('Please provide an integer.')
        #}
    #)
    #bounce_unrecognized_goes_to_list_owner = forms.BooleanField(
        #widget = forms.RadioSelect(choices = choices), 
        #required = False,
        #label = _('Bounce unrecognized goes to list owner'),
    #)
    #bounce_you_are_disabled_warnings = forms.IntegerField(
        #label = _('Bounce you are disabled warnings'),
        #error_messages = {
            #'invalid': _('Please provide an integer.')
        #}
    #)
    #bounce_you_are_disabled_warnings_interval = forms.CharField(
        #label = _('Bounce you are disabled warnings interval'),
    #)
    #archive = forms.BooleanField(
        #widget = forms.RadioSelect(choices=choices),
        #required = False,
        #label = _('Archive'),
        #)
    #archive_private = forms.BooleanField(
        #widget = forms.RadioSelect(choices=choices),
        #required = False,
        #label = _('Private Archive'),
        #)
    advertised = forms.ChoiceField(
        widget = forms.RadioSelect(),
        label = _('List Type (advertised)'), 
        error_messages = {
            'required': _("Please choose a list type."), 
        },
        required = True,
        choices = (
            (True, _("Advertise this list in List Index")),
            (False, _("Hide this list in Liste Index")),
        ))
    filter_content = forms.BooleanField(
        widget = forms.RadioSelect(choices = choices), 
        required = False,
        label = _('Filter content'),
    )
    collapse_alternatives = forms.BooleanField(
        widget = forms.RadioSelect(choices = choices), 
        required = False,
        label = _('Collapse alternatives'),
    )
    convert_html_to_plaintext = forms.BooleanField(
        widget = forms.RadioSelect(choices = choices), 
        required = False,
        label = _('Convert html to plaintext'),
    )
    #default_member_moderation = forms.BooleanField(
        #widget = forms.RadioSelect(choices = choices), 
        #required = False,
        #label = _('Default member moderation'),
    #)
    description = forms.CharField(
        label = _('Description'),
        widget = forms.Textarea()
    )
    #digest_footer = forms.CharField(
        #label = _('Digest footer'),
    #)
    #digest_header = forms.CharField(
        #label = _('Digest header'),
    #)
    #digest_is_default = forms.BooleanField(
        #widget = forms.RadioSelect(choices = choices), 
        #required = False,
        #label = _('Digest is default'),
    #)
    #digest_send_periodic = forms.BooleanField(
        #widget = forms.RadioSelect(choices = choices), 
        #required = False,
        #label = _('Digest send periodic'),
    #)
    digest_size_threshold = forms.DecimalField(
        label = _('Digest size threshold'),
    )
    #digest_volume_frequency = forms.CharField(
        #label = _('Digest volume frequency'),
    #)
    #digestable = forms.BooleanField(
        #widget = forms.RadioSelect(choices = choices), 
        #required = False,
        #label = _('Digestable'),
    #)
    digest_last_sent_at = forms.IntegerField(
        label = _('Digest last sent at'),
        error_messages = {
            'invalid': _('Please provide an integer.'),
        },
        required = False,
    )
    #discard_these_nonmembers = forms.CharField(
        #label = _('Discard these nonmembers'),
        #widget = forms.Textarea
    #)
    #emergency = forms.BooleanField(
        #widget = forms.RadioSelect(choices = choices), 
        #required = False,
        #label = _('Emergency'),
    #)
    #encode_ascii_prefixes = forms.BooleanField(
        #widget = forms.RadioSelect(choices = choices), 
        #required = False,
        #label = _('Encode ascii prefixes'),
    #)
    #first_strip_reply_to = forms.BooleanField(
        #widget = forms.RadioSelect(choices = choices), 
        #required = False,
        #label = _('First strip reply to'),
    #)
    #forward_auto_discards = forms.BooleanField(
        #widget = forms.RadioSelect(choices = choices), 
        #required = False,
        #label = _('Forward auto discards'),
    #)
    #gateway_to_mail = forms.BooleanField(
        #widget = forms.RadioSelect(choices = choices), 
        #required = False,
        #label = _('Gateway to mail'),
    #)
    #gateway_to_news = forms.BooleanField(
        #widget = forms.RadioSelect(choices = choices), 
        #required = False,
        #label = _('Gateway to news'),
    #)
    #generic_nonmember_action = forms.IntegerField(
        #label = _('Generic nonmember action'),
        #error_messages = {
            #'invalid': _('Please provide an integer.')
        #}
    #)
    #goodbye_msg = forms.CharField(
        #label = _('Goodbye message'),
    #)
    #header_matches = forms.CharField(
        #label = _('Header matches'),
        #widget = forms.Textarea
    #)
    #hold_these_nonmembers = forms.CharField(
        #label = _('Hold these nonmembers'),
        #widget = forms.Textarea
    #)
    #info = forms.CharField(
        #label = _('Information'),
    #)
    #linked_newsgroup = forms.CharField(
        #label = _('Linked newsgroup'),
    #)
    #max_days_to_hold = forms.IntegerField(
        #label = _('Maximum days to hold'),
        #error_messages = {
            #'invalid': _('Please provide an integer.')
        #}
    #)
    #max_message_size = forms.IntegerField(
        #label = _('Maximum message size'),
        #error_messages = {
            #'invalid': _('Please provide an integer.')
        #}
    #)
    #max_num_recipients = forms.IntegerField(
        #label = _('Maximum number of recipients'), 
        #error_messages = {
            #'invalid': _('Please provide an integer.')
        #}
    #)
    #member_moderation_action = forms.BooleanField(
        #widget = forms.RadioSelect(choices = choices), 
        #required = False,
        #label = _('Member moderation action'),
    #)
    #member_moderation_notice = forms.CharField(
        #label = _('Member moderation notice'),
    #)
    #mime_is_default_digest = forms.BooleanField(
        #widget = forms.RadioSelect(choices = choices), 
        #required = False,
        #label = _('Mime is default digest'),
    #)
    #moderator_password = forms.CharField(
        #label = _('Moderator password'),
        #widget = forms.PasswordInput,
        #error_messages = {'required': _('Please enter your password.'), 
                          #'invalid': _('Please enter a valid password.')},
    #)
    #msg_footer = forms.CharField(
        #label = _('Message footer'),
    #)
    #msg_header = forms.CharField(
        #label = _('Message header'),
    #)
    #new_member_options = forms.IntegerField(
        #label = _('New member options'),
        #error_messages = {
            #'invalid': _('Please provide an integer.')
        #}
    #)
    #news_moderation = forms.CharField(
        #label = _('News moderation'),
    #)
    #news_prefix_subject_too = forms.BooleanField(
        #widget = forms.RadioSelect(choices = choices), 
        #required = False,
        #label = _('News prefix subject too'),
    #)
    #nntp_host = forms.CharField(
        #label = _('Nntp host'),
    #)
    #nondigestable = forms.BooleanField(
        #widget = forms.RadioSelect(choices = choices), 
        #required = False,
        #label = _('Nondigestable'),
    #)
    #nonmember_rejection_notice = forms.CharField(
        #label = _('Nonmember rejection notice'),
    #)
    next_digest_number = forms.IntegerField(
        label = _('Next digest number'),
        error_messages = {
            'invalid': _('Please provide an integer.'),
        },
        required = False,
    )
    no_reply_address = forms.EmailField(
        label = _('No reply address'),
        required = False,
    )
    #obscure_addresses = forms.BooleanField(
        #widget = forms.RadioSelect(choices = choices), 
        #required = False,
        #label = _('Obscure addresses'), 
    #)
    #personalize = forms.CharField(
        #label = _('Personalize'),
    #)
    pipeline = forms.CharField(
        label = _('Pipeline'),
    )
    post_id = forms.IntegerField(
        label = _('Post ID'),
        error_messages = {
            'invalid': _('Please provide an integer.'),
        },
        required = False,
    )
    #preferred_language = forms.CharField(
        #label = _('Preferred language'),
    #)
    #private_roster = forms.BooleanField(
        #widget = forms.RadioSelect(choices = choices), 
        #required = False,
        #label = _('Private roster'),
    #)
    real_name = forms.CharField(
        label = _('Real name'),
    )
    #reject_these_nonmembers = forms.CharField(
        #label = _('Reject these nonmembers'),
        #widget = forms.Textarea
    #)
    #reply_goes_to_list = forms.CharField(
        #label = _('Reply goes to list'),
    #)
    #reply_to_address = forms.EmailField(
        #label = _('Reply to address'),
    #)
    #require_explicit_destination = forms.BooleanField(
        #widget = forms.RadioSelect(choices = choices), 
        #required = False,
        #label = _('Require explicit destination'),
    #)
    #respond_to_post_requests = forms.BooleanField(
        #widget = forms.RadioSelect(choices = choices), 
        #required = False,
        #label = _('Respond to post requests'),
    #)
    request_address = forms.EmailField(
        label = _('Request address'),
        required = False,
    )
    #scrub_nondigest = forms.BooleanField(
        #widget = forms.RadioSelect(choices = choices), 
        #required = False,
        #label = _('Scrub nondigest'),
    #)
    #send_goodbye_msg = forms.BooleanField(
        #widget = forms.RadioSelect(choices = choices), 
        #required = False,
        #label = _('Send goodbye message'),
    #)
    #send_reminders = forms.BooleanField(
        #widget = forms.RadioSelect(choices = choices), 
        #required = False,
        #label = _('Send reminders'),
    #)
    #send_welcome_msg = forms.BooleanField(
        #widget = forms.RadioSelect(choices = choices), 
        #required = False,
        #label = _('Send welcome message'),
    #)
    #start_chain = forms.CharField(
        #label = _('Start chain'),
    #)
    #subject_prefix = forms.CharField(
        #label = _('Subject prefix'),
    #)
    #subscribe_auto_approval = forms.CharField(
        #label = _('Subscribe auto approval'),
        #widget = forms.Textarea
    #)
    #subscribe_policy = forms.IntegerField(
        #label = _('Subscribe policy'),
        #error_messages = {
            #'invalid': _('Please provide an integer.')
        #}
    #)
    scheme = forms.CharField(
        label = _('Scheme'),
        required = False,
    )
    #topics = forms.CharField(
        #label = _('Topics'),
        #widget = forms.Textarea
    #)
    #topics_bodylines_limit = forms.IntegerField(
        #label = _('Topics bodylines limit'),
        #error_messages = {
            #'invalid': _('Please provide an integer.')
        #}
    #)
    #topics_enabled = forms.BooleanField(
        #widget = forms.RadioSelect(choices = choices), 
        #required = False,
        #label = _('Topics enabled'),
    #)
    #unsubscribe_policy = forms.IntegerField(
        #label = _('Unsubscribe policy'),
        #error_messages = {
            #'invalid': _('Please provide an integer.')
        #}
    #)
    #welcome_msg = forms.CharField(
        #label = _('Welcome message'),
    #)
    volume = forms.IntegerField(
        label = _('Volume'),
        required = False,
    )
    web_host = forms.CharField(
        label = _('Web host'),
        required = False,
    )
    acceptable_aliases = forms.CharField(
        label = _("Acceptable aliases"),
    )
    admin_immed_notify = forms.BooleanField(
        widget = forms.RadioSelect(choices = choices), 
        required = False,
        label = _('Admin immed notify'),
    )
    admin_notify_mchanges = forms.BooleanField(
        widget = forms.RadioSelect(choices = choices), 
        required = False,
        label = _('Admin notify mchanges'),
    )
    administrivia = forms.BooleanField(
        widget = forms.RadioSelect(choices = choices), 
        required = False,
        label = _('Administrivia'),
    )
    anonymous_list = forms.BooleanField(
        widget = forms.RadioSelect(choices = choices), 
        required = False,
        label = _('Anonymous list'),
    )
    created_at = forms.IntegerField(
        label = _('Created at'),
        widget = forms.HiddenInput(),
        required = False,
    )
    join_address = forms.EmailField(
        label = _('Join address'),
        required = False,
    )
    last_post_at = forms.IntegerField(
        label = _('Last post at'),
        required = False,
    )
    leave_address = forms.EmailField(
        label = _('Leave address'),
        required = False,
    )
    owner_address = forms.EmailField(
        label = _('Owner Address'),
        required = False,
    )
    posting_address = forms.EmailField(
        label = _('Posting Address'),
        required = False,
    )
    #Descriptions used in the Settings Overview Page
    section_descriptions = {
        "List Identity":_("General List settings use"),
        "Automatic Responses":_("All options for Autoreply"),
        "Content Filtering":_("Decide how incoming mails might be filtered"),
        "Digest": _("Modify and check some Digest options"),
        "Privacy" : _("Check the lists privacy standards"),
        "Assorted" : _("Some other Admin stuff"),
        }
    def __init__(self,visible_section,visible_option, *args, **kwargs):  
        super(ListSettings, self).__init__(*args, **kwargs)  
        #if settings:raise Exception(settings) #debug
        if visible_option:
            options=[]
            for option in self.layout:
                options += option[1:]
            if visible_option in options:
                self.layout = [["",visible_option]]
        if visible_section:
            sections=[]
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
            pass #empty form                        
    def truncate(self):
        """
           truncates the form to have only those fields which are in self.layout 
        """
        #delete form.fields which are not in the layout
        used_options=[]
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
            ["List Identity", "real_name", "include_list_post_header", 
             "include_rfc2369_headers"], 
             #"info", "list_name", "host_name", "list_id", "fqdn_listname", 
             #"http_etag", "volume", "web_host"
            ["Automatic Responses", "autorespond_owner",
             "autoresponse_owner_text", "autorespond_postings",
             "autoresponse_postings_text", "autorespond_requests",
             "autoresponse_request_text", "autoresponse_grace_period"],
             #["Bounce", "ban_list", 
             #"bounce_info_stale_after", "bounce_matching_headers", 
             # "bounce_notify_owner_on_disable",
             #"bounce_notify_owner_on_removal", "bounce_processing",
             #"bounce_score_threshold",
             #"bounce_unrecognized_goes_to_list_owner",
             #"bounce_you_are_disabled_warnings",
             #"bounce_you_are_disabled_warnings_interval"],
            #["Archiving", "archive"],
            ["Content Filtering", "filter_content", "collapse_alternatives",
             "convert_html_to_plaintext", "description"], 
             #"default_member_moderation", "scheme"
            ["Digest", "digest_size_threshold"], #"next_digest_number", 
             #"last_post_at", "digest_last_sent_at", "digest_footer", 
             #"digest_header", "digest_is_default",
             #"digest_send_periodic", "digest_size_threshold",
             #"digest_volume_frequency", "digestable"],
             #["Moderation","discard_these_nonmembers", "emergency",
             #"generic_nonmember_action", "generic_nonmember_action",
             #"member_moderation_action", "member_moderation_notice",
             #"moderator_password", "hold_these_nonmembers"],
             #["Message Text", "msg_header", "msg_footer", "welcome_msg", 
             #"goodbye_msg"],
            ["Privacy", "advertised", "admin_immed_notify", 
             "admin_notify_mchanges", "anonymous_list"], #"archive_private", 
            #"obscure_addresses", "private_roster",
            #["Addresses", "bounces_address", "join_address", "leave_address", 
             #"no_reply_address", "owner_address", "posting_address", 
             #"request_address"],
            ["Assorted", "acceptable_aliases", "administrivia", "pipeline"]
             #"post_id", "encode_ascii_prefixes", "first_strip_reply_to",
             #"forward_auto_discards", "gateway_to_mail", "gateway_to_news",
             #"header_matches", "linked_newsgroup", "max_days_to_hold",
             #"max_message_size", "max_num_recipients",
             #"mime_is_default_digest", "new_member_options",
             #"news_moderation", "news_prefix_subject_too", "nntp_host",
             #"nondigestable", "nonmember_rejection_notice", "personalize",
             #"preferred_language",
             #"reject_these_nonmembers", "reply_goes_to_list",
             #"reply_to_address", "require_explicit_destination",
             #"respond_to_post_requests", "scrub_nondigest",
             #"send_goodbye_msg", "send_reminders", "send_welcome_msg",
             #"start_chain", "subject_prefix", "subscribe_auto_approval",
             #"subscribe_policy", "topics", "topics_bodylines_limit",
             #"topics_enabled", "unsubscribe_policy"]]
             ]

class Login(FieldsetForm):
    """Form fields to let the user log in.
    """
    user = forms.EmailField(
        label = _('Email address'),
        error_messages = {'required': _('Please enter an email address.'), 
                          'invalid': _('Please enter a valid email address.')},
        required = True,
    )
    password = forms.CharField(
        label = _('Password'),
        widget = forms.PasswordInput,
        error_messages = {'required': _('Please enter your password.'), 
                          'invalid': _('Please enter a valid password.')},
        required = True,
    )

    class Meta:
        """
        Class to define the name of the fieldsets and what should be
        included in each.
        """
        layout = [["Login", "user", "password"],]

class ListMassSubscription(FieldsetForm):
    """Form fields to masssubscribe users to a list.
    """
    emails = forms.CharField(
        label = _('Emails to mass subscribe'),
        widget = forms.Textarea,
    )

    class Meta:
        """
        Class to define the name of the fieldsets and what should be
        included in each.
        """
        layout = [["Mass subscription", "emails"],]

class MembershipSettings(FieldsetForm):
    """Form handling the membership settings.
    """
    choices = ((True, _('Yes')), (False, _('No')),)
    acknowledge_posts = forms.BooleanField(
        widget = forms.RadioSelect(choices = choices), 
        required = False,
        label = _('Acknowledge posts'),
    )
    hide_address = forms.BooleanField(
        widget = forms.RadioSelect(choices = choices), 
        required = False,
        label = _('Hide address'),
    )
    receive_list_copy = forms.BooleanField(
        widget = forms.RadioSelect(choices = choices), 
        required = False,
        label = _('Receive list copy'),
    )
    receive_own_postings = forms.BooleanField(
        widget = forms.RadioSelect(choices = choices), 
        required = False,
        label = _('Receive own postings'),
    )
    delivery_mode = forms.ChoiceField(
        widget = forms.Select(),
        error_messages = {
            'required': _("Please choose a mode."),
        },
        required = False,
        choices = (
            ("", _("Please choose")),
            ("delivery_mode", "some mode..."), # TODO: this must later
            # be dynalically changed to what modes the list offers
            # (see the address field in __init__ in UserSettings for
            # how to do this)
        ),
        label = _('Delivery mode'),
    )
    delivery_status = forms.ChoiceField(
        widget = forms.Select(),
        error_messages = {
            'required': _("Please choose a status."),
        },
        required = False,
        choices = (
            ("", _("Please choose")),
            ("delivery_status", "some status..."), # TODO: this must 
            # later be dynalically changed to what statuses the list 
            # offers (see the address field in __init__ in UserSettings
            # for how to do this)
        ),
        label = _('Delivery status'),
    )

    class Meta:
        """
        Class to define the name of the fieldsets and what should be
        included in each.
        """
        layout = [["Membership Settings", "acknowledge_posts", "hide_address", 
                   "receive_list_copy", "receive_own_postings", 
                   "delivery_mode", "delivery_status"],]

class UserSettings(FieldsetForm):
    """Form handling the user settings.
    """
    def __init__(self, address_choices, *args, **kwargs):
        """
        Initialize the user settings with a field 'address' where 
        the values are set dynamically in the view.
        """
        super(UserSettings, self).__init__(*args, **kwargs)
        self.fields['address'] = forms.ChoiceField(choices=(address_choices), 
                                                   widget = forms.Select(), 
                                                   error_messages = {'required': _("Please choose an address."),},
                                                   required = True,
                                                   label = _('Default email address'),)
    
    id = forms.IntegerField(    # this should probably not be 
                                # changeable...
        label = _('ID'),
        initial = 9,
        widget = forms.HiddenInput(),
        required = False,
        error_messages = {
            'invalid': _('Please provide an integer ID.')
        }
    )
    mailing_list = forms.CharField( # not sure this needs to be here
        label = _('Mailing list'),
        widget = forms.HiddenInput(),
        required = False,
    )
    real_name =forms.CharField(
        label = _('Real name'),
        required = False,
    )
    preferred_language = forms.ChoiceField(
        label = _('Default/Preferred language'),
        widget = forms.Select(),
        error_messages = {
            'required': _("Please choose a language."),
        },
        required = False,
        choices = (
            ("", _("Please choose")),
            ("English (USA)", "English (USA)"), # TODO: this must later
            # be dynalically changed to what languages the list offers
            # (see the address field in __init__ for how to do this)
        )
    )
    password = forms.CharField(
        label = _('Change password'),
        widget = forms.PasswordInput,
        required = False,
        error_messages = {'required': _('Please enter your password.'), 
                          'invalid': _('Please enter a valid password.')},
    )
    conf_password = forms.CharField(
        label = _('Confirm password'),
        widget = forms.PasswordInput,
        required = False,
        error_messages = {'required': _('Please enter your password.'), 
                          'invalid': _('Please enter a valid password.')},
    )

    class Meta:
        """
        Class to define the name of the fieldsets and what should be
        included in each.
        """
        layout = [["User settings", "real_name", "password", 
                   "conf_password", "preferred_language", "address"],]
