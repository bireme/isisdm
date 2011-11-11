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

from ..utils import base28
from .mapper import Document, TextProperty, FileProperty
import uuid
import couchdbkit
import time
import colander
import deform

def _attach_exists(old_doc, property_name):
    if property_name in old_doc:
        try:
            if old_doc[property_name]['filename'] in old_doc['_attachments']:
                return True
        except (AttributeError, TypeError, KeyError):
            pass

    return False

def _attach_updated(new_doc, property_name):
    try:
        return new_doc[property_name]['fp'] is not None
    except KeyError:
        return False


class CouchdbDocument(Document):

    def __init__(self, **kwargs):
        super(CouchdbDocument, self).__init__(**kwargs)
        if '_id' not in kwargs:
            self._id = base28.genbase(5)

    def __clean_before_save(self, doc):
        '''
        removes attributes with None values
        '''
        doc = dict((str(k), v) for k, v in doc.items() if v is not None)

        return doc

    def to_python(self):
        pstruct = super(CouchdbDocument, self).to_python()
        try:
            pstruct['_id'] = self._id
        except AttributeError:
            pass

        try:
            pstruct['_rev'] = self._rev
        except AttributeError:
            pass

        return pstruct

    @classmethod
    def from_python(cls, pystruct):
        if pystruct.get('_id',None) == 'None':
            pystruct['_id'] = None

        if pystruct.get('_rev',None) == 'None':
            pystruct['_rev'] = None

        return super(CouchdbDocument, cls).from_python(pystruct)

    def save(self, db):
        new_doc = self.to_python()
        new_doc = self.__clean_before_save(new_doc)

        old_doc = db.get(new_doc['_id']) if '_rev' in new_doc else None

        while True:
            try:
                if old_doc is not None and '_attachments' in old_doc:
                    new_doc['_attachments'] = old_doc['_attachments']

                db.save_doc(new_doc)
                break
            except couchdbkit.ResourceConflict:
                time.sleep(0.5)
                new_doc['_id'] = base28.genbase(5)

        for key in self.__class__:
            prop = self.__class__.__getattribute__(self.__class__,key)
            if isinstance(prop, FileProperty):

                if old_doc is None:
                    #New document
                    file_metadata = getattr(self,key, None)
                    if file_metadata:
                        db.put_attachment(new_doc, file_metadata['fp'], getattr(self, key)['filename'])
                elif _attach_exists(old_doc, key) and not hasattr(self,key):
                    #Attachment exists and had not been changed
                    new_doc[key] = old_doc[key]
                    db.save_doc(new_doc)
                else:
                    #Attachment updated
                    file_metadata = getattr(self,key, None)
                    if file_metadata and file_metadata.get('fp'):
                        db.put_attachment(new_doc, file_metadata['fp'], getattr(self, key)['filename'])

        self._id, self._rev = new_doc['_id'], new_doc['_rev']

    @classmethod
    def get(cls, db, doc_id, controls=True):
        doc = db.get(doc_id)
        couchdocument = cls.from_python(doc)

        if not controls:
            del(couchdocument._id)
            del(couchdocument._rev)

        return couchdocument


    @classmethod
    def get_schema(cls, controls=True):
        schema = super(CouchdbDocument, cls).get_schema()

        if controls:
            rev_definition = colander.SchemaNode(colander.String(),
                                                      widget = deform.widget.HiddenWidget(),
                                                      default=None,
                                                      name='_rev')
            id_definition = colander.SchemaNode(colander.String(),
                                                      widget = deform.widget.HiddenWidget(),
                                                      default=None,
                                                      name='_id')
            schema.add(rev_definition)
            schema.add(id_definition)

        return schema
