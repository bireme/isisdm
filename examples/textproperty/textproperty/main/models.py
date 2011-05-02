from isis import model


class Entry(model.CouchdbDocument):
    title = model.TextProperty()
    description = model.TextProperty()

