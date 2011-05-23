from pyramid.config import Configurator
from pyramidattachs.resources import Root

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(root_factory=Root, settings=settings)
    config.add_view('pyramidattachs.views.my_view',
                    context='pyramidattachs:resources.Root',
                    renderer='pyramidattachs:templates/mytemplate.pt')
    config.add_static_view('static', 'pyramidattachs:static')
    return config.make_wsgi_app()

