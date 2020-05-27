from stuff.models import MasterPassword, Password

from sqlalchemy.exc import IntegrityError


class PasswordViewMixin:
    model = None

    def __init__(self, db_session):
        self._db_session = db_session

    def get(self):
        return self.model.get(self._db_session)

    def get_all(self):
        return [
            record.to_dict()
            for record in self.model.get_all(self._db_session)
        ]

    def create(self, **kwargs):
        try:
            record = self.model.create(**kwargs)

            self._db_session.add(record)
            self._db_session.commit()

            return record
        except IntegrityError as integrity_error:
            self._db_session.rollback()
            return {'error': f'{str(integrity_error)}'}

    def purge(self):
        self.model.purge(self._db_session)
        self._db_session.commit()

    def has_records(self):
        return self.model.has_records(self._db_session)


class MasterPasswordView(PasswordViewMixin):
    model = MasterPassword

    @property
    def salt(self):
        master_password = self.model.get(self._db_session)
        return master_password.salt

    @property
    def hash_key(self):
        master_password = self.model.get(self._db_session)
        return master_password.hash_key

    def is_valid(self, hash_key):
        return hash_key == self.hash_key


class PasswordView(PasswordViewMixin):
    model = Password

    @property
    def name(self):
        password = self.model.get(self._db_session)
        return password.name

    @property
    def value(self):
        password = self.model.get(self._db_session)
        return password.value

    def get_by_name(self, name):
        record = self.model.get_by_name(name, self._db_session)
        return [record.to_dict()] if record else []

    def update(self, field, value, field_to_update, new_value):
        try:
            self.model.update_by_field(
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

    def delete(self, name):
        try:
            self.model.delete_by_name(name=name, session=self._db_session)
            self._db_session.commit()
            return f'Successfully deleted record with name={name}.'
        except IntegrityError as integrity_error:
            self._db_session.rollback()
            return f'{str(integrity_error)}'
