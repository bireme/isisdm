from pyramid.response import Response
from pyramid.renderers import render_to_response
from pyramid.url import static_url

from .models import Entry

import deform
import couchdbkit
import Image
import StringIO

def list_entries(request):

    all_docs = request.db.view('_all_docs', include_docs=True).all()
    result = []
    
    for doc in all_docs:
        doc = doc['doc']
        result.append({'key':doc['_id'],
                      'value':doc['title']
                      })
    return render_to_response('templates/list.pt',
                              {'result':result},
                              request=request)
    
def view_entry(request):
    doc = request.db.get(request.matchdict['id'])    
    
    return render_to_response('templates/view.pt',
                              {'title':doc['title'],
                               'about':doc['description'],
                               '_id': doc['_id']},
                              request=request)

def insert_entry(request):
    entry_schema = Entry.get_schema()
    entry_form = deform.Form(entry_schema, buttons=('submit',))
    
    if 'submit' in request.POST:
        controls = request.POST.items()
        try:
            appstruct = entry_form.validate(controls)
        except deform.ValidationFailure, e:
            return Response(e.render())       

        entry = Entry.from_python(appstruct)
        entry_id = entry.save(request.db)
        
        return Response('''<html>
                            <p>Inserido com sucesso sob o ID %s</p>
                            <a href="/list">Voltar</a>
                            ''' % entry._id)

    return Response(entry_form.render())

def edit_entry(request):
    entry_schema = Entry.get_schema()
    entry_form = deform.Form(entry_schema, buttons=('submit',))
    
    if 'submit' in request.POST:
        controls = request.POST.items()
        try:
            appstruct = entry_form.validate(controls)
        except deform.ValidationFailure, e:
            return Response(e.render())
        
        entry = Entry.from_python(appstruct)
        
        entry._id = request.matchdict['id']
        entry._rev = request.db.get(entry._id)['_rev']

        entry_id = entry.save(request.db)
        
        response_text = '''<html>
                        <p>Atualizado com sucesso sob o ID %s </p>
                        <a href="/list">Voltar</a>
                    </html>''' % entry._id
        return Response(response_text)

    else:        
        try:
           entry = request.db.get(request.matchdict['id'])
        except couchdbkit.ResourceNotFound:
            raise exceptions.NotFound()
         
    return Response(entry_form.render(entry))
    

