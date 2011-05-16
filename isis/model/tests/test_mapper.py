#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
----------------------
Object-document mapper
----------------------
    >>> def text_validator(node, value):
    ...     if value.startswith('Banana'):
    ...         raise BaseException, "You can't start a text with 'Banana'"
    ...

    >>> def colon_validator(node, value):
    ...     for author in value:
    ...         if ',' not in author:
    ...             raise BaseException, "Authors name must be in 'LastName, FirstName' format"

    >>> def is_number(node, value):
    ...     if not value.isdigit():
    ...         raise ValueError, "Value must be Integer"
    ...

    >>> class Book(Document):
    ...     title = TextProperty(required=True, validator=text_validator)
    ...     authors = MultiTextProperty(required=False, validator=colon_validator)
    ...     pages = TextProperty()
    ...
    >>> class Article(Document):
    ...     title = TextProperty(required=True, validator=text_validator)
    ...     authors = CompositeTextProperty(required=False, subkeys='fl')
    ...     publisher = TextProperty(required=True, validator=text_validator)
    ...
    >>> class Magazine(Document):
    ...     title = TextProperty(required=True, validator=text_validator)
    ...     authors = MultiCompositeTextProperty(required=False, subkeys='fl')
    ...     pages = TextProperty(validator=is_number)
    ...

Using ReferenceProperty::

    >>> class Collection(Document):
    ...     title = TextProperty(required=True, validator=text_validator)
    ...     publisher = TextProperty(required=True, validator=text_validator)
    ...
    >>> class BookWithinCollection(Document):
    ...     title = TextProperty(required=True, validator=text_validator)
    ...     authors = MultiCompositeTextProperty(required=False, subkeys='fl')
    ...     collection = ReferenceProperty()
    ...

Using class Meta::

    >>> class BookWithinMeta(Document):
    ...     title = TextProperty(required=True, validator=text_validator)
    ...     authors = MultiTextProperty(required=False, validator=colon_validator)
    ...     pages = TextProperty()
    ...     status = TextProperty()
    ...
    ...     class Meta:
    ...         hide = ('status',)

Using FileProperty::

    >>> class BookWithAttachment(Document):
    ...     title = TextProperty(required=True, validator=text_validator)
    ...     authors = MultiCompositeTextProperty(required=False, subkeys='fl')
    ...     cover = FileProperty()
    ...

Using BooleanProperty::

    >>> class BookWithBoolean(Document):
    ...     title = TextProperty(required=True)
    ...     is_published = BooleanProperty()
    ...

Instantiating a Book object::

    >>> book1 = Book(title='Godel, Escher, Bach',
    ...               authors=(u'Hofstadter, Douglas',),
    ...               pages='777')
    ...
    >>> article1 = Article(title='Too Soon To Tell: Essays for the End of The Computer Revolution',
    ...               authors=u'^lGrier^fDavid',
    ...               publisher=u'IEEE Computer Society')
    ...
    >>> magazine1 = Magazine(title='Algorithms in a nutshell',
    ...               authors=(u'^lGreene^fLewis Joel',
    ...                        u'^lRodrigues^fJose Antunes',
    ...                        u'^lCalixto^fJoao Batista'))
    ...
    >>> book2 = BookWithinCollection(title='Ninar songs',
    ...               authors=(u'^lHeineman^fGeorge T.',
    ...                        u'^lPollice^fGary',
    ...                        u'^lSelkov^fStanley'),
    ...               collection='123abc')
    ...
    >>> book3 = BookWithAttachment(title='Other Ninar songs',
    ...               authors=(u'^lHeineman^fGeorge T.',
    ...                        u'^lPollice^fGary',
    ...                        u'^lSelkov^fStanley'),
    ...               cover={'fp':open('test_mapper.py')})
    ...
    >>> book4 = BookWithBoolean(title='Other other Ninar songs',
    ...                         is_published=True)

Manipulating its attributes::

    >>> book1.title
    u'Godel, Escher, Bach'

    >>> book1.authors[0]
    u'Hofstadter, Douglas'

    >>> book1.authors = (u'Hofstadter Douglas',)
    Traceback (most recent call last):
    ...
    BaseException: Authors name must be in 'LastName, FirstName' format

    >>> book1.authors[0]
    u'Hofstadter, Douglas'

    >>> book1.authors += (u'Daiana Rose',)
    Traceback (most recent call last):
    ...
    BaseException: Authors name must be in 'LastName, FirstName' format

    >>> book1.authors += (u'Rose, Daiana',)
    >>> book1.authors
    (u'Hofstadter, Douglas', u'Rose, Daiana')

    >>> print article1.authors
    ^lGrier^fDavid

    >>> article1.authors['f']
    u'David'

    >>> article1.authors['j']
    Traceback (most recent call last):
    ...
    KeyError: 'j'

    >>> magazine1.authors[0]['f']
    u'Lewis Joel'

    >>> magazine1.authors[0]['j']
    Traceback (most recent call last):
    ...
    KeyError: 'j'

    >>> for i in magazine1.authors: print i['l']
    Greene
    Rodrigues
    Calixto

    >>> book2.collection
    u'123abc'
    >>> book2.collection = tuple('abcdef')
    Traceback (most recent call last):
      ...
    TypeError: Reference value must be unicode or str instance

    >>> book4.is_published
    True
    >>> book4.is_published = 'must raise error'
    Traceback (most recent call last):
      ...
    TypeError: 'is_published' must be bool

Colander Schema Generation::

    >>> book1.to_python() == {'authors': (u'Hofstadter, Douglas', u'Rose, Daiana'),
    ...     'TYPE': 'Book', 'pages': u'777', 'title': u'Godel, Escher, Bach'}
    True


    >>> sc = Book.get_schema()
    >>> ' '.join('%s:%s' % (c.name, type(c.typ).__name__) for c in sc.children)
    'title:String authors:Sequence pages:String'

    >>> book_with_bool_schema = BookWithBoolean.get_schema()
    >>> ' '.join('%s:%s' % (c.name, type(c.typ).__name__) for c in book_with_bool_schema.children)
    'title:String is_published:Boolean'

Hidding an attribute

    >>> book_with_meta_schema = BookWithinMeta.get_schema()
    >>> ' '.join('%s:%s' % (c.name, type(c.typ).__name__) for c in book_with_meta_schema.children)
    'title:String authors:Sequence pages:String'
"""
from isis.model import Document
from isis.model import TextProperty, MultiTextProperty
from isis.model import CompositeTextProperty, MultiCompositeTextProperty
from isis.model import ReferenceProperty, FileProperty, BooleanProperty

def test():
    import doctest
    doctest.testmod()

if __name__=='__main__':
    test()