from contextlib import contextmanager

from flask import Flask, request

from backend import api
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
    register_validation_api()
    register_blueprints(app)

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


def register_validation_api():
    api.resources.password_api.add_resource(
        api.resources.MasterPassword,
        '/master_password'
    )
    api.resources.password_api.add_resource(
        api.resources.Passwords,
        '/passwords',
    )


def register_blueprints(app):
    app.register_blueprint(api.resources.blueprint, url_prefix='/api/')


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