# package
from .mapper import Document
from .mapper import TextProperty, MultiTextProperty
from .mapper import CompositeTextProperty, IsisCompositeTextProperty
from .mapper import MultiIsisCompositeTextProperty, MultiCompositeTextProperty
from .mapper import ReferenceProperty, FileProperty, BooleanProperty
from .couchdb import CouchdbDocument