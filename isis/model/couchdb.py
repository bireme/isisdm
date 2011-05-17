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
        pstruct['_id'] = self._id
        
        try:
            pstruct['_rev'] = self._rev
        except AttributeError:
            pass
        
        return pstruct

    @classmethod
    def from_python(cls, pystruct):
        if pystruct['_id'] == 'None':
            pystruct['_id'] = None
        if pystruct['_rev'] == 'None':
            pystruct['_rev'] = None
        
        return super(CouchdbDocument, cls).from_python(pystruct)

    def save(self, db):

        doc = self.to_python()

        doc = self.__clean_before_save(doc)

        while True:
            try:
                db.save_doc(doc)
                for key in self.__class__:
                    prop = self.__class__.__getattribute__(self.__class__,key)
                    if isinstance(prop, FileProperty):                        
                        file_dict = getattr(self,key)
                        db.put_attachment(doc, file_dict['fp'], getattr(self, key)['filename'])                        
                break
            except couchdbkit.ResourceConflict:
                time.sleep(0.5)
                doc['_id'] = base28.genbase(5)

        return doc['_id']
    
    @classmethod
    def get(cls, db, doc_id):
        doc = db.get(doc_id)
        return cls.from_python(doc)

    @classmethod
    def get_schema(cls):
        schema = super(CouchdbDocument, cls).get_schema()
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