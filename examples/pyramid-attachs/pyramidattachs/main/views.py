from pyramid.response import Response
from pyramid.renderers import render_to_response
from pyramid.url import static_url

from .models import Entry

import deform
import couchdbkit
import Image
import StringIO

def list_entries(request):
    all_docs = request.db.view('pyattachs/all_docs')        
    return render_to_response('templates/list.pt',
                              {'result':all_docs.all()},
                              request=request)
    
def view_entry(request):
    doc = request.db.get(request.matchdict['id'])
    
    img_url = static_url('pyramidattachs:attachments/%s/%s', request)  % (doc['_id'], doc['attachment']['filename'])
    
    return render_to_response('templates/view.pt',
                              {'title':doc['title'],
                               'attach':img_url,
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
        entry.save(request.db)
        
        return Response('Inserido com sucesso sob o ID ' + entry._id)

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
    

