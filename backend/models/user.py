from backend.extensions import db


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True)

    master_password = db.relationship(
        'MasterPassword',
        uselist=False,
        backref='user'
    )
    passwords = db.relationship(
        'Password',
        backref='password',
        lazy='dynamic'
    )

    @classmethod
    def create(cls, **kw):
        obj = cls(**kw)
        db.session.add(obj)
        db.session.commit()

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username
        }
