import os
import sys

from dinopass.encryption import generate_hash_key, generate_key_derivation
from dinopass.helpers import pretty_print
from dinopass.models import SESSION
from dinopass.views import MasterPasswordView, PasswordView

import click
import pyperclip


SALT_LENGTH = 16


def set_context_master_password_exists(ctx, master_password_view, password_view):
    master_password = click.prompt(
        'Please enter your master password: ',
        hide_input=True
    )

    hash_key = generate_hash_key(master_password)
    key_derivation = generate_key_derivation(master_password_view.salt, master_password)

    if master_password_view.is_valid(hash_key):
        ctx.obj['key_derivation'] = key_derivation
        ctx.obj['password_view'] = password_view
    else:
        sys.exit('Invalid master password')


def set_context_master_password_does_not_exist(ctx, master_password_view, password_view):
    if click.confirm(f'It looks like you do not have a master password yet. '
                     f'Would you like to create one now?', abort=True):

        master_password = click.prompt(
            'Please enter your master password: ',
            hide_input=True
        )

        salt = os.urandom(SALT_LENGTH)
        hash_key = generate_hash_key(master_password)
        key_derivation = generate_key_derivation(salt, master_password)

        master_password_view.create(salt=salt, hash_key=hash_key)

        ctx.obj['key_derivation'] = key_derivation
        ctx.obj['password_view'] = password_view


@click.group(help="Simple CLI Password Manager for personal use")
@click.pass_context
def main(ctx):
    session = SESSION()

    password_view = PasswordView(session)
    master_password_view = MasterPasswordView(session)

    if master_password_view.has_records():
        set_context_master_password_exists(ctx, master_password_view, password_view)
    else:
        set_context_master_password_does_not_exist(ctx, master_password_view, password_view)


@main.command(help='List all credentials (this command does not have clipboard option).')
@click.pass_context
def all(ctx):
    password_view = ctx.obj['password_view']
    key_derivation = ctx.obj['key_derivation']

    if click.confirm(f'This will display all passwords in clear text. Still want to proceed ?', abort=True):
        data = password_view.get_all(key_derivation)
        pretty_print(title='ALL CREDENTIALS', data=data)


@main.command(help='Purge all credentials.')
@click.pass_context
def purge(ctx):
    if click.confirm(f'Are you sure you want to purge ALL the records?', abort=True):
        password_view = ctx.obj['password_view']
        password_view.purge()
        click.echo('\n\nALL the records have been deleted!\n\n')


@main.command(help='Create a new password with a specific name.')
@click.option('--name', prompt=True, help='Name of the password.')
@click.option('--password', prompt=True, hide_input=True, help='Your new password.')
@click.pass_context
def create(ctx, name: str, password: str):
    password_view = ctx.obj['password_view']
    key_derivation = ctx.obj['key_derivation']

    password_view.create(key_derivation, name, password)


@main.command(help='Get a specific credential by name.')
@click.option('--name', prompt=True, help='Name of the password.')
@click.option('--clipboard/--no-clipboard', default=False, help='Copy password to clipboard')
@click.pass_context
def get(ctx, name: str, clipboard: bool):
    password_view = ctx.obj['password_view']
    key_derivation = ctx.obj['key_derivation']

    data = password_view.get_by_name(key_derivation, name)

    if clipboard:
        if data:
            pyperclip.copy(data[0]['value'])
            click.echo('Password copied to clipboard!')
        else:
            click.echo('No data available.')
    else:
        pretty_print(title=f'CREDENTIAL for {name}', data=data)


@main.command(help='Update a credential field matching a specific condition with a new value.')
@click.option('--field_name_to_lookup_for', prompt=True, help='Name of the field.')
@click.option('--value_to_lookup_for', prompt=True, help='Value of the field.')
@click.option('--field_to_update', prompt=True, help='Name of the field to update.')
@click.option('--new_field_value', prompt=True, help='New value')
@click.pass_context
def update(ctx, field: str, value: str, field_to_update: str, new_value: str):
    password_view = ctx.obj['password_view']
    key_derivation = ctx.obj['key_derivation']

    password_view.update(key_derivation, field, value, field_to_update, new_value)


@main.command(help='Delete a specific credential by name.')
@click.option('--name', prompt=True, help='Name of the password.')
@click.pass_context
def delete(ctx, name: str):
    if click.confirm(f'Are you sure you want to delete {name} record?', abort=True):
        password_view = ctx.obj['password_view']
        password_view.delete(name)
        click.echo(f'The record with name={name} has been deleted!')


def start():
    main(obj={})


if __name__ == '__main__':
    start()
