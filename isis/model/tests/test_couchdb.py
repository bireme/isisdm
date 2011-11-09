#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
--------------------------------
Persisting a document in CouchDB
--------------------------------
    >>> def text_validator(node, value):
    ...     if value.startswith('Banana'):
    ...         raise Exception("You can't start a text with 'Banana'")
    ...

    >>> def colon_validator(node, value):
    ...     for author in value:
    ...         if ',' not in author:
    ...             raise Exception("Authors name must be in 'LastName, FirstName' format")

    >>> class Book(CouchdbDocument):
    ...     title = TextProperty(required=True, validator=text_validator)
    ...     authors = MultiTextProperty(required=False, validator=colon_validator)
    ...     pages = TextProperty()

    >>> class BookWithAttachment(CouchdbDocument):
    ...     title = TextProperty(required=True, validator=text_validator)
    ...     authors = MultiIsisCompositeTextProperty(required=False, subkeys='fl')
    ...     cover = FileProperty()
    ...

Instantiating a Book object::

    >>> book1 = Book(title='Godel, Escher, Bach',
    ...               authors=(u'Hofstadter, Douglas',),
    ...               pages='777',)
    ...

    >>> len(book1._id)
    5

    >>> for key in sorted(book1.to_python()): print key, book1.to_python()[key] #doctest: +ELLIPSIS
    TYPE Book
    _id ...
    authors (u'Hofstadter, Douglas',)
    pages 777
    title Godel, Escher, Bach

    >>> book1.save(db)

    >>> book2 = Book.get(db, book1._id)
    >>> book2.title
    u'Godel, Escher, Bach'

    >>> book3 = BookWithAttachment(title='Other Ninar songs',
    ...               authors=(u'^lHeineman^fGeorge T.',
    ...                        u'^lPollice^fGary',
    ...                        u'^lSelkov^fStanley'),
    ...               cover={'fp':open('test_mapper.py'),'uid':'asldkfj', 'filename':'test_mapper.py'})
    ...
    >>> book3_id = book3.save(db)

    >>> book_schema = BookWithAttachment.get_schema()
    >>> ' '.join('%s:%s' % (c.name, type(c.typ).__name__) for c in book_schema.children)
    'title:String authors:Sequence cover:FileData _rev:String _id:String'


----------------------------------------
_attach_updated method tests
----------------------------------------
    >>> tmpfile = open(__file__)
    >>> updated_attach = {u'title': u'Title example', u'_rev': u'25-9b1b088acc5d42cc9cb97bf18781811b', u'cover': {u'filename': u'updated.xls', u'uid': u'BCE0I1KH1Y', u'md5': u'7da75d0e101dbf5c2eec9e117aj32b7', u'fp': tmpfile}, u'_attachments': {u'updated.xls': {u'stub': True, u'length': 19408, u'revpos': 26, u'content_type': u'application/vnd.ms-excel'}}, u'_id': u'rhvkd', u'TYPE': u'Monograph'}
    >>> updated_doc = {u'title': u'Title updated', u'_rev': u'25-9b1b088acc5d42cc9cb97bf18781811b', u'_attachments': {u'campos lilacs_scielolivros.xls': {u'stub': True, u'length': 17408, u'revpos': 25, u'content_type': u'application/vnd.ms-excel'}}, u'_id': u'rhvkd', u'TYPE': u'Monograph'}
    >>> updated_doc_no_attach = {u'title': u'Title updated', u'_rev': u'25-9b1b088acc5d42cc9cb97bf18781811b', u'_id': u'rhvkd', u'TYPE': u'Monograph'}
    >>> _attach_updated(updated_attach, 'cover')
    True
    >>> _attach_updated(updated_doc, 'cover')
    False
    >>> _attach_updated(updated_doc_no_attach, 'cover')
    False

----------------------------------------
_attach_exists method tests
----------------------------------------
    >>> old_doc = {u'title': u'Title example', u'_rev': u'25-9b1b088acc5d42cc9cb97bf18781811b', u'cover': {u'filename': u'campos lilacs_scielolivros.xls', u'uid': u'BCE0I1KH1Y', u'md5': u'7da75d0e101dbf5c2eec9e117ae82e58'}, u'_attachments': {u'campos lilacs_scielolivros.xls': {u'stub': True, u'length': 17408, u'revpos': 25, u'content_type': u'application/vnd.ms-excel'}}, u'_id': u'rhvkd', u'TYPE': u'Monograph'}
    >>> _attach_exists(old_doc, 'cover')
    True
    >>> _attach_exists(old_doc, 'title')
    False
    >>> _attach_exists(old_doc, 'not_exists')
    False

"""
from isis.model import CouchdbDocument
from isis.model import TextProperty, MultiTextProperty
from isis.model import CompositeTextProperty, MultiCompositeTextProperty, ReferenceProperty, FileProperty
from isis.model import IsisCompositeTextProperty, MultiIsisCompositeTextProperty
from isis.model.couchdb import _attach_updated, _attach_exists
import couchdbkit


def test():
    import doctest
    doctest.testmod()

if __name__=='__main__':
    conn = couchdbkit.Server('http://127.0.0.1:5984')
    db = conn.get_or_create_db('isismodel_api')
    test()