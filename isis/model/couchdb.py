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
    """
    >>> old_doc = {u'title': u'Title example', u'_rev': u'25-9b1b088acc5d42cc9cb97bf18781811b', u'cover': {u'filename': u'campos lilacs_scielolivros.xls', u'uid': u'BCE0I1KH1Y', u'md5': u'7da75d0e101dbf5c2eec9e117ae82e58'}, u'_attachments': {u'campos lilacs_scielolivros.xls': {u'stub': True, u'length': 17408, u'revpos': 25, u'content_type': u'application/vnd.ms-excel'}}, u'_id': u'rhvkd', u'TYPE': u'Monograph'}
    >>> _attach_exists(old_doc, 'cover')
    True
    >>> _attach_exists(old_doc, 'title')
    False
    >>> _attach_exists(old_doc, 'not_exists')
    False
    """

    if property_name in old_doc:
        try:
            if old_doc[property_name]['filename'] in old_doc['_attachments']:
                return True
        except (AttributeError, TypeError):
            pass
        
    return False

def _attach_updated(old_doc, new_doc, property_name):
    """
    >>> old_doc_no_attach = {u'title': u'Title example', u'_rev': u'25-9b1b088acc5d42cc9cb97bf18781811b',  u'_attachments': {u'campos lilacs_scielolivros.xls': {u'stub': True, u'length': 17408, u'revpos': 25, u'content_type': u'application/vnd.ms-excel'}}, u'_id': u'rhvkd', u'TYPE': u'Monograph'}
    >>> old_doc_with_attach = {u'title': u'Title example', u'_rev': u'25-9b1b088acc5d42cc9cb97bf18781811b', u'cover': {u'filename': u'campos lilacs_scielolivros.xls', u'uid': u'BCE0I1KH1Y', u'md5': u'7da75d0e101dbf5c2eec9e117ae82e58'}, u'_attachments': {u'campos lilacs_scielolivros.xls': {u'stub': True, u'length': 17408, u'revpos': 25, u'content_type': u'application/vnd.ms-excel'}}, u'_id': u'rhvkd', u'TYPE': u'Monograph'}
    >>> updated_attach = {u'title': u'Title example', u'_rev': u'25-9b1b088acc5d42cc9cb97bf18781811b', u'cover': {u'filename': u'updated.xls', u'uid': u'BCE0I1KH1Y', u'md5': u'7da75d0e101dbf5c2eec9e117aj32b7'}, u'_attachments': {u'updated.xls': {u'stub': True, u'length': 19408, u'revpos': 26, u'content_type': u'application/vnd.ms-excel'}}, u'_id': u'rhvkd', u'TYPE': u'Monograph'}
    >>> updated_doc = {u'title': u'Title updated', u'_rev': u'25-9b1b088acc5d42cc9cb97bf18781811b', u'cover': {u'filename': u'campos lilacs_scielolivros.xls', u'uid': u'BCE0I1KH1Y', u'md5': u'7da75d0e101dbf5c2eec9e117ae82e58'}, u'_attachments': {u'campos lilacs_scielolivros.xls': {u'stub': True, u'length': 17408, u'revpos': 25, u'content_type': u'application/vnd.ms-excel'}}, u'_id': u'rhvkd', u'TYPE': u'Monograph'}
    >>> updated_doc_no_attach = {u'title': u'Title updated', u'_rev': u'25-9b1b088acc5d42cc9cb97bf18781811b', u'_id': u'rhvkd', u'TYPE': u'Monograph'}
    >>> _attach_updated(old_doc_no_attach, updated_attach, 'cover')
    True
    >>> _attach_updated(old_doc_no_attach, updated_doc, 'cover')
    True
    >>> _attach_updated(old_doc_with_attach, updated_attach, 'cover')
    True
    >>> _attach_updated(old_doc_with_attach, updated_doc, 'cover')
    False
    >>> _attach_updated(old_doc_no_attach, updated_doc_no_attach, 'cover')
    False
    >>> _attach_updated(old_doc_with_attach, updated_attach, 'title')
    False
    >>> _attach_updated(old_doc_with_attach, updated_doc, 'title')
    False    
    """
    if _attach_exists(new_doc, property_name):
        if not _attach_exists(old_doc, property_name):
            return True
        else:
            return not new_doc[property_name]['md5'] == old_doc[property_name]['md5']

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
        new_doc = self.to_python()
        new_doc = self.__clean_before_save(new_doc)
        
        old_doc = db.get(new_doc['_id']) if '_rev' in new_doc else None
                
        while True:
            try:
                db.save_doc(new_doc)
                break
            except couchdbkit.ResourceConflict:
                time.sleep(0.5)
                new_doc['_id'] = base28.genbase(5)

        for key in self.__class__:
            prop = self.__class__.__getattribute__(self.__class__,key)
            if isinstance(prop, FileProperty):
                if old_doc is None:
                    #Novo documento, PUT do anexo para o couchdb
                    file_metadata = getattr(self,key, None)
                    if file_metadata:
                        db.put_attachment(new_doc, file_metadata['fp'], getattr(self, key)['filename'])
                
                elif _attach_exists(old_doc, key) and not _attach_updated(old_doc, new_doc, key):
                    #Anexo existe e nao foi alterado
                    #FIXME
                    new_doc['_attachments'] = old_doc['_attachments']
                    new_doc[key] = old_doc[key]     
                    db.save_doc(new_doc)
                else:
                    #PUT do anexo para o couchdb
                    file_metadata = getattr(self,key, None)
                    if file_metadata:
                        db.put_attachment(new_doc, file_metadata['fp'], getattr(self, key)['filename'])

        self._id, self._rev = new_doc['_id'], new_doc['_rev']
    
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

if __name__=='__main__':
    import doctest
    doctest.testmod()