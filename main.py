from flask import Flask
from config import Config
from flask_session import Session
from extensions import db, mail, socketio
from socketchat import Chat
from setup import initialize_roles
from threading import Thread
from tasks import check_and_send_reminders

# Флаг для проверки, был ли поток запущен
reminder_thread_started = False

app = Flask(__name__)
app.config.from_object(Config)
Session(app)
db.init_app(app)
mail.init_app(app)
socketio.init_app(app)
socketio.on_namespace(Chat('/chat'))

from views import *
from utils import *
from apishki import *

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        initialize_roles(app)
        # чтобы не было дублирований тредов от некорректных запусков
        if not reminder_thread_started:
            # # Поток для ежедневной проверки (тик каждые 24 часа)
            # reminder_thread_real = Thread(target=check_and_send_reminders, args=(app, 86400))
            # reminder_thread_real.daemon = True
            # reminder_thread_real.start()

            # Поток для тестирования (тик каждую минуту)
            reminder_thread_test = Thread(target=check_and_send_reminders, args=(app, 60))
            reminder_thread_test.daemon = True
            reminder_thread_test.start()


    socketio.run(app, host="0.0.0.0", port=5000,debug=True, allow_unsafe_werkzeug=True)