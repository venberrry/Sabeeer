from extensions import db
from models import Role

def initialize_roles(app):
    roles = [
        {'name': 'admin', 'description': 'Владелец комнаты'},
        {'name': 'guest', 'description': 'Приглашенный участник комнаты'}
    ]

    with app.app_context():
        for role_data in roles:
            existing_role = Role.query.filter_by(name=role_data['name']).first()
            if not existing_role:
                new_role = Role(name=role_data['name'], description=role_data['description'])
                db.session.add(new_role)

        db.session.commit()
