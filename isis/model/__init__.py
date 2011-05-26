# package
from .mapper import Document
from .mapper import TextProperty, MultiTextProperty
from .mapper import CompositeTextProperty, IsisCompositeTextProperty, MultiCompositeTextProperty
from .mapper import ReferenceProperty, FileProperty, BooleanProperty
from .couchdb import CouchdbDocument