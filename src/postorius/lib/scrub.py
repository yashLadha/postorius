# Copyright (C) 2011-2012 by the Free Software Foundation, Inc.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301,
# USA.

"""Cleanse a message for archiving."""

from __future__ import absolute_import, unicode_literals

import os
import re
import binascii
from mimetypes import guess_all_extensions
from email.header import decode_header, make_header
from email.errors import HeaderParseError

pre = re.compile(r'[/\\:]')
sre = re.compile(r'[^-\w.]')
dre = re.compile(r'^\.*')

BR = '<br>\n'

NEXT_PART = re.compile(r'--------------[ ]next[ ]part[ ]--------------\n')


def guess_extension(ctype, ext):
    all_exts = guess_all_extensions(ctype, strict=False)
    if ext in all_exts:
        return ext
    return all_exts and all_exts[0]


def get_charset(message, default="ascii", guess=False):
    if message.get_content_charset():
        return message.get_content_charset().decode("ascii")
    if message.get_charset():
        return message.get_charset().decode("ascii")
    charset = default
    if not guess:
        return charset
    text = message.get_payload(decode=True)
    for encoding in ["ascii", "utf-8", "iso-8859-15"]:
        try:
            text.decode(encoding)
        except UnicodeDecodeError:
            continue
        else:
            charset = encoding
            break
    return charset


def oneline(s):
    """Inspired by mailman.utilities.string.oneline"""
    try:
        h = make_header(decode_header(s))
        ustr = h.__unicode__()
        return ''.join(ustr.splitlines())
    except (LookupError, UnicodeError, ValueError, HeaderParseError):
        return ''.join(s.splitlines())


class Scrubber(object):
    def __init__(self, msg):
        self.msg = msg

    def scrub(self):
        attachments = []
        for part_num, part in enumerate(self.msg.walk()):
            ctype = part.get_content_type()
            if not isinstance(ctype, unicode):
                ctype = ctype.decode("ascii")
            if ctype == 'text/plain':
                disposition = part.get('content-disposition')
                if disposition and disposition.decode(
                        "ascii", "replace").strip().startswith("attachment"):
                    attachments.append(self.parse_attachment(part, part_num))
                    part.set_payload('')
            elif ctype == 'text/html':
                attachments.append(self.parse_attachment(part, part_num,
                                                         filter_html=False))
                part.set_payload('')
            elif ctype == 'message/rfc822':
                attachments.append(self.parse_attachment(part, part_num))
                part.set_payload('')
            elif part.get_payload() and not part.is_multipart():
                payload = part.get_payload(decode=True)
                ctype = part.get_content_type()
                if not isinstance(ctype, unicode):
                    ctype.decode("ascii")
                if payload is None:
                    continue
                attachments.append(self.parse_attachment(part, part_num))
        if self.msg.is_multipart():
            text = []
            for part in self.msg.walk():
                if not part.get_payload() or part.is_multipart():
                    continue
                partctype = part.get_content_type()
                if partctype != 'text/plain' and partctype != 'text/html':
                    continue
                try:
                    t = part.get_payload(decode=True) or ''
                except (binascii.Error, TypeError):
                    t = part.get_payload() or ''
                partcharset = get_charset(part, guess=True)
                try:
                    t = t.decode(partcharset, 'replace')
                except (UnicodeError, LookupError, ValueError,
                        AssertionError):
                    t = t.decode('ascii', 'replace')
                if isinstance(t, basestring):
                    if not t.endswith('\n'):
                        t += '\n'
                    text.append(t)

            text = u"\n".join(text)
        else:
            text = self.msg.get_payload(decode=True)
            charset = get_charset(self.msg, guess=True)
            try:
                text = text.decode(charset, "replace")
            except (UnicodeError, LookupError, ValueError, AssertionError):
                text = text.decode('ascii', 'replace')

            next_part_match = NEXT_PART.search(text)
            if next_part_match:
                text = text[0:next_part_match.start(0)]

        return (text, attachments)

    def parse_attachment(self, part, counter, filter_html=True):
        decodedpayload = part.get_payload(decode=True)
        ctype = part.get_content_type()
        if not isinstance(ctype, unicode):
            ctype = ctype.decode("ascii")
        charset = get_charset(part, default=None, guess=False)
        try:
            filename = oneline(part.get_filename(''))
        except (TypeError, UnicodeDecodeError):
            filename = u"attachment.bin"
        filename, fnext = os.path.splitext(filename)
        ext = fnext or guess_extension(ctype, fnext)
        if not ext:
            if ctype == 'message/rfc822':
                ext = '.txt'
            else:
                ext = '.bin'
        ext = sre.sub('', ext)
        if not filename:
            filebase = u'attachment'
        else:
            parts = pre.split(filename)
            filename = parts[-1]
            filename = dre.sub('', filename)
            filename = sre.sub('', filename)
            filebase = filename
        if ctype == 'message/rfc822':
            submsg = part.get_payload()
            decodedpayload = str(submsg)
        return (counter, filebase + ext, ctype, charset, decodedpayload)
