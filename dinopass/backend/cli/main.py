import os
import sys

import click
import pyperclip

from backend.config.cli_settings import SESSION
from backend.helpers import (
    generate_hash_key,
    generate_key_derivation,
    pretty_print
)
from backend.views import MasterPasswordView, PasswordView

SALT_LENGTH = 16


def set_context_master_password_exists(ctx, master_password_view, password_view):
    master_password = click.prompt(
        'Please enter your master password',
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
            'Please enter your master password',
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
    if click.confirm(f'This will DELETE ALL passwords. Still want to proceed ?', abort=True):
        password_view = ctx.obj['password_view']
        password_view.purge()


@main.command(help='Create a new password with a specific name.')
@click.option('--name', prompt=True, help='Name of the password.')
@click.option('--password', prompt=True, hide_input=True, help='Your new password.')
@click.option('--description', prompt=True, default="", help='Description of password.')
@click.pass_context
def create(ctx, name: str, password: str, description: str):
    password_view = ctx.obj['password_view']
    key_derivation = ctx.obj['key_derivation']

    try:
        password_view.create(key_derivation, name, password, description)
    except Exception as integrity_error:
        if 'UNIQUE constraint failed' in str(integrity_error):
            click.echo(f'You have already created a record with this name.')
        else:
            click.echo(str(integrity_error))

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


@main.command(help='Update password name.')
@click.option('--current_name', prompt=True, help='Current name of a specific password.')
@click.option('--new_name', prompt=True, help='New name of a specific password.')
@click.pass_context
def update_name(ctx, current_name: str, new_name: str):
    password_view = ctx.obj['password_view']
    password_view.update_name(current_name, new_name)


@main.command(help='Update password value.')
@click.option('--name', prompt=True, help='Name of a specific password.')
@click.option('--new_value', prompt=True, hide_input=True, help='New value of a specific password.')
@click.pass_context
def update_password(ctx, name: str, new_value: str):
    password_view = ctx.obj['password_view']
    key_derivation = ctx.obj['key_derivation']

    password_view.update_password(key_derivation, name, new_value)


@main.command(help='Delete a specific credential by name.')
@click.option('--name', prompt=True, help='Name of the password.')
@click.pass_context
def delete(ctx, name: str):
    if click.confirm(f'Are you sure you want to delete {name} record?', abort=True):
        password_view = ctx.obj['password_view']
        password_view.delete(name)


@main.command(help='Create backup of db and send to email.')
@click.option('--master_password', prompt=True, hide_input=True, help='Your master password (again, yes).')
@click.pass_context
def backup_and_email(ctx, master_password):
    password_view = ctx.obj['password_view']
    if click.confirm(f'Are you sure you want to backup db & send via email?', abort=True):
        password_view.backup_and_send(master_password)


def start():
    main(obj={})


if __name__ == '__main__':
    start()
