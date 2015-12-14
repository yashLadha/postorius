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
import json
import email
import sys

from email.Header import decode_header
from base64 import b64decode
from email.Parser import Parser as EmailParser
from email.utils import parseaddr
from StringIO import StringIO

from django.http import HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext as _

from postorius.auth.decorators import *


# based on https://www.ianlewis.org/en/parsing-email-attachments-python
def parse_attachment(message_part, counter):
    content_disposition = message_part.get("Content-Disposition", None)
    if content_disposition:
        dispositions = content_disposition.strip().split(";")
        if bool(content_disposition and dispositions[0].lower() == "attachment"):

            file_data = message_part.get_payload(decode=True)
            attachment = StringIO(file_data)
            attachment.content_type = message_part.get_content_type()
            attachment.size = len(file_data)
            attachment.name = message_part.get_filename()

            if not attachment.name:
		ext = mimetypes.guess_extension(part.get_content_type())
		if not ext:
		    ext = '.bin'
		attachment.name = 'part-%03d%s' % (counter, ext)

            return attachment
    return None

def parse(content):
    p = EmailParser()
    msgobj = p.parsestr(content)
    if msgobj['Subject'] is not None:
        decodefrag = decode_header(msgobj['Subject'])
        subj_fragments = []
        for s , enc in decodefrag:
            if enc:
                s = unicode(s , enc).encode('utf8','replace')
            subj_fragments.append(s)
        subject = ''.join(subj_fragments)
    else:
        subject = None

    attachments = []
    body = None
    html = None
    counter = 1
    for part in msgobj.walk():
        attachment = parse_attachment(part, counter)
        if attachment:
            attachments.append(attachment)
            counter += 1
        elif part.get_content_type() == "text/plain":
            if body is None:
                body = ""
            if part.get_content_charset():
                body += unicode(
                    part.get_payload(decode=True),
                    part.get_content_charset(),
                    'replace'
                ).encode('utf8','replace')
            else:
                body += part.get_payload(decode=True)
        elif part.get_content_type() == "text/html":
            if html is None:
                html = ""
            if part.get_content_charset():
                html += unicode(
                    part.get_payload(decode=True),
                    part.get_content_charset(),
                    'replace'
                ).encode('utf8','replace')
            else:
                html += part.get_payload(decode=True)
    return {
        'subject' : subject,
        'body' : body,
        'html' : html,
        'from' : parseaddr(msgobj.get('From'))[1],
        'to' : parseaddr(msgobj.get('To'))[1],
        #'attachments': attachments,
    }


@login_required
@list_moderator_required
def get_held_message(request, list_id, held_id=-1):
    """Return a held message as a json object
    """
    if held_id == -1:
        raise Http404(_('Message does not exist'))

    held_message = List.objects.get_or_404(fqdn_listname=list_id).get_held_message(held_id)

    response_data = dict()
    response_data['sender'] = held_message.sender
    try:
        response_data['reasons'] = held_message.reasons
    except AttributeError:
        pass
    response_data['moderation_reasons'] = held_message.moderation_reasons
    response_data['hold_date'] = held_message.hold_date
    response_data['msg'] = held_message.msg
    response_data['stripped_msg'] = parse(held_message.msg)
    response_data['msgid'] = held_message.request_id
    response_data['subject'] = held_message.subject

    return HttpResponse(json.dumps(response_data), content_type="application/json")
