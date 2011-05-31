from isis import model


class Entry(model.CouchdbDocument):
    title = model.TextProperty()
    attachment = model.FileProperty()
    description = model.TextProperty()

