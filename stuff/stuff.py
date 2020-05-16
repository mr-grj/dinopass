import sys

from models import Base, CredentialsTable
from stuff.settings import ENGINE, session

from psycopg2 import OperationalError
from rich.console import Console
from rich.table import Table
from sqlalchemy.exc import IntegrityError

from argparse import ArgumentParser


try:
    Base.metadata.create_all(ENGINE)
except OperationalError as operational_error:
    sys.exit(f'Error when connecting to DB: {operational_error}. '
             f'Please make sure you have correctly set up your DB!')


class Credential:
    def __init__(self, db_session):
        self._db_session = db_session

    def create(self, name, group, password):
        """Create a password.

        Arguments:
            name (str): Name of the password.
            group (str): Group of the password.
            password (str): Password value.

        Returns:
            str
        """

        try:
            record = CredentialsTable.create(
                name=name,
                group=group,
                password=password
            )
            self._db_session.add(record)
            self._db_session.commit()
            return f'Successfully added record with name={name}.'
        except IntegrityError as integrity_error:
            self._db_session.rollback()

            if 'duplicate key value violates unique constraint' in str(integrity_error):
                return 'Password should be unique per group!'

            return f'{str(integrity_error)}'

    def get_all(self):
        return [
            credential.to_dict()
            for credential in CredentialsTable.get_all(self._db_session)
        ]

    def get(self, field, value):
        """Retrieve a credential record with a specific field value.

        Arguments:
            field (str): Name of a table column.
            value (str): Value to filter by.

        Returns:
            str if no data is found, dict otherwise
        """

        if not field:
            raise ValueError('You should provide a field name.')

        if not isinstance(field, str):
            raise ValueError('Field should be a string.')

        record = CredentialsTable.get_by_field(
            field=field,
            value=value,
            session=self._db_session
        )

        if not record:
            return

        return [record.to_dict()] if record else []

    def update(self, field, value, field_to_update, new_value):
        """Update a record with a specific value.

        Arguments:
            field (str): Name of a table column.
            value (str): Value to filter by.
            field_to_update (str): The column that needs updating.
            new_value (str): The new value.

        Returns:
            str
        """

        try:
            CredentialsTable.update_by_field(
                field=field,
                value=value,
                field_to_update=field_to_update,
                new_value=new_value,
                session=self._db_session
            )
            self._db_session.commit()
            return f'Successfully updated record matching {field}={value} ' \
                   f'with {field_to_update}={new_value}.'
        except IntegrityError as integrity_error:
            self._db_session.rollback()
            return f'{str(integrity_error)}'

    def purge(self):
        CredentialsTable.purge(self._db_session)
        session.commit()

    def delete(self, field, value):
        """Delete a credential record with a specific field value.

        Arguments:
            field (str): Name of a table column.
            value (str): Value to filter by.

        Returns:
            str
        """

        if not field:
            raise ValueError('You should provide a field name.')

        if not isinstance(field, str):
            raise ValueError('Field should be a string.')

        try:
            CredentialsTable.delete_by_field(
                field=field,
                value=value,
                session=self._db_session
            )
            self._db_session.commit()
            return f'Successfully deleted record with {field}={value}.'
        except IntegrityError as integrity_error:
            self._db_session.rollback()
            return f'{str(integrity_error)}'


def pp(title, data):
    title = f'[bold red][u]{title}[/u][/bold red]'
    table = Table(title=title, show_lines=True)

    console = Console()

    table.add_column("GROUP", justify="center", style="cyan", no_wrap=True)
    table.add_column("NAME", justify="center", style="magenta", no_wrap=True)
    table.add_column("PASSWORD", justify="center", style="bold green", no_wrap=True)

    for item in data:
        table.add_row(item['group'], item['name'], item['password'])

    console.print(table)


def command_line_parser():
    parser = ArgumentParser(
        description='Simple CLI Password manager for personal use',
        epilog='All the arguments are mutually exclusive'
    )
    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument(
        '-a', '--all',
        action='store_true',
        help='List all credentials'
    )
    group.add_argument(
        '-p', '--purge',
        action='store_true',
        help='Purge all credentials'
    )

    group.add_argument(
        '-c', '--create',
        nargs=3,
        metavar=('<name>', '<group>', '<password>'),
        help='Create a new credential with a specific name, in a specific group, with a specific password',
    )
    group.add_argument(
        '-g', '--get',
        nargs=2,
        metavar=('<field>', '<value>'),
        help='Get a specific credential by name/group value'
    )
    group.add_argument(
        '-u', '--update',
        nargs=4,
        metavar=('<field>', '<value>', '<field_to_update>', '<new_value>'),
        help='Update a credential field matching a specific condition with a new value'
    )
    group.add_argument(
        '-d', '--delete',
        nargs=2,
        metavar=('<field>', '<value>'),
        help='Delete a specific credential by name/group value'
    )

    return parser


def main():
    credential = Credential(session)
    args = command_line_parser().parse_args()

    if args.all:
        data = credential.get_all()
        if not data:
            print('There are no credentials stored yet!')
        pp(title='ALL CREDENTIALS', data=data)

    elif args.purge:
        credential.purge()

    elif args.create:
        name, group, password = args.create
        credential.create(name, group, password)

    elif args.get:
        field, value = args.get
        data = credential.get(field, value)
        if not data:
            print(f'There is no record with {field}={value}!')
            return
        pp(title=f'CREDENTIAL for {value}', data=data)

    elif args.update:
        field, value, field_to_update, new_value = args.update
        credential.update(field, value, field_to_update, new_value)

    elif args.delete:
        field, value = args.delete
        credential.delete(field, value)

    else:
        raise ValueError('Invalid option')


if __name__ == '__main__':
    main()
