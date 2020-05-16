from models import CredentialsTable

from sqlalchemy.exc import IntegrityError


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
        self._db_session.commit()

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