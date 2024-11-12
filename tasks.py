from datetime import datetime, timedelta
from flask_mail import Message
from extensions import db, mail
from models import Reminder, User, Event
import time

def send_reminder_email(reminder):
    """
    Отправка напоминания по email для конкретного пользователя.
    """
    user = User.query.get(reminder.user_id)
    event = Event.query.get(reminder.event_id)

    if user and event:
        msg = Message(
            subject=f"Напоминание о мероприятии {event.title}",
            recipients=[user.email],
            body=f"Здравствуйте, {user.name}!\n\n"
                 f"Это напоминание о мероприятии '{event.title}', которое состоится "
                 f"{event.date.strftime('%d.%m.%Y %H:%M')} по адресу {event.location}.\n\n"
                 "С уважением, команда вашего приложения."
        )
        mail.send(msg)
        reminder.is_sent = True
        db.session.commit()
        print("Напоминаниеи ушло на почту", user.email)

def check_and_send_reminders(app, interval=86400):
    """
    Проверяет и отправляет напоминания за 2 дня до события.
    """
    while True:
        with app.app_context():
            now = datetime.utcnow()
            reminders = Reminder.query.filter(
                Reminder.reminder_time <= now, Reminder.is_sent == False
            ).all()

            for reminder in reminders:
                send_reminder_email(reminder)

        # Пауза перед следующим запуском (каждый день в 00:01или через полминуты)
        time.sleep(interval)
