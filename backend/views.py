from backend.encryption import encrypt, decrypt
from backend.models import MasterPassword, Password


class PasswordViewMixin:
    model = None

    def __init__(self, db_session):
        if not self.model:
            raise NotImplementedError('Please specify a model!')

        self._db_session = db_session

    def get(self):
        return self.model.get(self._db_session)

    def purge(self):
        self.model.purge(self._db_session)
        self._db_session.commit()

    def has_records(self):
        return self.model.has_records(self._db_session)


class MasterPasswordView(PasswordViewMixin):
    model = MasterPassword

    @property
    def salt(self):
        return self.model.get(self._db_session).salt

    @property
    def hash_key(self):
        return self.model.get(self._db_session).hash_key

    def create(self, **kwargs):
        record = self.model.create(**kwargs)

        self._db_session.add(record)
        self._db_session.commit()

    def is_valid(self, hash_key):
        return hash_key == self.hash_key


class PasswordView(PasswordViewMixin):
    model = Password

    @property
    def name(self):
        return self.model.get(self._db_session).name

    @property
    def value(self):
        return self.model.get(self._db_session).value

    def create(self, key, name, value):
        encrypted_value = encrypt(key, value)
        record = self.model.create(name=name, value=encrypted_value)

        self._db_session.add(record)
        self._db_session.commit()

    def get_all(self, key):
        records = []
        for record in self.model.get_all(self._db_session):
            record.value = decrypt(key, record.value)
            records.append(record.to_dict())
        return records

    def get_by_name(self, key, name):
        record = self.model.get_by_name(name, self._db_session)
        if record:
            record.value = decrypt(key, record.value)
            return [record.to_dict()]
        return []

    def update(self, key, field, value, field_to_update, new_value):
        if field_to_update == 'value':
            new_value = encrypt(key, new_value)

        self.model.update_by_field(
            field=field,
            value=value,
            field_to_update=field_to_update,
            new_value=new_value,
            session=self._db_session
        )
        self._db_session.commit()

        print(f'Updated record with name = {field_to_update}')

    def delete(self, name):
        self.model.delete_by_name(name=name, session=self._db_session)
        self._db_session.commit()
        print(f'Deleted record with name = {name}')
