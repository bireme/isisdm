from isis import model
import deform

choices = ['article', 'book', 'booklet', 'conference', 'inbook', 'incollection', 'inproceedings',
           'manual', 'mastersthesis', 'misc', 'phdthesis', 'proceedings', 'techreport', 'unpublished', ]

class Bibitex(model.CouchdbDocument):
    entry_type = model.TextProperty(choices=[(entry,entry) for entry in choices],)
    reference_name = model.TextProperty(required=True)
    title = model.TextProperty(required=True)
    authors = model.MultiCompositeTextProperty(required=True, subkeys=['name', 'lastname'])
    publisher = model.TextProperty()
    year = model.TextProperty()
    address = model.TextProperty()
    review = model.TextProperty()


