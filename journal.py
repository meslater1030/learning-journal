# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
from pyramid.config import Configurator
from pyramid.view import view_config
from waitress import serve
import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
import datetime
from sqlalchemy import create_engine

Base = declarative_base()


class Entry(Base):
    __tablename__ = 'entries'

    id = sa.Column(sa.Integer, primary_key=True)
    title = sa.Column(sa.String(128))
    text = sa.Column(sa.String, nullable=False)
    created = sa.Column(sa.DateTime, nullable=False,
                        default=datetime.datetime.utcnow)

    def __repr__(self):
        return "<Entry(title='%s', created='%s')>" % (
            self.title, self.created)

DATABASE_URL = os.environ.get(
    'DATABASE_URL',
    'postgresql://meslater@localhost:5432/learning-journal')


def init_db():
    engine = create_engine('DATABASE_URL')
    Base.metadata.create_all(engine)


@view_config(route_name='home', renderer='string')
def home(request):
    return "Hello World"


def main():
    """Create a configured wsgi app"""
    settings = {}
    debug = os.environ.get('DEBUG', True)
    settings['reload_all'] = debug
    settings['debug_all'] = debug
    # configuration setup
    config = Configurator(
        settings=settings
        )
    config.add_route('home', '/')
    config.scan()
    app = config.make_wsgi_app()
    return app

if __name__ == '__main__':
    app = main()
    port = os.environ.get('PORT', 5000)
    serve(app, host='0.0.0.0', port=port)
