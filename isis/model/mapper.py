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

from .ordered import OrderedProperty, OrderedModel
from .subfield import CompositeString


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
            raise Invalid('%r value must be unicode or str instance' % self.name)
        value = unicode(value)
        if self.required and len(value.rstrip()) == 0:
            raise Invalid('%r value cannot be empty' % self.name)
        super(TextProperty, self).__set__(instance, value)


class MultiTextProperty(CheckedProperty):
    
    def __set__(self, instance, value):
        if not isinstance(value, tuple):
            raise TypeError('MultiText value must be tuple')
        super(MultiTextProperty, self).__set__(instance, value)


class CompositeTextProperty(CheckedProperty):
    
    def __init__(self, subkeys=None, **kwargs):
        super(CompositeTextProperty, self).__init__(**kwargs)
        self.subkeys = subkeys
    
    def __set__(self, instance, value):
        if not isinstance(value, basestring):
            raise Invalid('%r value must be unicode or str instance' % self.name)
                
        composite_text = CompositeString(value, self.subkeys)
        super(CompositeTextProperty, self).__set__(instance, composite_text)
    
    
class MultiCompositeTextProperty(CheckedProperty):
    
    def __init__(self, subkeys=None, **kwargs):
        super(MultiCompositeTextProperty, self).__init__(**kwargs)
        self.subkeys = subkeys
    
    def __set__(self, instance, value):
        if not isinstance(value, tuple):
            raise TypeError('MultiCompositeText value must be tuple')
        
        composite_texts = []
        for raw_composite_text in value:
            composite_texts.append(CompositeString(raw_composite_text, self.subkeys))
            
        super(MultiCompositeTextProperty, self).__set__(instance, tuple(composite_texts))


class ReferenceProperty(CheckedProperty):
    
    def __init__(self, ref_type, **kwargs):
        super(ReferenceProperty, self).__init__(**kwargs)
        self.__ref_type = ref_type        
        
    def __set__(self, instance, value):
        if not isinstance(value, self.__ref_type):
            raise TypeError('Reference value must be %s' % self.__ref_type)
        
        super(ReferenceProperty, self).__set__(instance, value)
    
    
if __name__ == '__main__':
    import doctest
    doctest.testmod()
    