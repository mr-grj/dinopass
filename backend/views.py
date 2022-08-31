from sqlalchemy.orm import Session

from backend.helpers import encrypt, decrypt
from backend.models.master_password import MasterPasswordModel
from backend.models.password import PasswordModel


class MasterPasswordView:
    def __init__(self, db_session: Session) -> None:
        self._db_session = db_session

    @property
    def salt(self):
        return MasterPasswordModel.get(self._db_session).salt

    @property
    def hash_key(self):
        return MasterPasswordModel.get(self._db_session).hash_key

    def get(self):
        return MasterPasswordModel.get(self._db_session)

    def purge(self) -> None:
        MasterPasswordModel.purge(self._db_session)
        self._db_session.commit()

    def has_records(self):
        return MasterPasswordModel.has_records(self._db_session)

    def create(self, **kwargs):
        record = MasterPasswordModel.create(**kwargs)

        self._db_session.add(record)
        self._db_session.commit()

    def is_valid(self, hash_key: str) -> bool:
        return hash_key == self.hash_key


class PasswordView:
    def __init__(self, db_session: Session) -> None:
        self._db_session = db_session

    def get(self):
        return PasswordModel.get(self._db_session)

    def purge(self) -> None:
        PasswordModel.purge(self._db_session)
        self._db_session.commit()

    def has_records(self):
        return PasswordModel.has_records(self._db_session)

    @property
    def password_name(self):
        return PasswordModel.get(self._db_session).password_name

    @property
    def password_value(self):
        return PasswordModel.get(self._db_session).password_value

    def create(self, key, name, value, description):
        encrypted_value = encrypt(key, value)
        record = PasswordModel.create(
            password_name=name,
            password_value=encrypted_value,
            description=description
        )

        self._db_session.add(record)
        self._db_session.commit()

    def get_all(self, key):
        records = []
        for record in PasswordModel.get_all(self._db_session):
            decrypted_value = decrypt(key, record.password_value)
            if not decrypted_value:
                return False

            record.password_value = decrypted_value
            records.append(record.to_dict())
        return records

    def get_by_name(self, key, name):
        record = PasswordModel.get_by_name(name, self._db_session)
        if record:
            record.password_value = decrypt(key, record.password_value)
            return [record.to_dict()]
        return []

    def update_name(self, current_password_name, new_password_name):
        PasswordModel.update_name(
            current_password_name,
            new_password_name,
            session=self._db_session
        )
        self._db_session.commit()
        print(
            f'Updated password name from {current_password_name} '
            f'to {new_password_name}.'
        )

    def update_password(self, key, name, new_password_value):
        new_password_value = encrypt(key, new_password_value)

        PasswordModel.update_password(
            name,
            new_password_value,
            session=self._db_session
        )
        self._db_session.commit()
        print(f'Successfully updated password value')

    def delete(self, name):
        PasswordModel.delete_by_name(name=name, session=self._db_session)
        self._db_session.commit()
        print(f'Deleted record with password_name = {name}')
