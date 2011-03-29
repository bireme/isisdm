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

from .mapper import Document, TextProperty
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
