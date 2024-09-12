import click
import os


@click.group()
def cli():
    pass


@cli.command()
def init():
    os.system('flask db init')


@cli.command()
@click.option('--message', default='migration', help='Migration description.')
def migrate(message):
    os.system(f'flask db migrate -m "{message}"')


@cli.command()
def upgrade():
    os.system('flask db upgrade')


@cli.command()
@click.option('--revision', default='-1', help='Specify the revision to downgrade to (default is one step back).')
def downgrade(revision):
    os.system(f'flask db downgrade {revision}')


if __name__ == '__main__':
    cli()
