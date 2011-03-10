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

from operator import attrgetter
        
class OrderedProperty(object):
    __count = 0
    
    def __init__(self):
        self.order = OrderedProperty.__count
        OrderedProperty.__count += 1
        
    def __get__(self, instance, cls):
        try:
            return instance._props[self.name]
        except KeyError:
            raise AttributeError("'%s' object has no attribute '%s'" % (instance.__class__.__name__, self.name))
        
    def __set__(self, instance, value):
        instance._props[self.name] = value
        
    def __repr__(self):
        return '<%s %s>' % (self.__class__.__name__, self.name)

class OrderedMeta(type):
    def __new__(cls, name, bases, dict):        
        props = []
        for key, attr in dict.items():
            if isinstance(attr, OrderedProperty):
                attr.name = key
                props.append(attr)
        dict['_ordered_prop_keys'] = sorted(props, key=attrgetter('order'))
        return type.__new__(cls, name, bases, dict)
        
    def __iter__(self):
        return iter(self._ordered_prop_keys)

    def __contains__(self, key):
        return key in self._ordered_prop_keys

class OrderedModel(object):
    __metaclass__ = OrderedMeta

    def __init__(self, **kwargs):
        self._props = {}
        for k in kwargs:
            setattr(self, k, kwargs[k])
    
    def __iter__(self):
        return (prop.name for prop in self.__class__)
        
    def __contains__(self, key):
        return key in self.__class__

    def iteritems(self):
        return ((prop.name, getattr(self, prop.name)) 
                for prop in self.__class__)


if __name__=='__main__':
    import doctest
    doctest.testmod()
    
    
