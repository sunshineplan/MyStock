import os

import click
from flask import Flask

import auth
import db
import stock

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


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    if ctx.invoked_subcommand is None:
        ctx.invoke(run)


@cli.command(hidden=True)
@click.confirmation_option()
def init_db():
    db.init_db(app)
    click.echo('Initialized the database.')


@cli.command(short_help='Run Server')
@click.option('--port', '-p', default=80, help='Listening Port')
@click.option('--debug', is_flag=True, hidden=True)
def run(port, debug):
    if debug:
        app.run(host='0.0.0.0', port=port, debug=debug)
    else:
        app.run(host='0.0.0.0', port=port, debug=True)


if __name__ == '__main__':
    cli()
