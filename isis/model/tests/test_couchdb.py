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
    ...     authors = MultiCompositeTextProperty(required=False, subkeys='fl')
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

    >>> book1_id = book1.save(db)

    >>> book2 = Book.get(db, book1_id)
    >>> book2.title
    u'Godel, Escher, Bach'

    >>> book3 = BookWithAttachment(title='Other Ninar songs',
    ...               authors=(u'^lHeineman^fGeorge T.',
    ...                        u'^lPollice^fGary',
    ...                        u'^lSelkov^fStanley'),
    ...               cover={'fp':open('test_mapper.py')})
    ...
    >>> book3_id = book3.save(db)



"""
from isis.model import CouchdbDocument
from isis.model import TextProperty, MultiTextProperty
from isis.model import CompositeTextProperty, MultiCompositeTextProperty, ReferenceProperty, FileProperty
import couchdbkit


def test():
    import doctest
    doctest.testmod()

if __name__=='__main__':
    conn = couchdbkit.Server('http://127.0.0.1:5984')
    db = conn.get_or_create_db('isismodel_api')
    test()