from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login

class User(UserMixin, db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128), nullable=False)
    # profile_picture = db.Column(db.String(140))
    user_bio = db.Column(db.String(140), default='New to SPS eSports!!!')
    pronouns = db.Column(db.String(64), nullable=True)
    skill_level = db.Column(db.String(64), default='Unsure')
    role = db.Column(db.String(64))
    grade = db.Column(db.String(64), nullable=True)
    availability = db.Column(db.String(140), default='Unsure')

    def get_id(self):
        return str(self.user_id)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Games(db.Model):
    game_id = db.Column(db.Integer, primary_key=True, index=True, unique=True, nullable=False)
    game_title = db.Column(db.String(64), index=True, nullable=False)
    platform = db.Column(db.String(64), index=True)
    year = db.Column(db.Integer, index=True)
    genre = db.Column(db.String(64), index=True)
    publisher = db.Column(db.String(64), index=True)
    global_sales = db.Column(db.Float, index=True)
    sales_ranking = db.Column(db.Integer, index=True)

    def __repr__(self):
        return '<Game {}>'.format(self.game_title)

    def get_id(self):
        return str(self.game_id)

"""class Following(db.Model):
    follow_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), primary_key=True)
    following_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), primary_key=True)

    def __repr__(self):
        return '<Following {}>'.format(self.following_id)

    def get_id(self):
        return str(self.follow_id)"""

class Teams(db.Model):
    team_id = db.Column(db.Integer, primary_key=True)
    team_name = db.Column(db.String(64), index=True, unique=True)
    team_description = db.Column(db.String(140), default='New Team!!!')
    admin_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    limit = db.Column(db.Integer, default=5)
    availability = db.Column(db.String(140), nullable=True)
    skill_level = db.Column(db.String(64), nullable=True)

    def __repr__(self):
        return '<Team {}>'.format(self.team_name)

    def get_id(self):
        return str(self.team_id)




@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id)) # returns the user id as an integer