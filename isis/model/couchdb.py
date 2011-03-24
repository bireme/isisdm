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

from .mapper import Document
import uuid

class CouchdbDocument(Document):

    def save(self, db):
        doc = self.to_python()
        if not doc.has_key('_id'):
            doc['_id'] = str(uuid.uuid4())
        db.save_doc(doc)
        return doc['_id']

    @classmethod
    def get(cls, db, doc_id):
        doc = db.get(doc_id)
        return cls.from_python(doc)

    def to_python(self):
        '''
        generate a python representation for Document type classes
        '''
        properties = {}
        properties['type'] = self.__class__.__name__
        for prop in self:
            descriptor = self.__class__.__getattribute__(self.__class__, prop)
            properties[prop] = descriptor._pystruct(self, getattr(self, prop, None))
        return properties

    @classmethod
    def from_python(cls, pystruct):
        if cls.__name__ != pystruct.pop('type'):
            raise TypeError()

        isisdm_pystruct = dict((str(k), tuple(v) if isinstance(v, list) else v)
            for k, v in pystruct.items())

        return cls(**isisdm_pystruct)