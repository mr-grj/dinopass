from contextlib import contextmanager

from flask import Flask
from flask_cors import CORS

from backend import api, models
from backend.extensions import db, migrate


def create_app():
    app = Flask(
        __name__,
        template_folder='./frontend/templates/',
        static_folder='./frontend/static/'
    )
    app.url_map.strict_slashes = False
    app.db_session_scope = session_scope

    get_config(app)
    register_extensions(app)
    register_api()
    register_blueprints(app)
    register_shellcontext(app)

    CORS(app)

    return app


def get_config(app):
    environments = (
        'production',
        'development',
        'local',
    )

    flask_environment = app.config['ENV']

    for environment in environments:
        if flask_environment == environment:
            app.config.from_object(f'backend.config.{environment.title()}Config')
            return
    else:
        raise ValueError(
            f'It looks like you have wrongly configured your settings. Check '
            f'the .env file! Your `FLASK_ENV` MUST match one of the following: '
            f'{", ".join(environments)} (most probably `local`)'
        )


def register_extensions(app):
    db.init_app(app)
    migrate.init_app(app, db)


def register_api():
    api.passwords.passwords_api.add_resource(
        api.passwords.PasswordsListApi,
        '/passwords',
    )
    api.users.users_api.add_resource(
        api.users.UsersListApi,
        '/users'
    )
    api.users.users_api.add_resource(
        api.users.UserListApi,
        '/user/<int:id_>'
    )


def register_blueprints(app):
    app.register_blueprint(api.passwords.passwords_blueprint, url_prefix='/api/')
    app.register_blueprint(api.users.users_blueprint, url_prefix='/api/')


@contextmanager
def session_scope():
    """
    Provide a transactional scope around a series of operations.
    """

    try:
        yield db.session
        db.session.commit()
    except Exception as e:
        print(f'Something went wrong here: {str(e)}. rolling back.')
        db.session.rollback()
        raise
    finally:
        db.session.close()


def register_shellcontext(app):
    """Register shell context objects."""

    def shell_context():
        """Shell context objects."""
        return dict(
            app=app,
            db=db,
            User=models.user.User,
            Password=models.password.Password,
            MasterPassword=models.master_password.MasterPassword,
        )

    app.shell_context_processor(shell_context)
