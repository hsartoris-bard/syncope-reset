import flask
from werkzeug.routing import Rule
from werkzeug.middleware.proxy_fix import ProxyFix

import logging

def _force_https(wsgi_app):
    def wrapper(environe, start_response):
        environ['wsgi.url_scheme'] = 'https'
        return wsgi_app(environ, start_response)
    return wrapper

def create_app(proxy_fix = True, secret_key = None):
    from app.config import PREFIX
    if not PREFIX.startswith('/'):
        prefix = f'/{PREFIX}'
    else:
        prefix = PREFIX

    app = Flask(__name__, static_url_path = f'{prefix}/static')
    app.config.from_pyfile('config.py')

    if secret_key:
        app.secret_key = secret_key

    with app.app_context():
        from app.main import main

    app.wsgi_app = _force_https(app.wsgi_app)
    app.prefix = prefix
    app.config['APPLICATION_ROOT'] = prefix

    app.url_rule_class = lambda path, **options: Rule(app.prefix + path, **options)

    app.register_blueprint(main)

    if proxy_fix:
        return ProxyFix(app, x_for=1, x_host=1)
    return app


