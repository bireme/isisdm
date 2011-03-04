#!/usr/bin/env python
# -*- encoding: utf-8 -*-

# ISIS-DM: the ISIS Data Model API
#
# Copyright (C) 2010 BIREME/PAHO/WHO
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation, either version 2.1 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.


"""
-----------------
Subfield parsing
-----------------

    >>> expand('John Tenniel^rillustrator')
    [('_', 'John Tenniel'), ('r', 'illustrator')]

All subfields are stripped of trailing whitespace::

    >>> expand('John Tenniel ^rillustrator ')
    [('_', 'John Tenniel'), ('r', 'illustrator')]

Subfield keys are case-insensitive, and always converted to lower case::

    >>> expand('John Tenniel^Rillustrator')
    [('_', 'John Tenniel'), ('r', 'illustrator')]


Even if there is no main subfield, the '_' key is returned::

    >>> expand('^1one^2two^3three')
    [('_', ''), ('1', 'one'), ('2', 'two'), ('3', 'three')]

---------------
Abnormal cases
---------------

Empty field::

    >>> expand('')
    [('_', '')]

Empty subfields::

    >>> expand('aa^1^2c') # empty subfield ^1, middle position
    [('_', 'aa'), ('1', ''), ('2', 'c')]
    >>> expand('aa^1b^2') # empty subfield ^2, last position
    [('_', 'aa'), ('1', 'b'), ('2', '')]

Subfield keys are limited to a-z and 0-9. Invalid keys are ignored,
and the subfield delimiter is appended to the previous subfield::

    >>> expand('John Tenniel^!illustrator')
    [('_', 'John Tenniel^!illustrator')]
    >>> expand('John Tenniel^rillustrator^')
    [('_', 'John Tenniel'), ('r', 'illustrator^')]
    >>> expand('John Tenniel^rillustrator^^')
    [('_', 'John Tenniel'), ('r', 'illustrator^^')]

To reduce the damage from duplicate delimiters in the middle of the
field, a space is added after each pair. Otherwise the example below
would seem to have an ^i subfield with the content "llustrator".
Keeping the duplicate delimiters together makes it easier to find
and fix these problems later::

    >>> expand('John Tenniel^^illustrator')
    [('_', 'John Tenniel^^ illustrator')]

----------------------------
Controlled subfield parsing
----------------------------

When a subkeys parameter is passed, only subfield markers with those keys
are expanded::

    >>> expand('John Tenniel^rillustrator', subkeys='r')
    [('_', 'John Tenniel'), ('r', 'illustrator')]
    >>> expand('John Tenniel^xillustrator', subkeys='r')
    [('_', 'John Tenniel^xillustrator')]
    >>> expand('John Tenniel^rillustrator', subkeys='')
    [('_', 'John Tenniel^rillustrator')]


"""

import re

MAIN_SUBFIELD_KEY = '_'
SUBFIELD_MARKER_RE = re.compile(r'\^([a-z0-9])', re.IGNORECASE)
DEFAULT_ENCODING = u'utf-8'

def expand(content, subkeys=None):
    ''' Parse a field into an association list of keys and subfields

        >>> expand('zero^1one^2two^3three')
        [('_', 'zero'), ('1', 'one'), ('2', 'two'), ('3', 'three')]

    '''
    if subkeys is None:
        regex = SUBFIELD_MARKER_RE
    elif subkeys == '':
        return [(MAIN_SUBFIELD_KEY, content)]
    else:
        regex = re.compile(r'\^(['+subkeys+'])', re.IGNORECASE)
    content = content.replace('^^', '^^ ')
    parts = []
    start = 0
    key = MAIN_SUBFIELD_KEY
    while True:
        found = regex.search(content, start)
        if found is None: break
        parts.append((key, content[start:found.start()].rstrip()))
        key = found.group(1).lower()
        start = found.end()
    parts.append((key, content[start:].rstrip()))
    return parts


class CompositeString(object):
    ''' Represent an Isis field, with subfields, using
        Python native datastructures
        
        >>> pythonic_author = CompositeString('John Tenniel^xillustrator',
        ...                                   subkeys='x')
        >>> print pythonic_author
        [('_', u'John Tenniel'), (u'x', u'illustrator')]
        
    '''
    
    def __init__(self, isis_string, subkeys=None, encoding=DEFAULT_ENCODING):
        if not isinstance(isis_string, basestring):
            raise Invalid('%r value must be unicode or str instance' % isis_string)
            
        isis_string = isis_string.decode(encoding)
        self.expanded = expand(isis_string, subkeys)

    def __getitem__(self, key):
        for subfield in self.expanded:
            if subfield[0] == key:
                return subfield[1]
        else:
            raise KeyError(key)
            
    def __unicode__(self):
        return unicode(self.expanded)
    
    def __str__(self):
        return str(self.expanded)


def test():
    import doctest
    doctest.testmod()

if __name__=='__main__':
    test()


