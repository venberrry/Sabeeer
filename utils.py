from flask_mail import Message
from flask import current_app, session
from main import mail
import random

def generate_six_digit_code():
    """
    Генерирует случайный шестизначный код
    """
    return str(random.randint(100000, 999999))

def send_confirmation_code(email):
    """
    Отправляет код подтверждения для завершения регистрации
    Внутри генерируется шестизначный код и отправляется на указанный email
    """
    code = generate_six_digit_code()
    msg = Message('Код подтверждения регистрации', recipients=[email])
    msg.body = f"Ваш код подтверждения: {code}"
    msg.sender = current_app.config['MAIL_DEFAULT_SENDER']
    mail.send(msg)
    session['confirmation_code'] = code
    return code

def send_password_reset_code(email):
    """
    Отправляет код для восстановления пароля
    Внутри генерируется шестизначный код и отправляется на указанный email
    """
    code = generate_six_digit_code()
    msg = Message('Код для восстановления пароля', recipients=[email])
    msg.body = f"Ваш код для восстановления пароля: {code}"
    msg.sender = current_app.config['MAIL_DEFAULT_SENDER']
    mail.send(msg)
    session['confirmation_code'] = code
    return code
