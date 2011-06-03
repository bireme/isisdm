from pyramid.config import Configurator
from pyramid.response import Response
from pyramid.view import view_config
from pyramid.renderers import render_to_response

from paste.httpserver import serve
from models import Bibitex
from forms import BibitexForm

import deform
import couchdbkit

def new(request):
    bibitex_form = BibitexForm.get_form()

    if 'submit' in request.POST:   
        controls = request.POST.items()
        try:
            appstruct = bibitex_form.validate(controls)
        except deform.ValidationFailure, e:
            return render_to_response('bibitex:form.pt',
              {'content': e.render()})

        bibitex = Bibitex.from_python(appstruct)
        bibitex.save(db)

        return Response('Saved under id: %s' % bibitex._id)
    else:

        if 'id' in request.matchdict: #edit
            bibitex = Bibitex.get(db, request.matchdict['id'])
            
            return render_to_response('bibitex:form.pt',
              {'content': bibitex_form.render(bibitex.to_python())})

        return render_to_response('bibitex:form.pt',
          {'content': bibitex_form.render()})


def index(request):
    records = db.view('_all_docs', include_docs=True)

    return render_to_response('bibitex:index.pt',
      {'records':records})


if __name__ == '__main__':
    config = Configurator()

    """Configuring couchdb"""
    server = couchdbkit.Server()
    db = server.get_or_create_db('bibitex')

    """Adding static views"""
    config.add_static_view('deform_static', 'deform:static')

    """Registering views and routes"""
    config.add_view(view=index, route_name='index')
    config.add_view(view=new, route_name='new')
    config.add_view(view=new, route_name='edit')
    config.add_route('index', '/')
    config.add_route('new', '/new')
    config.add_route('edit', '/edit/{id}')
    
    app = config.make_wsgi_app()
    serve(app, host='0.0.0.0:6543')