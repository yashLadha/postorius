# -*- coding: utf-8 -*-
from django.forms import Form
from django.utils import safestring
from django.forms.forms import BoundField

class FieldsetError(Exception):
    pass

class FieldsetForm(Form):
    """
    Extends a standard form and adds fieldsets and the possibililty
    to use as_div for the automatic rendering of form fields. Inspired
    by WTForm.
    """

    def __init__(self, *args):
        """Initialize a FormsetField."""
        super(FieldsetForm, self).__init__(*args)
        # check if the user specified the wished layout of the form
        if hasattr(self, 'Meta') and hasattr(self.Meta, 'layout'):
            msg = "Meta.layout must be iterable"
            assert hasattr(self.Meta.layout, '__getitem__'), msg
            self.layout = self.Meta.layout
        else:
            self.layout = self.fields.keys()

    def as_div(self):
        """Render the form as a set of <div>s."""
        output = ""
        # first, create the fieldsets
        for index in range(len(self.layout)):
            output += self.create_fieldset(self.layout[index])
        return safestring.mark_safe(output)

    def create_fieldset(self, field):
        """
        Create a <fieldset> around a number of field instances.
        field[0] is the name of the fieldset and field[1:] the fields
        it should include.
        """
        # Create the divs in each fieldset by calling create_divs.
        return u'<fieldset><legend>%s</legend>%s</fieldset>' % (field[0], 
                                                                self.create_divs(field[1:]))
    
    def create_divs(self, fields):
        """Create a <div> for each field."""
        output = ""
        for field in fields:
            try:
                # create a field instance for the bound field
                field_instance = self.base_fields[field]
            except KeyError:
                # could not create the instance so throw an exception
                # msg on a separate line since the line got too long 
                # otherwise
                msg = "Could not resolve form field '%s'." % field
                raise FieldsetError(msg)
            # create a bound field containing all the necessary fields 
            # from the form
            bound_field = BoundField(self, field_instance, field)
            output += '<div class="field %(class)s">%(label)s%(help_text)s%(errors)s%(field)s</div>\n' % \
                     {'class': bound_field.name, 
                      'label': bound_field.label, 
                      'help_text': bound_field.help_text, 
                      'errors': bound_field.errors, 
                      'field': unicode(bound_field)}
        return output
