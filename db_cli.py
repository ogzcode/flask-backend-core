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


@cli.command()
@click.option('--username', required=True, help='Superadmin username')
@click.option('--email', required=True, help='Superadmin email')
@click.option('--password', required=True, help='Superadmin password', hide_input=True)
def create_superadmin(username, email, password):
    from app import app, db
    from app.models import User
    
    with app.app_context():
        if User.query.filter_by(is_superadmin=True).first():
            click.echo("⛔ System already has a superadmin user")
            return
            
        try:
            new_user = User(
                username=username,
                email=email,
                is_superadmin=True,
            )
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            click.echo(f"✅ {username} created as superadmin")
        except Exception as e:
            db.session.rollback()
            click.echo(f"❌ Error: {str(e)}")


if __name__ == '__main__':
    cli()
