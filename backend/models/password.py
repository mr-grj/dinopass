from backend.encryption import encrypt, generate_key_derivation
from backend.extensions import db
from backend.models.master_password import MasterPassword


class Password(db.Model):
    __tablename__ = 'password'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    name = db.Column(db.String, nullable=False, unique=True)
    value = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f"<Password(name='{self.name}')>"

    def __str__(self):
        return f"<Password(name='{self.name}', value='***')>"

    def __init__(self, user_id, name, value):
        self.user_id = user_id
        self.name = name
        self.value = self._encrypt_password_value(user_id, value)

    @classmethod
    def create(cls, **kw):
        obj = cls(**kw)
        db.session.add(obj)
        db.session.commit()

    @classmethod
    def _encrypt_password_value(cls, user_id, value):
        master_password_model = MasterPassword.query.filter_by(
            user_id=user_id
        ).first()

        key_derivation = generate_key_derivation(
            master_password_model.salt,
            master_password_model.hash_key
        )

        return encrypt(key_derivation, value)
