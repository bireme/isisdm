#!/usr/bin/env python
# -*- encoding: utf-8 -*-

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


---------------------
CompositeString tests
---------------------
    >>> author = CompositeString('John Tenniel^rillustrator',
    ...                          subkeys='r')
    
    >>> unicode(author)
    u'John Tenniel^rillustrator'
    
    >>> str(author)
    'John Tenniel^rillustrator'
    
Iteration semantics are similar to dicts::

    >>> for k in author: print k
    _
    r
    
    >>> for k, v in author.items(): print k, v
    _ John Tenniel
    r illustrator
"""

from isis.model.subfield import expand, CompositeString
import json

def test():
    import doctest
    doctest.testmod()

if __name__=='__main__':
    test()