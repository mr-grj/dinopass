from stuff.models import CredentialsTable

from sqlalchemy.exc import IntegrityError


class Credential:
    def __init__(self, db_session):
        self._db_session = db_session

    def create(self, name, password):
        """Create a password.

        Arguments:
            name (str): Name of the password.
            password (str): Password value.

        Returns: str
        """
        try:
            record = CredentialsTable.create(name=name, password=password)

            self._db_session.add(record)
            self._db_session.commit()

            return record
        except IntegrityError as integrity_error:
            self._db_session.rollback()
            return {'error': f'{str(integrity_error)}'}

            # if 'UNIQUE constraint failed' in str(integrity_error):
            #     return f'There is already a record with name={name}'
            #
            # return f'{str(integrity_error)}'

    def get_all(self):
        return [
            credential.to_dict()
            for credential in CredentialsTable.get_all(self._db_session)
        ]

    def get(self, name):
        """Retrieve a credential record with a specific name.

        Arguments:
            name (str): Name to filter by.

        Returns:
            str if no data is found, dict otherwise
        """
        record = CredentialsTable.get_by_name(name=name, session=self._db_session)
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

    def delete(self, name):
        """Delete a credential record with a specific name.

        Arguments:
            name (str): Name to filter by.

        Returns: str
        """

        try:
            CredentialsTable.delete_by_name(name=name, session=self._db_session)
            self._db_session.commit()
            return f'Successfully deleted record with name={name}.'
        except IntegrityError as integrity_error:
            self._db_session.rollback()
            return f'{str(integrity_error)}'
