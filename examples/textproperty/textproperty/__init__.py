from pyramid.config import Configurator
from textproperty.resources import Root
from pyramid.events import subscriber
from pyramid.events import NewRequest, NewResponse

from textproperty.main import views


import couchdbkit

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    
    
    config = Configurator(root_factory=Root, settings=settings)
    
    config.add_route('insert', '/insert', view=views.insert_entry)
    config.add_route('list', '/list', view=views.list_entries)
    config.add_route('edit', '/edit/{id}', view=views.edit_entry)
    config.add_route('view', '/view/{id}', view=views.view_entry)
    config.add_route('index', '', view=views.list_entries)
    
    db_uri = settings['db_uri']
    conn = couchdbkit.Server(db_uri)
    
    db = conn.get_or_create_db(settings['db_name']) #create DB if it doesnt exist
    
    config.registry.settings['db_conn'] = conn
    config.add_subscriber(add_couch_db, NewRequest) 
    
    attachs_uri = settings['db_uri'] + '/' + settings['db_name']
    config.add_static_view(attachs_uri, 'textproperty:attachments')
    config.add_static_view('static', 'textproperty:static')
    return config.make_wsgi_app()

def add_couch_db(event):
    
    settings = event.request.registry.settings
    db = settings['db_conn'][settings['db_name']]
    event.request.db = db
    
