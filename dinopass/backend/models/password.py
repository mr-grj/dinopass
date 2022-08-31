from sqlalchemy import Column, String

from backend.models.base import PasswordBaseModel


class PasswordModel(PasswordBaseModel):
    __tablename__ = 'passwords'

    password_name = Column(String, nullable=False, unique=True)
    password_value = Column(String, nullable=False)
    description = Column(String, nullable=True)

    def __repr__(self):
        return f"<Password(password_name='{self.password_name}')>"

    def __str__(self):
        return f"<Password(password_name='{self.password_name}', password_value='***')>"

    def __init__(self, password_name, password_value, description):
        self.password_name = password_name
        self.password_value = password_value
        self.description = description

    @classmethod
    def get_all(cls, session):
        return session.query(cls).all()

    @classmethod
    def update_name(cls, current_name, new_name, session):
        if not session.query(cls).filter_by(password_name=current_name).first():
            raise ValueError(f"No password with name={current_name}")
        return (
            session
                .query(cls)
                .filter_by(**{"password_name": current_name})
                .update({"password_name": new_name})
        )

    @classmethod
    def update_password(cls, name, new_password, session):
        if not session.query(cls).filter_by(password_name=name).first():
            raise ValueError(f"No password with name={name}")

        return (
            session
                .query(cls)
                .filter_by(**{"password_name": name})
                .update({"password_value": new_password})
        )

    @classmethod
    def delete_by_name(cls, name, session):
        return session.query(cls).filter_by(password_name=name).delete()

    def to_dict(self):
        record = vars(self)
        record.pop('_sa_instance_state')
        record.pop('id')
        return record


password_table = PasswordModel.__table__
