import os


BASEDIR = os.path.dirname(os.path.dirname(__file__))


class BaseConfig:
    DEBUG = False
    TESTING = False

    SQLALCHEMY_DATABASE_URI = f'sqlite:///{BASEDIR}/dinopass.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class LocalConfig(BaseConfig):
    DEBUG = True


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class ProductionConfig(BaseConfig):
    PROPAGATE_EXCEPTIONS = True
