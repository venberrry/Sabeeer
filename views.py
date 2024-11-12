import requests
from main import app
from main import socketio
from flask import render_template, request, redirect, url_for, flash, session, jsonify

from models import db, User, Room, Event, UserRole, Reminder, Note, Role
from forms import RegistrationForm, LoginForm, ResetPasswordForm, VerificationForm, EventForm, RoomForm, CommentForm, \
    ChangePasswordForm
from flask_socketio import emit, join_room, leave_room

from werkzeug.security import generate_password_hash, check_password_hash
from utils import send_confirmation_code, send_password_reset_code

from sqlalchemy.exc import IntegrityError

from datetime import timedelta, datetime

GITHUB_CLIENT_ID = app.config['GITHUB_CLIENT_ID']
GITHUB_CLIENT_SECRET = app.config['GITHUB_CLIENT_SECRET']



# ---------------------- Блок аутентификации ----------------------

@app.route("/", methods=["GET"])
def home():
    """
    Хоум
    перенаправление на дашборд, если пользователь уже авторизован
    """
    if 'user_id' in session:
        return redirect(url_for("dashboard"))
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """
    Регистрация нового пользователя
    проверяет существование email в базе
    отправляет код подтверждения на email после регистрации
    """
    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash("Пользователь с таким email уже существует", "danger")
            return redirect(url_for("register"))

        # сохраняем поля пользователя во временной сессии
        session['temp_user'] = {
            'name': form.name.data,
            'email': form.email.data,
            'password': generate_password_hash(form.password.data)
        }
        # отправка кода подтверждения на email
        send_confirmation_code(form.email.data)
        flash("Проверьте свою почту для подтверждения регистрации", "info")
        return redirect(url_for("verify_registration"))
    return render_template("register.html", form=form)


@app.route("/verify", methods=["GET", "POST"])
def verify_registration():
    """
    Проверка кода подтверждения для завершения регистрации
    При успешной проверке завершает регистрацию и создает нового пользователя
    """
    form = VerificationForm()
    if form.validate_on_submit():
        if form.code.data == session.get('confirmation_code'):
            # данные из временной сессии пользователя в бд
            temp_user = session.get('temp_user')
            if temp_user:
                new_user = User(
                    name=temp_user['name'],
                    email=temp_user['email'],
                    password=temp_user['password']
                )
                db.session.add(new_user)
                db.session.commit()
                session.pop('temp_user', None)
                flash("Регистрация завершена. Теперь вы можете войти", "success")
                session.pop('confirmation_code', None)
                return redirect(url_for("login"))
            else:
                flash("Ошибка при регистрации. Пожалуйста, попробуйте снова", "danger")
                return redirect(url_for("register"))
        else:
            flash("Неверный код подтверждения. Пожалуйста, попробуйте снова", "danger")
    return render_template("verify.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Авторизация пользователя, проверка email и пароля
    При успешном входе сохраняет ID пользователя в сессии
    """
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            session['user_id'] = user.id
            return redirect(url_for("dashboard"))
        flash("Неверный email или пароль", "danger")
    return render_template("login.html", form=form)


@app.route("/logout")
def logout():
    """
    логаут пользователя, удаление данных из сессии
    """
    session.pop('user_id', None)
    return redirect(url_for("home"))



# ---------------------- Блок профиля и восстановления пароля ----------------------


@app.route("/profile", methods=["GET"])
def profile():
    """
    Профиль
    Имя, емейл, смена пароля
    """
    if 'user_id' not in session:
        return redirect(url_for("login"))
    # получаем пользователя из базы данных по ID из сессии
    user = User.query.get(session['user_id'])

    if not user:
        flash("Пользователь не найден", "danger")
        return redirect(url_for("home"))

    return render_template("profile.html", user=user)


@app.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    """
    Восстановление пароля
    отправка кода подтверждения на email пользователя, если email найден в базе
    """
    if 'user_id' not in session:
        return redirect(url_for("login"))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            # отправка кода подтверждения на email
            send_password_reset_code(user.email)
            flash("Проверьте свою почту для восстановления пароля", "info")
            return redirect(url_for("verify_reset"))
        flash("Пользователь с таким email не найден", "danger")
    return render_template("reset_password.html", form=form)


@app.route("/verify-reset", methods=["GET", "POST"])
def verify_reset():
    """
    Проверка кода подтверждения для восстановления пароля
    Перенаправляет на страницу смены пароля после успешной проверки
    """
    form = VerificationForm()
    if form.validate_on_submit():
        flash("Код подтверждения принят. Смените пароль:", "success")
        return redirect(url_for("change_password"))
    return render_template("verify_reset_passw.html", form=form)


@app.route("/change-password", methods=["GET", "POST"])
def change_password():
    """
    Установка нового пароля после успешного подтверждения кода
    """
    if 'user_id' not in session:
        return redirect(url_for("login"))

    form = ChangePasswordForm()
    if form.validate_on_submit():
        user = User.query.get(session['user_id'])
        # обновление пароля пользователя
        user.password = generate_password_hash(form.password.data)
        db.session.commit()
        return redirect(url_for("profile"))
    else:
        print("Ошибки валидации:", form.errors)

    return render_template("change_password.html", form=form)


@app.route("/request-password-reset", methods=["POST"])
def request_password_reset():
    """
    Отправка кода подтверждения для восстановления пароля на email пользователя
    Доступно только для авторизованных пользователей
    """
    if 'user_id' not in session:
        return redirect(url_for("login"))

    user = User.query.get(session['user_id'])
    send_password_reset_code(user.email)
    return redirect(url_for("verify_reset"))


# ---------------------- Для комнат ----------------------

@app.route("/dashboard")
def dashboard():
    """
    Отображает список созданных и присоединенных комнат
    """
    if 'user_id' not in session:
        return redirect(url_for("login"))

    user_id = session['user_id']

    # получение комнат, которые пользователь создал
    created_rooms = Room.query.filter_by(creator_id=user_id).all()

    # получение комнат, к которым пользователь присоединился, исключая созданные им
    created_room_ids = {room.id for room in created_rooms}
    joined_room_ids = [
        room_id for room_id, in db.session.query(UserRole.room_id).filter_by(user_id=user_id).all()
        if room_id not in created_room_ids
    ]
    joined_rooms = Room.query.filter(Room.id.in_(joined_room_ids)).all()

    # формируем список всех комнат с проверкой роли
    rooms_with_roles = []
    for room in created_rooms + joined_rooms:
        role = 'admin' if room.creator_id == user_id else 'guest'
        rooms_with_roles.append({"room": room, "role": role})

    form = RoomForm()
    return render_template("dashboard.html", rooms=rooms_with_roles, form=form)


@app.route("/create-room", methods=["POST"])
def create_room():
    """
    Создает новую комнату и назначает текущего пользователя админом комнаты
    """
    if 'user_id' not in session:
        return redirect(url_for("login"))

    form = RoomForm()
    if form.validate_on_submit():
        try:
            # создание комнаты
            new_room = Room(
                name=form.name.data,
                identifier=form.identifier.data,
                password=form.password.data,
                description=form.description.data,
                creator_id=session['user_id']
            )
            db.session.add(new_room)
            db.session.commit()

            # присвоение роли admin создателю комнаты
            admin_role = Role.query.filter_by(name='admin').first()
            if admin_role:
                creator_role = UserRole(user_id=session['user_id'], room_id=new_room.id, role_id=admin_role.id)
                db.session.add(creator_role)
                db.session.commit()

            return redirect(url_for("dashboard"))

        except IntegrityError:
            db.session.rollback()
            flash("Идентификатор уже существует. Выберите другой.", "danger")
            return redirect(url_for("dashboard"))

    else:
        flash("Пожалуйста, заполните форму правильно.", "warning")
        return redirect(url_for("dashboard"))


@app.route('/join-room', methods=['POST'])
def join_room():
    """
    Присоединяет юзера к комнате как гостя после проверки идентификатора и пароля комнаты
    """
    if 'user_id' not in session:
        return redirect(url_for("login"))

    identifier = request.form.get('identifier')
    password = request.form.get('password')
    user_id = session.get('user_id')

    # проверка существования комнаты
    room = Room.query.filter_by(identifier=identifier).first()

    # Сущ комнаты и верности пароля
    if not room or room.password != password:
        return jsonify({"success": False, "message": "Неверный идентификатор или пароль комнаты."}), 400

    # является ли пользователь создателем комнаты
    if room.creator_id == user_id:
        return jsonify({"success": True, "message": "Вы уже являетесь создателем этой комнаты."}), 200

    #  не является ли пользователь уже участником
    existing_role = UserRole.query.filter_by(user_id=user_id, room_id=room.id).first()
    if existing_role:
        return jsonify({"success": False, "message": "Вы уже присоединились к этой комнате."}), 400

    # назначение роли пользователя как гостя
    role = Role.query.filter_by(name='guest').first()

    # добавление записи о присоединении пользователя к комнате
    user_role = UserRole(user_id=user_id, room_id=room.id, role_id=role.id)
    db.session.add(user_role)
    db.session.commit()

    return jsonify({"success": True, "message": "Вы успешно присоединились к комнате."})


@app.route("/rooms/<int:room_id>/edit", methods=["GET", "POST"])
def edit_room(room_id):
    """
    Редактирование данных комнаты доступно только для админа
    сохраняет изменения в базе данных
    """
    if 'user_id' not in session:
        return redirect(url_for("login"))
    room = Room.query.get_or_404(room_id)
    user_id = session.get('user_id')

    if room.creator_id != user_id:
        return render_template("dashboard.html", rooms=[room], form=RoomForm())

    form = RoomForm(obj=room)

    if form.validate_on_submit():
        try:
            # обновление данных комнаты
            room.name = form.name.data
            room.identifier = form.identifier.data
            room.password = form.password.data
            room.description = form.description.data
            db.session.commit()
            return redirect(url_for("dashboard"))
        except IntegrityError:
            db.session.rollback()
            flash("Идентификатор уже существует. Выберите другой.", "danger")

    return render_template("edit_room.html", form=form, room=room)


@app.route("/rooms/<int:room_id>/delete", methods=["POST"])
def delete_room(room_id):
    """
    Удаляет комнату вместе со всеми связанными событиями и записями о пользователях (user_roles)
    """
    if 'user_id' not in session:
        return redirect(url_for("login"))

    room = Room.query.get_or_404(room_id)

    # удаление всех ивентов, связанных с комнатой
    for event in room.events:
        db.session.delete(event)

    # удаление связанных с комнатой user_roles,
    user_roles = UserRole.query.filter_by(room_id=room_id).all()
    for user_role in user_roles:
        db.session.delete(user_role)

    # удал самой комнаты
    db.session.delete(room)
    db.session.commit()

    return redirect(url_for("dashboard"))



# --------------------- Ивенты ----------------------


@app.route("/rooms/<int:room_id>")
def room_detail(room_id):
    """
    Отображает детали комнаты
    Кнопки Создать ивент, Посмотреть участников для админа, Выйти из профиля
    """
    if 'user_id' not in session:
        return redirect(url_for("login"))

    user_id = session['user_id']
    room = Room.query.get_or_404(room_id)
    # Проверка роли пользователя в этой комнате
    user_role = UserRole.query.filter_by(user_id=user_id, room_id=room.id).first()
    if not user_role and room.creator_id != user_id:
        return redirect(url_for("dashboard"))

    # Определение роли и прав администратора
    role = 'admin' if room.creator_id == user_id else user_role.role.name
    is_admin = role == 'admin'

    return render_template("room_detail.html", room=room, events=room.events, form=EventForm(), role=role,
                           is_admin=is_admin)


@app.route("/rooms/<int:room_id>/members")
def room_members(room_id):
    """
    Отображает список участников комнаты,
    доступно только для админа комнаты
    """
    if 'user_id' not in session:
        return redirect(url_for("login"))

    user_id = session['user_id']
    room = Room.query.get_or_404(room_id)
    # пользователь админ ли комнаты
    user_role = UserRole.query.filter_by(user_id=user_id, room_id=room.id).first()
    if not user_role or user_role.role.name != 'admin':
        return redirect(url_for("room_detail", room_id=room_id))

    # Получение списка участников комнаты
    members = [
        {"user_id": ur.user.id, "name": ur.user.name, "role": ur.role.name}
        for ur in room.user_roles
    ]
    return render_template("room_members.html", room=room, members=members)


@app.route('/room/<int:room_id>/remove-member', methods=["POST"])
def remove_member(room_id):
    """
    Админ выгоняет guestа из комнаты
    """
    if 'user_id' not in session:
        return redirect(url_for("login"))

    user_id = session.get('user_id')
    room = Room.query.get_or_404(room_id)

    # админ ли юзер кто выгоняет
    admin_role = UserRole.query.filter_by(user_id=user_id, room_id=room.id,
                                          role_id=Role.query.filter_by(name='admin').first().id).first()
    if not admin_role:
        return redirect(url_for("room_members", room_id=room_id))

    # получение ID пользователя для удаления
    member_user_id = request.form.get("user_id")
    if not member_user_id:
        return redirect(url_for("room_members", room_id=room_id))
    #Удаляем участника из комнаты
    user_role = UserRole.query.filter_by(user_id=member_user_id, room_id=room.id).first()
    if user_role:
        db.session.delete(user_role)
        db.session.commit()
    else:
        flash("Пользователь для удаления не найден", "danger")
    return redirect(url_for("room_members", room_id=room_id))


@app.route("/create-event/<int:room_id>", methods=["POST"])
def create_event(room_id):
    """
    Создает новое событие для комнаты
    """
    if 'user_id' not in session:
        return redirect(url_for("login"))
    form = EventForm()
    if form.validate_on_submit():
        new_event = Event(
            title=form.title.data,
            description=form.description.data,
            date=form.date.data,
            location=form.location.data,
            room_id=room_id,
            organizer_id=session['user_id']
        )
        db.session.add(new_event)
        db.session.commit()
        return jsonify({"success": True}), 200

    # ошибки
    errors = {field: errors for field, errors in form.errors.items()}
    return jsonify({"success": False, "message": "Неправильные данные формы", "errors": errors}), 400


@app.route('/event/<int:event_id>', methods=['GET'])
def event_detail(event_id):
    """
    update ивента, коментарии и заметки
    """
    if 'user_id' not in session:
        return redirect(url_for("login"))
    event = Event.query.get_or_404(event_id)
    form = EventForm(obj=event)
    comment_form = CommentForm()
    notes = event.notes
    return render_template('event_detail.html', event=event, form=form, comment_form=comment_form, notes=notes)


@app.route('/event/<int:event_id>/delete', methods=['POST'])
def delete_event(event_id):
    """
    Удаляет событие, доступно только для админа
    """
    if 'user_id' not in session:
        return redirect(url_for("login"))
    event = Event.query.get_or_404(event_id)
    user_id = session.get('user_id')
    # проверка, что текущий пользователь - создатель события или комнаты
    if event.room.creator_id == user_id:
        db.session.delete(event)
        db.session.commit()
        return redirect(url_for('room_detail', room_id=event.room_id))
    else:
        return redirect(url_for('event_detail', event_id=event_id))


@app.route('/event/<int:event_id>/update', methods=['POST'])
def update_event(event_id):
    """
    Обновляет данные события при редактировании
    """
    if 'user_id' not in session:
        return redirect(url_for("login"))
    event = Event.query.get_or_404(event_id)
    form = EventForm()
    if form.validate_on_submit():
        # обновление данных события
        event.title = form.title.data
        event.description = form.description.data
        event.date = form.date.data
        event.location = form.location.data
        db.session.commit()
    else:
        return redirect(url_for('event_detail', event_id=event_id))
    return redirect(url_for('event_detail', event_id=event_id))


@app.route('/event/<int:event_id>/comment', methods=['POST'])
def add_comment(event_id):
    """
    Добавляет заметки к ивенту
    """
    if 'user_id' not in session:
        return redirect(url_for("login"))
    form = CommentForm()
    if form.validate_on_submit():
        # создание заметки
        comment = Note(content=form.content.data, event_id=event_id, user_id=session['user_id'])
        db.session.add(comment)
        db.session.commit()
    else:
        return redirect(url_for('event_detail', event_id=event_id))
    return redirect(url_for('event_detail', event_id=event_id))



# ---------------------- Уведомления ----------------------


@app.route('/add-reminder/<int:event_id>', methods=['POST'])
def add_reminder(event_id):
    """
    Добавляет напоминание для события за 2 дня до его начала
    """
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    event = Event.query.get_or_404(event_id)

    # Определение времени напоминания
    # reminder_time = event.date - timedelta(days=2)  # вариант для реального напоминания за 2 дня
    reminder_time = datetime.utcnow() + timedelta(minutes=1)  # вариант для теста

    # проверка на наличие существующего напоминания для этого события
    existing_reminder = Reminder.query.filter_by(event_id=event_id, user_id=user_id).first()
    if existing_reminder:
        # если напоминание уже создано, перенаправление на детали события
        return redirect(url_for('event_detail', event_id=event_id))

    # Создание напоминания и сохранение в базе
    reminder = Reminder(
        event_id=event_id,
        user_id=user_id,
        reminder_time=reminder_time,
        is_sent=False
    )
    db.session.add(reminder)
    db.session.commit()

    return redirect(url_for('event_detail', event_id=event_id))






# ----------------------OAuth----------------------


@app.route("/login/github")
def github_login():
    """
    Перенаправляет пользователя на GitHub для аутентификации через OAuth
    """
    github_auth_url = (
        f"https://github.com/login/oauth/authorize"
        f"?client_id={app.config['GITHUB_CLIENT_ID']}&scope=user"
    )
    return redirect(github_auth_url)


@app.route("/github/callback")
def github_callback():
    """
    обрабатывает обратный вызов от GitHub после авторизации
    обменивает код на токен доступа и создает/находит пользователя в базе
    """
    # Получение кода авторизации из параметров запроса
    code = request.args.get("code")
    if code is None:
        return "Authorization failed", 401

    # Обмен кода на токен доступа
    token_response = requests.post(
        "https://github.com/login/oauth/access_token",
        headers={"Accept": "application/json"},
        data={
            "client_id": app.config['GITHUB_CLIENT_ID'],
            "client_secret": app.config['GITHUB_CLIENT_SECRET'],
            "code": code,
        },
    )
    token_data = token_response.json()
    access_token = token_data.get("access_token")

    if access_token is None:
        return "Failed to obtain access token", 401

    #инфа о пользователе с помощью токена
    user_response = requests.get(
        "https://api.github.com/user",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    user_data = user_response.json()
    #Есть ли в бд или создание пользователя в базе данных
    user = User.query.filter_by(email=user_data.get("email")).first()
    iiimale = str(user_data.get("login", "")+"@gmail.com")
    if not user:
        user = User(
            name=user_data.get("login", "GitHub User"),
            email=user_data.get(iiimale, ""),
            password="iwerjqeismdawjko!!!$$@kqiwonmfznfuw2183471289hfH@H&@&@",  #неугадает 100%
        )
        db.session.add(user)
        db.session.commit()
    session["user_id"] = user.id
    return redirect(url_for("dashboard"))


@app.route("/login/yandex")
def yandex_login():
    """
    Перенаправляет пользователя на Яндекс для аутентификации через OAuth
    запрашивает разрешение на доступ к базовой информации о пользователе
    """
    yandex_auth_url = (
        f"https://oauth.yandex.ru/authorize"
        f"?response_type=code&client_id={app.config['YANDEX_CLIENT_ID']}"
    )
    return redirect(yandex_auth_url)


@app.route("/yandex/callback")
def yandex_callback():
    """
    Обрабатывает обратный вызов от Яндекс после авторизации
    обменивает код на токен доступа и создает/находит пользователя в базе
    """
    # получение кода авторизации
    code = request.args.get("code")
    if code is None:
        return "Authorization failed", 401

    # обмен кода на токен доступа
    token_response = requests.post(
        "https://oauth.yandex.ru/token",
        data={
            "grant_type": "authorization_code",
            "code": code,
            "client_id": app.config['YANDEX_CLIENT_ID'],
            "client_secret": app.config['YANDEX_CLIENT_SECRET'],
        }
    )
    token_data = token_response.json()
    access_token = token_data.get("access_token")
    if access_token is None:
        return "Failed to obtain access token", 401

    #получение пользователя с помощью токена
    user_response = requests.get(
        "https://login.yandex.ru/info",
        headers={"Authorization": f"OAuth {access_token}"}
    )
    user_data = user_response.json()
    #поиск или создание пользователя в базе данных
    user = User.query.filter_by(email=user_data.get("default_email")).first()
    if not user:
        user = User(
            name=user_data.get("real_name", "Yandex User"),
            email=user_data.get("default_email", ""),
            password="iwerjqeismdawjko!!!$$@kqiwonmfznfuw2183471289hfH@H&@&@",
        )
        db.session.add(user)
        db.session.commit()
    session["user_id"] = user.id
    return redirect(url_for("dashboard"))


