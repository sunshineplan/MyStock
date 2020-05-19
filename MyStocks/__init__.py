#!/usr/bin/env python3

import os

from flask import Flask

from MyStocks import auth, db, stock


def create_app():
    app = Flask(__name__)
    app.config['DATABASE'] = os.path.join(app.instance_path, 'mystocks.db')
    app.config['SECRET_KEY'] = os.urandom(16)

    db.init_app(app)

    app.register_blueprint(auth.bp)
    app.register_blueprint(stock.bp)
    app.add_url_rule('/', endpoint='index')

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    return app
