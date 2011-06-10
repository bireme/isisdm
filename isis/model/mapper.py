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
from .subfield import CompositeString, CompositeField
import json
import colander
import deform
import hashlib

class Document(OrderedModel):

    def __init__(self, **kwargs):
        super(Document, self).__init__(**kwargs)
        self.validate()

    def validate(self):
        for prop in self:
            descriptor = self.__class__.__getattribute__(self.__class__, prop)
            descriptor.validate(self, getattr(self, prop, None))

    @classmethod
    def get_schema(cls):
        schema = colander.SchemaNode(colander.Mapping())
        exclude_fields = ()

        if hasattr(cls, 'Meta'):
            if hasattr(cls.Meta, 'hide'):
                if not isinstance(cls.Meta.hide, tuple):
                    raise TypeError('hide value must be tuple')
                exclude_fields = cls.Meta.hide

        for prop in cls:
            if prop in exclude_fields:
                continue
            descriptor = cls.__getattribute__(cls, prop)
            colander_definition = descriptor._colander_schema(cls, getattr(cls, prop, None))
            schema.add(colander_definition)

        return schema

    def to_python(self):
        '''
        generate a python representation for Document type classes
        '''
        properties = {}
        for prop in self:
            descriptor = self.__class__.__getattribute__(self.__class__, prop)
            try:
                properties[prop] = descriptor._pystruct(self, getattr(self, prop))
            except AttributeError:
                pass
        if not 'TYPE' in properties:
            properties['TYPE'] = self.TYPE

        return properties

    @classmethod
    def from_python(cls, pystruct):
        if 'TYPE' in pystruct and cls.__name__ != pystruct.pop('TYPE'):
            raise TypeError()

        isisdm_pystruct = dict((str(k), tuple(v) if isinstance(v, list) else v)
            for k, v in pystruct.items() if v is not None)

        return cls(**isisdm_pystruct)

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
        self.choices = choices if choices else ()

    def __set__(self, instance, value):
        if self.validator:
            self.validator(self, value)
        super(CheckedProperty, self).__set__(instance, value)

    def validate(self, instance, value):
        if self.missing(instance):
            raise TypeError('required %r property missing' % self.name)
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
            raise TypeError('%r value must be unicode or str instance' % self.name)
        value = unicode(value)
        if self.required and len(value.rstrip()) == 0:
            raise Invalid('%r value cannot be empty' % self.name)
        super(TextProperty, self).__set__(instance, value)

    def _pystruct(self, instance, value):
        '''
        python representation for this property
        '''
        return value

    def _colander_schema(self, instance, value):
        kwargs = {'name':self.name}
        if not self.required:
            kwargs.update({'missing':None})
        if self.choices:
            choices_keys = [item[0] for item in self.choices]
            kwargs.update({'widget':deform.widget.SelectWidget(values=self.choices),
                           'validator':colander.OneOf(choices_keys)})
        
        return colander.SchemaNode(colander.String(), **kwargs)

class BooleanProperty(CheckedProperty):

    def __set__(self, instance, value):
        if not isinstance(value, bool):
            raise TypeError('%r must be bool' % self.name)
        super(BooleanProperty, self).__set__(instance, value)

    def _pystruct(self, instance, value):
        '''
        python representation for this property
        '''
        return value

    def _colander_schema(self, instance, value):
        kwargs = {'name':self.name}
        if not self.required:
            kwargs.update({'missing':None})

        return colander.SchemaNode(colander.Boolean(), **kwargs)

class FileProperty(CheckedProperty):

    def __set__(self, instance, value):
        if not isinstance(value, dict):
            raise TypeError('%r must be a dictionary' % self.name)
       
        if 'filename' not in value:
            try:
                value['filename'] = value['fp'].name
            except AttributeError:
                raise TypeError('%r must be a file' % self.name)
        
        super(FileProperty, self).__set__(instance, value)

    def _pystruct(self, instance, value):
        '''
        python representation for this property
        '''        
        if isinstance(value, dict):
            serializable_value = {'uid':value['uid'],
                                  'filename':value['filename'],}
            return serializable_value

        return value

    def _colander_schema(self, instance, value):
        class MemoryTmpStore(dict):

            def __getitem__(self, name):                
                return self.get(name)
            
            def get(self, name):
                item = super(MemoryTmpStore,self).get(name)
                
                if item is not None and item['fp'] is not None:
                    if not item['fp'].read(100):
                        item['fp'] = None
                    else:
                        item['fp'].seek(0)

                return item

            def preview_url(self, name):
                return None
        tmpstore = MemoryTmpStore()

        kwargs = {'widget':deform.widget.FileUploadWidget(tmpstore),
                  'name':self.name}
        if not self.required:
            kwargs.update({'missing':None})

        return colander.SchemaNode(deform.FileData(), **kwargs)

class MultiTextProperty(CheckedProperty):

    def __set__(self, instance, value):
        if not isinstance(value, tuple):
            raise TypeError('MultiText value must be tuple')
        super(MultiTextProperty, self).__set__(instance, value)

    def _pystruct(self, instance, value):
        '''
        python representation for this property
        '''
        return value

    def _colander_schema(self, instance, value):
        kwargs = {'name':self.name}
        if not self.required:
            kwargs.update({'missing':None})

        schema = colander.SchemaNode(colander.Sequence(), **kwargs)
        schema.add(colander.SchemaNode(colander.String(), name=self.name))

        return schema


class IsisCompositeTextProperty(CheckedProperty):

    def __init__(self, subkeys=None, **kwargs):
        super(IsisCompositeTextProperty, self).__init__(**kwargs)
        self.subkeys = subkeys

    def __set__(self, instance, value):
        if not isinstance(value, basestring):
            raise TypeError('%r value must be unicode or str instance' % self.name)

        composite_text = CompositeString(value, self.subkeys)
        super(IsisCompositeTextProperty, self).__set__(instance, composite_text)

    def _pystruct(self, instance, value):
        '''
        python representation for this property
        '''
        return value.items()

    def _colander_schema(self, instance, value):
        subfield = colander.SchemaNode(colander.Tuple())
        subfield.add(colander.SchemaNode(colander.String(), name='subkey'))
        subfield.add(colander.SchemaNode(colander.String(), name='value'))

        return colander.SchemaNode(colander.Sequence(),
                                   subfield,
                                   name=self.name)

class CompositeTextProperty(CheckedProperty):

    def __init__(self, subkeys, **kwargs):
        super(CompositeTextProperty, self).__init__(**kwargs)
        if not isinstance(subkeys,tuple) and not isinstance(subkeys, list):
            raise TypeError('subkeys argument must be tuple or list')
        self.subkeys = subkeys

    def __set__(self, instance, value):
        try:
            value_as_dict = dict(value)
        except ValueError:
            raise TypeError('%r value must be a key-value structure' % self.name)

        try:
            value = CompositeField(value_as_dict, self.subkeys)
        except TypeError:
            raise TypeError('%r got an unexpected keyword' % self.name)

        super(CompositeTextProperty, self).__set__(instance, value)

    def _pystruct(self, instance, value):
        '''
        python representation for this property
        '''
        return value.items()

    def _colander_schema(self, instance, value):
        #option arg acts in each attribute
        kwargs = {}
        if not self.required:
            kwargs.update({'missing':None})

        subfield = colander.SchemaNode(colander.Mapping(), name=self.name)
        for subkey in self.subkeys:
            subfield.add(colander.SchemaNode(colander.String(), name=subkey, **kwargs))

        return subfield

class MultiIsisCompositeTextProperty(CheckedProperty):

    def __init__(self, subkeys=None, **kwargs):
        super(MultiIsisCompositeTextProperty, self).__init__(**kwargs)
        self.subkeys = subkeys

    def __set__(self, instance, value):
        if not isinstance(value, tuple):
            raise TypeError('MultiIsisCompositeText value must be tuple')

        composite_texts = tuple(CompositeString(raw_composite_text, self.subkeys) for raw_composite_text in value)
        super(MultiIsisCompositeTextProperty, self).__set__(instance, composite_texts)

    def _pystruct(self, instance, value):
        '''
        python representation for this property
        '''
        return tuple(composite_text.items() for composite_text in value)

    def _colander_schema(self, instance, value):
        schema = colander.SchemaNode(colander.Tuple())
        for subkey in self.subkeys:
            schema.add(colander.SchemaNode(colander.String(), name=subkey))

        return colander.SchemaNode(colander.Sequence(),
                                   schema,
                                   name=self.name)

class MultiCompositeTextProperty(CheckedProperty):

    def __init__(self, subkeys, **kwargs):
        super(MultiCompositeTextProperty, self).__init__(**kwargs)
        if not isinstance(subkeys,tuple) and not isinstance(subkeys, list):
            raise TypeError('subkeys argument must be tuple or list')
        self.subkeys = subkeys

    def __set__(self, instance, value):
        if not isinstance(value, tuple) and not isinstance(value, list):
            raise TypeError('%r value must be tuple or list')
        
        try:
            composite_texts = tuple(CompositeField(dict(composite_text), self.subkeys) for composite_text in value)            
        except ValueError:
            raise TypeError('%r value must be a list or tuple of key-value structures' % self.name)

        super(MultiCompositeTextProperty, self).__set__(instance, composite_texts)

    def _pystruct(self, instance, value):
        '''
        python representation for this property
        '''
        return tuple(composite_text.items() for composite_text in value)

    def _colander_schema(self, instance, value):
        schema = colander.SchemaNode(colander.Mapping(), name=self.name)
        
        kwargs = {}
        if not self.required:
            kwargs.update({'missing':None})
        
        for subkey in self.subkeys:
            schema.add(colander.SchemaNode(colander.String(), name=subkey, **kwargs))

        return colander.SchemaNode(colander.Sequence(),
                                   schema,
                                   name=self.name,
                                   **kwargs)

class ReferenceProperty(CheckedProperty):

    def __set__(self, instance, value):
        if not isinstance(value, basestring):
            raise TypeError('Reference value must be unicode or str instance')
        value = unicode(value)
        if self.required and len(value.rstrip()) == 0:
            raise Invalid('%r value cannot be empty' % self.name)
        super(ReferenceProperty, self).__set__(instance, value)

    def _pystruct(self, instance, value):
        '''
        python representation for this property
        '''
        return value

    def _colander_schema(self, instance, value):
        return [colander.String()]

if __name__ == '__main__':
    import doctest
    doctest.testmod()
