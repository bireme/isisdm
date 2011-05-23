from pyramid.config import Configurator
from pyramidattachs.resources import Root
from pyramid.events import subscriber
from pyramid.events import NewRequest, NewResponse

from pyramidattachs.main import views


import couchdbkit

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    
    
    config = Configurator(root_factory=Root, settings=settings)
    
    config.add_route('insert', '/insert', view=views.insert_entry)
    config.add_route('list', '/list', view=views.list_entries)
    config.add_route('main', '', view=views.list_entries)
    config.add_route('edit', '/edit/{id}', view=views.edit_entry)
    config.add_route('view', '/view/{id}', view=views.view_entry)
    
    db_uri = settings['db_uri']
    conn = couchdbkit.Server(db_uri)
    config.registry.settings['db_conn'] = conn
    config.add_subscriber(add_couch_db, NewRequest) 
    
    attachs_uri = settings['db_uri'] + '/' + settings['db_name']
    config.add_static_view(attachs_uri, 'pyramidattachs:attachments')
    config.add_static_view('static', 'pyramidattachs:static')
    return config.make_wsgi_app()

def add_couch_db(event):
    settings = event.request.registry.settings
    db = settings['db_conn'][settings['db_name']]
    event.request.db = db
    
