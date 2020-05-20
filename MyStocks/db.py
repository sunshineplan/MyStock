import sqlite3

from flask import current_app, g


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def get_db():
    '''Connect to the application's configured database. The connection
    is unique for each request and will be reused if this is called
    again.
    '''
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'], detect_types=sqlite3.PARSE_DECLTYPES)
        g.db.row_factory = dict_factory
    return g.db


def close_db(e=None):
    '''If this request connected to the database, close the
    connection.
    '''
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db(app=current_app):
    '''Clear existing data and create new tables and views.'''
    db = sqlite3.connect(
        app.config['DATABASE'], detect_types=sqlite3.PARSE_DECLTYPES)
    with app.open_resource('drop_all.sql') as f:
        db.executescript(f.read().decode('utf8'))
    with app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


def init_app(app):
    '''Register database functions with the Flask app. This is called by
    the application factory.
    '''
    app.teardown_appcontext(close_db)
