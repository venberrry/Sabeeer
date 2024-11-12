import os


class Config:
    SECRET_KEY = os.urandom(32)
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:test@db:5432/TimeManager'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
    SESSION_TYPE = 'filesystem'
    SESSION_FILE_DIR = os.path.join(os.getcwd(), 'flask_session')

    MAIL_SERVER = 'smtp.yandex.ru'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USE_TLS = False
    MAIL_USERNAME = 'elvenbe@yandex.ru'
    MAIL_DEFAULT_SENDER = 'elvenbe@yandex.ru'
    MAIL_PASSWORD = 'nfvevsdjnkgcqbbs'

    GITHUB_CLIENT_ID = "Ov23liG7LjFRNmieePcr"
    GITHUB_CLIENT_SECRET = "3c6b051299d9128baeab70689b4c7d1b2ec02857"

    YANDEX_REDIRECT_URI = "http://127.0.0.1:5000/yandex/callback"
    YANDEX_CLIENT_ID = "d72c6a71c543449688f6c3a281fe59a9"
    YANDEX_CLIENT_SECRET = "ae2841f9225647d08c2af93207966005"
