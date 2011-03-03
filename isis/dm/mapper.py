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
----------------------
Object-document mapper
----------------------
    >>> def text_validator(node, value):
    ...     if value.startswith('Banana'):
    ...         raise BaseException, "You can't start a text with 'Banana'"
    ...
    
    >>> def colon_validator(node, value):
    ...     import re
    ...     for author in value:
    ...         if re.search('(, )', author) is None:
    ...             raise BaseException, "Authors's name must be in 'LastName, FirstName' format"
    
    >>> class Book(Document):
    ...     title = TextProperty(required=True, validator=text_validator)
    ...     authors = MultiTextProperty(required=False, validator=colon_validator)
    ...     pages = TextProperty()
    ...     

Instantiating a Book object::

    >>> book1 = Book(title='Godel, Escher, Bach',
    ...               authors=[u'Hofstadter, Douglas'],    
    ...               pages='777')
    ...
    >>> book2 = Book(title='Semantic Web') 
    >>> book2.authors = [u'Breitman, Karin K.', u'Casanova, Marco Antonio', u'Truzkowski, Walter']
            
Manipulating its attributes::

    >>> book1.title        
    u'Godel, Escher, Bach'
    
    >>> book1.authors[0]
    u'Hofstadter, Douglas'
    
    >>> book1.authors = [u'Hofstadter Douglas'] #DOCTEST: +ELLIPSIS
    Traceback (most recent call last):
    ...
    BaseException: Authors's name must be in 'LastName, FirstName' format
    
    >>> book1.authors[0]
    u'Hofstadter, Douglas'
    
FIXME: validators don't work correctly when appending data
    >>> book1.authors.append(u'Daiana Rose')    
    >>> book1.authors
    [u'Hofstadter, Douglas', u'Daiana Rose']
    
"""
from ordered import OrderedProperty, OrderedModel

__all__ = ['Document', 'TextProperty', 'MultiTextProperty']


class Document(OrderedModel):

    def __init__(self, **kwargs):
        super(Document, self).__init__(**kwargs)
        self.validate()
                
    def isplural(self, name):
        return isinstance(self.__class__.__getattribute__(self.__class__, name), PluralProperty)

    def iteritemsplural(self):
        return ((prop.name, getattr(self, prop.name), self.isplural(prop.name))
                for prop in self.__class__)

    def validate(self):
        for prop in self:
            descriptor = self.__class__.__getattribute__(self.__class__, prop)
            descriptor.validate(self, getattr(self, prop, None))


class Invalid(Exception):
    ''' TODO: study colander.Invalid exception '''
    def __init__(self, message):
        super(Exception, self).__init__(message)

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self.message)

        
class CheckedProperty(OrderedProperty):

    def __init__(self, required=False, validator=None, choices=None):
        super(CheckedProperty, self).__init__()
        self.required = required
        self.validator = validator
        self.choices = choices if choices else []        

    def __set__(self, instance, value):
        if self.validator:
            self.validator(self, value)
        super(CheckedProperty, self).__set__(instance, value)

    def validate(self, instance, value):
        if self.missing(instance):
            raise Invalid('required %r property missing' % self.name)
        if value is not None and self.validator:
            self.validator(self, value)
                
    def missing(self, instance): 
        # a property is missing if it is required and 
        # does not exist or is set to None
        # if it is not required, it is never missing
        return self.required and getattr(instance, self.name, None) is None

        
class TextProperty(CheckedProperty):
    
    def __set__(self, instance, value):
        if not isinstance(value, basestring):
            raise Invalid('%r value must be unicode type instance' % self.name)
        value = unicode(value)
        if self.required and len(value.rstrip()) == 0:
            raise Invalid('%r value cannot be empty' % self.name)
        super(TextProperty, self).__set__(instance, value)


class MultiTextProperty(CheckedProperty):
    
    def __set__(self, instance, value):
        if not isinstance(value, (list, tuple, set)):
            raise TypeError('MultiText value must be list, tuple or set')        
        super(MultiTextProperty, self).__set__(instance, value)


if __name__ == '__main__':    
    import doctest
    doctest.testmod()
    