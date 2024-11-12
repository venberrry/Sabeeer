from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, DateTimeField, FileField
from wtforms.validators import DataRequired, Email, EqualTo, Length

class RegistrationForm(FlaskForm):
    """
    Форма регистрации нового пользователя
    Включает поля для имени, email и пароля, с проверкой совпадения паролей
    """
    name = StringField('Имя', validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Подтвердите пароль', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Зарегистрироваться')

class LoginForm(FlaskForm):
    """
    Форма для входа пользователя
    Включает поля для email и пароля
    """
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')

class ResetPasswordForm(FlaskForm):
    """
    Форма для запроса восстановления пароля
    Включает поле для email пользователя
    """
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Отправить код для восстановления пароля')

class VerificationForm(FlaskForm):
    """
    Форма для проверки кода подтверждения, отправленного на email
    Включает поле для ввода кода подтверждения
    """
    code = StringField('Код подтверждения', validators=[DataRequired(), Length(min=6, max=6)])
    submit = SubmitField('Подтвердить')

class ChangePasswordForm(FlaskForm):
    """
    Форма для смены пароля пользователя после подтверждения кода
    Включает поля для нового пароля и подтверждения
    """
    password = PasswordField('Новый пароль', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Подтвердите новый пароль', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Изменить пароль')

class EventForm(FlaskForm):
    """
    Форма для создания и редактирования мероприятия
    Включает поля для названия, описания, даты и места
    """
    title = StringField('Название', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Описание', validators=[Length(max=500)])
    date = DateTimeField('Дата и время', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    location = StringField('Место', validators=[DataRequired(), Length(max=150)])
    submit = SubmitField('Сохранить мероприятие')

class CommentForm(FlaskForm):
    content = TextAreaField('Комментарий', validators=[DataRequired(), Length(max=300)])
    submit = SubmitField('Отправить')

class RoomForm(FlaskForm):
    """
    Форма для создания и редактирования комнаты
    Включает поля для названия, идентификатора, пароля и описания
    """
    name = StringField('Название комнаты', validators=[DataRequired(), Length(max=20)])
    identifier = StringField('Идентификатор комнаты', validators=[DataRequired(), Length(max=50)])
    password = PasswordField('Пароль для комнаты', validators=[DataRequired(), Length(min=6)])
    description = TextAreaField('Описание комнаты', validators=[Length(max=20)])
    submit = SubmitField('Создать комнату')
