from stuff.credential import Credential
from stuff.helpers import pp
from stuff.models import SESSION

import click


@click.group(help="Simple CLI Password manager for personal use")
@click.pass_context
def main(ctx):
    session = SESSION()
    credential = Credential(session)
    ctx.obj['credential'] = credential


@main.command(help='List all credentials.')
@click.pass_context
def all(ctx):
    credential = ctx.obj['credential']
    data = credential.get_all()
    if not data:
        print('There are no credentials stored yet.')
    pp(title='ALL CREDENTIALS', data=data)


@main.command(help='Purge all credentials.')
@click.pass_context
def purge(ctx):
    credential = ctx.obj['credential']
    if click.confirm(f'Are you sure you want to purge ALL the records?', abort=True):
        credential.purge()
        click.echo('ALL the records have been deleted!')


@main.command(help='Create a new credential with a specific name and password.')
@click.option('--name', prompt=True, help='Name of the password.')
@click.option('--password', prompt=True, hide_input=True, help='Your new password.')
@click.pass_context
def create(ctx, name: str, password: str):
    credential = ctx.obj['credential']
    credential.create(name, password)


@main.command(help='Get a specific credential by name.')
@click.option('--name', prompt=True, help='Name of the password.')
@click.pass_context
def get(ctx, name: str):
    credential = ctx.obj['credential']
    data = credential.get(name)
    if not data:
        print(f'There is no record with name={name}!')
        return
    pp(title=f'CREDENTIAL for {name}', data=data)


@main.command(help='Update a credential field matching a specific '
                   'condition with a new value.')
@click.option('--field', prompt=True, help='Name of the field.')
@click.option('--value', prompt=True, help='Value of the field.')
@click.option('--field_to_update', prompt=True, help='Name of the field to update.')
@click.option('--new_value', prompt=True, help='New value')
@click.pass_context
def update(ctx, field: str, value: str, field_to_update: str, new_value: str):
    credential = ctx.obj['credential']
    credential.update(field, value, field_to_update, new_value)


@main.command(help='Delete a specific credential by name.')
@click.option('--name', prompt=True, help='Name of the password.')
@click.pass_context
def delete(ctx, name: str):
    credential = ctx.obj['credential']
    if click.confirm(f'Are you sure you want to delete {name} record?', abort=True):
        credential.delete(name)
        click.echo(f'The record with name={name} has been deleted!')


def start():
    main(obj={})


if __name__ == '__main__':
    start()
