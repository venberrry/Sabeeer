from flask import jsonify
from main import app
from models import Room, User, Event, UserRole, Reminder


@app.route('/api/rooms/all')
def api_get_all_rooms():
    """
    Получение списка всех комнат в формате JSON.
    jsonify: Возвращает JSON-объект со списком всех комнат.
    """
    rooms = Room.query.all()
    rooms_json = [{"id": room.id, "name": room.name, "description": room.description, "creator_id": room.creator_id} for room in rooms]
    return jsonify(rooms_json)


@app.route('/api/reminders')
def api_get_all_reminders():
    """
    Получение списка всех напоминаний в формате JSON.
    Returns: jsonify: Возвращает JSON-объект со списком всех напоминаний.
    """
    reminders = Reminder.query.all()
    reminders_json = [{"id": reminder.id, "event_id": reminder.event_id, "user_id": reminder.user_id, "reminder_time": reminder.reminder_time, "is_sent": reminder.is_sent} for reminder in reminders]
    return jsonify(reminders_json)


@app.route('/api/user_roles')
def api_get_user_roles():
    """
    Получение списка всех ролей, которые есть у пользователей на сервере в разных комнатах, в формате JSON.
    jsonify: Возвращает JSON-объект со списком всех ролей пользователей.
    """
    user_roles = UserRole.query.all()
    user_roles_json = [{"user_id": user_role.user_id, "room_id": user_role.room_id, "role_id": user_role.role_id} for user_role in user_roles]
    return jsonify(user_roles_json)
