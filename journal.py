# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from cryptacular.bcrypt import BCRYPTPasswordManager
import datetime
import os
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator
from pyramid.httpexceptions import HTTPFound
from pyramid.security import remember, forget
from pyramid.view import view_config
import sqlalchemy as sa
from sqlalchemy import create_engine
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from waitress import serve
from zope.sqlalchemy import ZopeTransactionExtension

# all the global variables
HERE = os.path.dirname(os.path.abspath(__file__))
DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()
DATABASE_URL = os.environ.get(
    'DATABASE_URL',
    'postgresql://meslater@localhost:5432/learning-journal'
)


# all the classes
class Entry(Base):
    __tablename__ = 'entries'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    title = sa.Column(sa.Unicode(128), nullable=False)
    text = sa.Column(sa.UnicodeText, nullable=False)
    created = sa.Column(sa.DateTime, nullable=False,
                        default=datetime.datetime.utcnow)

    @classmethod
    def write(cls, title=None, text=None, session=None):
        if session is None:
            session = DBSession
        instance = cls(title=title, text=text)
        session.add(instance)
        return instance

    @classmethod
    def edit(cls, title=None, text=None, session=None, id=None):
        if session is None:
            session = DBSession
        instance = cls(title=title, text=text, id=id)
        if title is not "" and text is not "":
            session.query(cls).filter(cls.id == id).update(
                {"title": title, "text": text})
        else:
            session.query(cls).filter(cls.id == id).delete()
        return instance

    @classmethod
    def id_lookup(cls, id=None, session=None):
        if session is None:
            session = DBSession
        return session.query(cls).filter(cls.id == id).one()

    @classmethod
    def all(cls, session=None):
        if session is None:
            session = DBSession
        return session.query(cls).order_by(cls.created.desc()).all()

    def __repr__(self):
        return "<Entry(title='%s', created='%s')>" % (
            self.title, self.created)

# all the views


@view_config(route_name='add', request_method='POST')
def add_entry(request):
    title = request.params.get('title')
    text = request.params.get('text')
    Entry.write(title=title, text=text)
    return HTTPFound(request.route_url('home'))


@view_config(route_name='add', renderer="templates/add.jinja2")
def add_entry_view(request):
    username = request.params.get('username', '')
    return {'username': username}


@view_config(route_name='edit', request_method='POST')
def edit_entry(request):
    entry = Entry.id_lookup(request.matchdict['id'])
    title = request.params.get('title')
    text = request.params.get('text')
    id = entry.id
    Entry.edit(title=title, text=text, id=id)
    return HTTPFound(request.route_url('home'))


@view_config(route_name='edit', renderer="templates/edit.jinja2")
def edit_view(request):
    entry = Entry.id_lookup(request.matchdict['id'])
    return {'entry': {
            'id': entry.id,
            'title': entry.title,
            'text': entry.text,
            'created': entry.created}}


@view_config(context=DBAPIError)
def db_exception(context, request):
    from pyramid.response import Response
    response = Response(context.message)
    response.status_int = 500
    return response


@view_config(route_name='permalink', renderer="templates/permalink.jinja2")
def permalink_view(request):
    entry = Entry.id_lookup(request.matchdict['id'])
    return {'entry': {
            'id': entry.id,
            'title': entry.title,
            'text': entry.text,
            'created': entry.created}}


@view_config(route_name='home', renderer='templates/list.jinja2')
def list_view(request):
    entries = Entry.all()
    return {'entries': entries}


@view_config(route_name='login', renderer="templates/login.jinja2")
def login(request):
    """authenticate a user by username/password"""
    username = request.params.get('username', '')
    error = ''
    if request.method == 'POST':
        error = "Login Failed"
        authenticated = False
        try:
            authenticated = do_login(request)
        except ValueError as e:
            error = str(e)

        if authenticated:
            headers = remember(request, username)
            return HTTPFound(request.route_url('home'), headers=headers)

    return {'error': error, 'username': username}


@view_config(route_name='logout')
def logout(request):
    headers = forget(request)
    return HTTPFound(request.route_url('home'), headers=headers)

# all the functions


def do_login(request):
    username = request.params.get('username', None)
    password = request.params.get('password', None)
    if not (username and password):
        raise ValueError('both username and password are required')
    settings = request.registry.settings
    manager = BCRYPTPasswordManager()
    if username == settings.get('auth.username', ''):
        hashed = settings.get('auth.password', '')
        return manager.check(hashed, password)


def init_db():
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)


def main():
    """Create a configured wsgi app"""
    settings = {}
    debug = os.environ.get('DEBUG', True)
    settings['reload_all'] = debug
    settings['debug_all'] = debug
    settings['auth.username'] = os.environ.get('AUTH_USERNAME', 'admin')
    settings['auth.password'] = os.environ.get('AUTH_PASSWORD', 'secret')
    manager = BCRYPTPasswordManager()
    settings['auth.password'] = os.environ.get(
        'AUTH_PASSWORD', manager.encode('secret')
        )
    if not os.environ.get('TESTING', False):
        engine = sa.create_engine(DATABASE_URL)
        DBSession.configure(bind=engine)
    # add a secret value for auth tkt signing
    auth_secret = os.environ.get('JOURNAL_AUTH_SECRET', 'itsaseekrit')
    # configuration setup
    config = Configurator(
        settings=settings,
        # add a new value to the constructor for our Configurator:
        authentication_policy=AuthTktAuthenticationPolicy(
            secret=auth_secret,
            hashalg='sha512'
        ),
        authorization_policy=ACLAuthorizationPolicy(),
        )
    config.include('pyramid_tm')
    config.include('pyramid_jinja2')
    config.add_static_view('static', os.path.join(HERE, 'static'))
    config.add_route('home', '/')
    config.add_route('add', '/add')
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')
    config.add_route('permalink', '/{id}/{title}')
    config.add_route('edit', 'edit/{id}/{title}')
    config.scan()
    app = config.make_wsgi_app()
    return app

if __name__ == '__main__':
    app = main()
    port = os.environ.get('PORT', 5000)
    serve(app, host='0.0.0.0', port=port)
