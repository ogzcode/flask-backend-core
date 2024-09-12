from app import db
from app.models import User


class UserService:
    @staticmethod
    def get_all_users():
        users = User.query.all()
        return [user for user in users]

    @staticmethod
    def get_user_by_id(user_id):
        user = User.query.get(user_id)
        return user

    @staticmethod
    def create_user(username, email, password):
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def update_user(user_id, username, email, password):
        user = User.query.get(user_id)
        user.username = username
        user.email = email
        user.set_password(password)
        db.session.commit()
        return user

    @staticmethod
    def delete_user(user_id):
        user = User.query.get(user_id)
        db.session.delete(user)
        db.session.commit()
        return user
    
    @staticmethod
    def get_user_by_email(email):
        user = User.query.filter_by(email=email).first()
        return user