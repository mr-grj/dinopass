from hashlib import new
from dinopass.encryption import encrypt, decrypt
from dinopass.models import MasterPassword, Password


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
    def password_name(self):
        return self.model.get(self._db_session).password_name

    @property
    def password_value(self):
        return self.model.get(self._db_session).password_value

    def create(self, key, name, value, description):
        encrypted_value = encrypt(key, value)
        record = self.model.create(
            password_name=name, 
            password_value=encrypted_value,
            description=description
        )

        self._db_session.add(record)
        self._db_session.commit()

    def get_all(self, key):
        records = []
        for record in self.model.get_all(self._db_session):
            record.password_value = decrypt(key, record.password_value)
            records.append(record.to_dict())
        return records

    def get_by_name(self, key, name):
        record = self.model.get_by_name(name, self._db_session)
        if record:
            record.password_value = decrypt(key, record.password_value)
            return [record.to_dict()]
        return []

    def update_name(self, current_password_name, new_password_name):
        self.model.update_name(
            current_password_name, 
            new_password_name,
            session=self._db_session
        )
        self._db_session.commit()
        print(f'Updated password name from {current_password_name} to {new_password_name}')

    def update_password(self, key, name, new_password_value):
        new_password_value = encrypt(key, new_password_value)

        self.model.update_password(
            name,
            new_password_value,
            session=self._db_session
        )
        self._db_session.commit()
        print(f'Successfully updated password value')

    def delete(self, name):
        self.model.delete_by_name(password_name=name, session=self._db_session)
        self._db_session.commit()
        print(f'Deleted record with password_name = {name}')
