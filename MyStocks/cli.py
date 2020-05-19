#!/usr/bin/env python3

import click

from MyStocks import create_app, db

app = create_app()


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
    app.run(host='0.0.0.0', port=port, debug=debug)


def main():
    cli()


if __name__ == '__main__':
    main()
