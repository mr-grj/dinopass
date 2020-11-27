from backend.encryption import generate_hash_key
from backend.extensions import db


class MasterPassword(db.Model):
    __tablename__ = 'master_password'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    salt = db.Column(db.String, nullable=False)
    hash_key = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f"<MasterPassword(user_id={self.user_id})>"

    def __str__(self):
        return f"<MasterPassword(user_id={self.user_id})>"

    def __init__(self, salt, hash_key):
        self.salt = salt
        self.hash_key = hash_key

    @classmethod
    def create(cls, **kw):
        obj = cls(**kw)
        db.session.add(obj)
        db.session.commit()
        return obj

    @classmethod
    def is_valid(cls, user_id, master_password):
        return cls._get_hash_key(user_id) == generate_hash_key(master_password)

    @classmethod
    def _get_hash_key(cls, user_id):
        master_password_model = cls.query.filter_by(user_id=user_id).first()
        return master_password_model.hash_key if master_password_model else None
