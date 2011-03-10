#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
Em Python os atributos de uma classe são armazenados em um `dict`, portanto
sua ordem não é preservada. Normalmente a ordem não é realmente importante.

Note no exemplo abaixo que a lista devolvida por `dir(l)` não preserva
a ordem em que foram declarados os atributos na classe `Livro`::

    >>> class LivroSimples(object):
    ...     titulo = u''
    ...     isbn = u''
    ...     autores = u''
    >>> l = LivroSimples()
    >>> dir(l) #doctest: +ELLIPSIS
    [...'autores', 'isbn', 'titulo'...]
    
Para gerar formulários automaticamente a partir da classe, é desejável
respeitar a ordem de declaração dos campos. Usando descritores e uma 
metaclasse, é possível preservar esta ordem.

    >>> class Livro(OrderedModel):
    ...     titulo = OrderedProperty()
    ...     isbn = OrderedProperty()
    ...     autores = OrderedProperty()
    >>> l2 = Livro()
    >>> l2.titulo = 'O Alienista'
    >>> l2.titulo
    'O Alienista'
    >>> list(l2)
    ['titulo', 'isbn', 'autores']
    >>> for campo in l2: print campo
    titulo
    isbn
    autores
    >>> l3 = Livro()
    >>> l3.titulo
    Traceback (most recent call last):
      ...
    AttributeError: 'Livro' object has no attribute 'titulo'
    >>> l4 = Livro(titulo=u'Alice', autores=[u'Carroll', u'Tenniel'], isbn=u'9781234567890')
    >>> for campo, valor in l4.iteritems():
    ...     print '%-8s: %s' % (campo, valor)
    titulo  : Alice
    isbn    : 9781234567890
    autores : [u'Carroll', u'Tenniel']
    
    
    
Os descritores têm um atributo `order` que é inicializado com um contador da 
classe `OrderedProperty` incrementado a cada nova instância. A metaclasse usa
este atributo `order` para ordenar uma lista com os nomes dos campos.

    >>> class Bicicleta(OrderedModel):
    ...     rodas = OrderedProperty()
    ...     aro = OrderedProperty()
    ...     cor = OrderedProperty()
    ...
    >>> bike = Bicicleta()
    >>> bike.rodas = 2
    >>> bike.aro = 26
    >>> bike.cor = u'preto'
    ...

"""
from isis.model.ordered import OrderedModel, OrderedProperty

def test():
    import doctest
    doctest.testmod()

if __name__=='__main__':
    test()