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
    ...             raise BaseException, "Authors's name must be in 'LastName, FirstName' format"
    
    >>> class Book(Document):
    ...     title = TextProperty(required=True, validator=text_validator)    
    ...     authors = MultiTextProperty(required=False, validator=colon_validator)    
    ...     pages = TextProperty()    
    ...     
    >>> class Book2(Document):
    ...     title = TextProperty(required=True, validator=text_validator)    
    ...     authors = CompositeTextProperty(required=False, subkeys='fl') 
    ...
    >>> class Book3(Document):
    ...     title = TextProperty(required=True, validator=text_validator)    
    ...     authors = MultiCompositeTextProperty(required=False, subkeys='fl') 
    ...

Instantiating a Book object::

    >>> book1 = Book(title='Godel, Escher, Bach',
    ...               authors=(u'Hofstadter, Douglas',),
    ...               pages='777')
    ...
    >>> book2 = Book2(title='Godel, Escher, Bach',
    ...               authors=u'^lHofstadter^fDouglas')
    ...
    >>> book3 = Book3(title='Algorithms in a nutshell',
    ...               authors=(u'^lHeineman^fGeorge T.',
    ...                        u'^lPollice^fGary',
    ...                        u'^lSelkov^fStanley'))
    ...

Manipulating its attributes::

    >>> book1.title        
    u'Godel, Escher, Bach'
    
    >>> book1.authors[0]
    u'Hofstadter, Douglas'
    
    >>> book1.authors = (u'Hofstadter Douglas',)
    Traceback (most recent call last):
    ...
    BaseException: Authors's name must be in 'LastName, FirstName' format
    
    >>> book1.authors[0]
    u'Hofstadter, Douglas'
    
    >>> book1.authors += (u'Daiana Rose',)
    Traceback (most recent call last):
    ...
    BaseException: Authors's name must be in 'LastName, FirstName' format
    
    >>> book1.authors += (u'Rose, Daiana',)
    >>> book1.authors
    (u'Hofstadter, Douglas', u'Rose, Daiana')
    
    >>> print book2.authors
    ^lHofstadter^fDouglas
    
    >>> book2.authors['f']
    u'Douglas'
    
    >>> book2.authors['j']
    Traceback (most recent call last):
    ...
    KeyError: 'j'

    >>> book3.authors[0]['f']
    u'George T.'
    
    >>> book3.authors[0]['j']
    Traceback (most recent call last):
    ...
    KeyError: 'j'
    
    >>> for i in book3.authors: print i['l']
    Heineman
    Pollice
    Selkov
"""
from isis.model import Document
from isis.model import TextProperty, MultiTextProperty
from isis.model import CompositeTextProperty, MultiCompositeTextProperty

def test():
    import doctest
    doctest.testmod()

if __name__=='__main__':
    test()