import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_COMMIT_ON_TEARDOWN = os.environ.get('SQLALCHEMY_COMMIT_ON_TEARDOWN')
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = os.environ.get('MAIL_PORT')
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS')
    MAIL_SUBJECT_PREFIX = os.environ.get('FLASKY_MAIL_SUBJECT_PREFIX')
    MAIL_SENDER = os.environ.get('FLASKY_MAIL_SENDER')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://root:@localhost/bluecollr'


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://root@localhost/bluecollr'


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'postgresql://root@localhost/bluecollr'


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}