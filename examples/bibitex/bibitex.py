from pyramid.config import Configurator
from pyramid.response import Response
from pyramid.view import view_config
from pyramid.renderers import render_to_response

from paste.httpserver import serve
from models import Bibitex
from forms import BibitexForm

import deform
import couchdbkit



def hello_world(request):
    return Response('Hello world!')

def goodbye_world(request):
    return Response('Goodbye world!')


def new_entry(request):
    bibitex_form = BibitexForm.get_form()
    if 'submit' in request.POST:
        return Response('OK')
    else:
        return render_to_response('bibitex:template.pt',
                                  {'content': bibitex_form.render()},
                                  )

def list_all(request):
    pass

def view_entry(request):
    pass


if __name__ == '__main__':
    config = Configurator()

    """Configuring couchdb"""
    server = couchdbkit.Server()
    db = server.get_or_create_db('bibitex')

    """Adding static views"""
    config.add_static_view('deform_static', 'deform:static')

    """Adding views"""
    config.add_view(list_all)
    config.add_view(new_entry, name="new_entry")
    config.add_view(view_entry, name="view_entry")
    
    app = config.make_wsgi_app()
    serve(app, host='0.0.0.0')