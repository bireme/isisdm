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
        
        >>> author = CompositeString('John Tenniel^xillustrator',
        ...                          subkeys='x')
        >>> unicode(author)
        u'John Tenniel^xillustrator'
        
    '''
    
    def __init__(self, isis_raw, subkeys=None, encoding=DEFAULT_ENCODING):
        if not isinstance(isis_raw, basestring):
            raise Invalid('%r value must be unicode or str instance' % isis_raw)
            
        self.__isis_raw = isis_raw.decode(encoding)
        self.__expanded = expand(self.__isis_raw, subkeys)

    def __getitem__(self, key):
        for subfield in self.__expanded:
            if subfield[0] == key:
                return subfield[1]
        else:
            raise KeyError(key)
            
    def __unicode__(self):
        return self.__isis_raw
    
    def __str__(self):
        return str(self.__isis_raw)


def test():
    import doctest
    doctest.testmod()

if __name__=='__main__':
    test()

