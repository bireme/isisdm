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


Instantiating a Book object::

    >>> book1 = Book(title='Godel, Escher, Bach',
    ...               authors=(u'Hofstadter, Douglas',),
    ...               pages='777')
    ...

    >>> book1.to_python() == {'authors': (u'Hofstadter, Douglas',),
    ...     'TYPE': 'Book', 'pages': u'777', 'title': u'Godel, Escher, Bach'}
    True

    >>> book1_id = book1.save(db)

    >>> book2 = Book.get(db, book1_id)
    >>> book2.title
    u'Godel, Escher, Bach'
"""
from isis.model import CouchdbDocument
from isis.model import TextProperty, MultiTextProperty
from isis.model import CompositeTextProperty, MultiCompositeTextProperty, ReferenceProperty
import couchdbkit


def test():
    import doctest
    doctest.testmod()

if __name__=='__main__':
    conn = couchdbkit.Server('http://127.0.0.1:5984')
    db = conn.get_or_create_db('isismodel_api')
    test()