# -*- coding: utf-8 -*-
from django import forms
from django.utils.translation import gettext as _
from fieldset_forms import FieldsetForm

class ListNew(FieldsetForm):
    """Form fields to add a new list. Languages are hard coded which should 
    be replaced by a REST lookup of available languages.
    """
    listname = forms.EmailField(
        label = _('List Name'), 
        initial = '@mailman.state-of-mind.de',
        error_messages = {
            'required': _('Please enter a name for your list.'), 
            'invalid': _('Please enter a valid list name.')
        }
    )
    list_owner = forms.EmailField(
        label = _('Inital list owner address'),
        error_messages = {
            'required': _("Please enter the list owner's email address."), 
            'invalid': _('Please enter a valid email adress.')
        },
        required = True,
    )
    list_type = forms.ChoiceField(
        widget = forms.Select(),
        label = _('List Type'), 
        error_messages = {
            'required': _("Please choose a list type."), 
        },
        required = True,
        choices = (
            ("", _("Please choose")),
            ("closed_discussion", _("Closed discussion list")),
            ("announcement", _("Announcement list")),
        )
    )
    languages = forms.MultipleChoiceField(
        label = _('Language'),
        widget = forms.CheckboxSelectMultiple(),
        choices = (
            ("Arabic", "Arabic"),
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
            ("Vietnamese", "Vietnamese")
        ),
        required = False
    )
    class Meta:
        """Class to handle the automatic insertion of fieldsets and divs.
        
        To use it: add a list for each wished fieldset. The first item in 
        the list should be the wished name of the fieldset, the following 
        the fields that should be included in the fieldset.
        """
        layout = [["List Details", "listname", "list_owner", "list_type"],
                  ["Available Languages", "languages"],]

class ListSubscribe(forms.Form):
    """Form fields to join an existing list
    """
    listname = forms.EmailField(
        label = _('List Name'), 
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
    real_name = forms.CharField(
        label = _('Your name'), 
        required = False,
    )
    name = forms.CharField(
        label = _('Name of action'), 
        widget = forms.HiddenInput(),
        #initial = 'subscribe',
    )
    
    # should add password!

class ListUnsubscribe(forms.Form):
    """Form fields to leave an existing list
    """
    listname = forms.EmailField(
        label = _('List Name'), 
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
    label = _('Name of action'), 
    widget = forms.HiddenInput(),
    #initial = 'unsubscribe'
    )

    # should at one point add the password to be required as well!
