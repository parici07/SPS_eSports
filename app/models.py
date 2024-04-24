from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login
from sqlalchemy import ForeignKeyConstraint


class User(UserMixin, db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128), nullable=False)
    pfp = db.Column(db.String(140))
    user_bio = db.Column(db.String(140), default='New to SPS eSports!!!')
    pronouns = db.Column(db.String(64), nullable=True)
    skill_level = db.Column(db.String(64), default='Unsure')
    role = db.Column(db.String(64))
    grade = db.Column(db.String(64), nullable=True)
    availability = db.Column(db.String(140), default='Unsure')

    teams = db.relationship('Teams', back_populates='user')
    team_users = db.relationship('TeamUsers', back_populates='user')
    posts = db.relationship('Posts', back_populates='user')
    likes = db.relationship('Likes', back_populates='user')
    tournaments = db.relationship('Tournaments', back_populates='user')
    favourite_games = db.relationship('FavouriteGames', back_populates='user')
    tournament_users = db.relationship('TournamentUsers', back_populates='user')
    comments = db.relationship('Comments', back_populates='user')
    matches = db.relationship('Matches', back_populates='user')
    match_users = db.relationship('MatchUsers', back_populates='user')

    following = db.relationship('Following', backref='user', foreign_keys='Following.user_id')
    followed = db.relationship('Following', foreign_keys='Following.following_id')

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

    favourite_games = db.relationship('FavouriteGames', back_populates='game')

    def __repr__(self):
        return '<Game {}>'.format(self.game_title)

    def get_id(self):
        return str(self.game_id)


class Teams(db.Model):
    team_id = db.Column(db.Integer, primary_key=True, index=True, unique=True, nullable=False)
    team_name = db.Column(db.String(64), index=True, unique=True)
    team_description = db.Column(db.String(140), default='New Team!!!')
    limit = db.Column(db.Integer, default=5)
    availability = db.Column(db.String(140), nullable=True)
    skill_level = db.Column(db.String(64), nullable=True)

    admin_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), name='fk_admin_id')

    user = db.relationship('User', back_populates='teams')
    team_users = db.relationship('TeamUsers', back_populates='team')
    practises = db.relationship('Practises', back_populates='team')

    def __repr__(self):
        return '<Team {}>'.format(self.team_name)

    def get_id(self):
        return str(self.team_id)


class TeamUsers(db.Model):
    team_user_id = db.Column(db.Integer, primary_key=True, index=True, unique=True, nullable=False)

    team_id = db.Column(db.Integer, db.ForeignKey('teams.team_id'), name='fk_team_id', nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), name='fk_user_id', nullable=False)

    team = db.relationship('Teams', back_populates='team_users')
    user = db.relationship('User', back_populates='team_users')

    def __repr__(self):
        return '<TeamUser {}>'.format(self.team_user_id)

    def get_id(self):
        return str(self.team_user_id)


class Posts(db.Model):
    post_id = db.Column(db.Integer, primary_key=True, index=True, unique=True, nullable=False)
    post_title = db.Column(db.String(64), nullable=False)
    post_content = db.Column(db.String(140), nullable=False)
    post_date = db.Column(db.DateTime, nullable=False)
    post_type = db.Column(db.String(64))
    likes = db.Column(db.Integer, default=0)

    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), name='post_user_id', nullable=False)

    user = db.relationship('User', back_populates='posts')
    post_likes = db.relationship('Likes', back_populates='post')
    comments = db.relationship('Comments', back_populates='post')

    def __repr__(self):
        return '<Post {}>'.format(self.post_title)

    def get_id(self):
        return str(self.post_id)


class Likes(db.Model):
    like_id = db.Column(db.Integer, primary_key=True, index=True, unique=True, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), name='like_user_id', nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.post_id'), name='like_post_id', nullable=False)

    user = db.relationship('User', back_populates='likes')
    post = db.relationship('Posts', back_populates='post_likes')

    def __repr__(self):
        return '<Likes {}>'.format(self.like_id)

    def get_id(self):
        return str(self.like_id)


class Comments(db.Model):
    comment_id = db.Column(db.Integer, primary_key=True, index=True, unique=True, nullable=False)
    comment_content = db.Column(db.String(140), nullable=False)
    comment_date = db.Column(db.DateTime, index=True, nullable=False)
    username = db.Column(db.String(64), nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), name='comment_user_id', nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.post_id'), name='comment_post_id', nullable=False)

    user = db.relationship('User', back_populates='comments')
    post = db.relationship('Posts', back_populates='comments')

    def __repr__(self):
        return '<Comment {}>'.format(self.comment_id)

    def get_id(self):
        return str(self.comment_id)


class Following(db.Model):
    follow_id = db.Column(db.Integer, primary_key=True, index=True, unique=True, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), name='follow_user_id', nullable=False)
    following_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), name='follow_following_id', nullable=False)

    def __repr__(self):
        return '<Following {}>'.format(self.follow_id)

    def get_id(self):
        return str(self.follow_id)


class Tournaments(db.Model):
    tournament_id = db.Column(db.Integer, primary_key=True, index=True, unique=True, nullable=False)
    tournament_name = db.Column(db.String(64), index=True, unique=True)
    tournament_description = db.Column(db.String(140), default='New Tournament!!!')
    tournament_start = db.Column(db.DateTime, index=True)
    tournament_end = db.Column(db.DateTime, index=True)
    tournament_skill_level = db.Column(db.String(64), nullable=True)
    tournament_min_grade = db.Column(db.String(64), nullable=True)
    winner = db.Column(db.Integer, db.ForeignKey('user.user_id'), name='tournament_user_id', nullable=True)
    participants = db.Column(db.Integer, default=2)

    user = db.relationship('User', back_populates='tournaments')
    tournament_users = db.relationship('TournamentUsers', back_populates='tournament')
    matches = db.relationship('Matches', back_populates='tournament')

    def __repr__(self):
        return '<Tournament {}>'.format(self.tournament_name)

    def get_id(self):
        return str(self.tournament_id)


class TournamentUsers(db.Model):
    tournament_user_id = db.Column(db.Integer, primary_key=True, index=True, unique=True, nullable=False)

    tournament_id = db.Column(db.Integer, db.ForeignKey('tournaments.tournament_id'), name='tournament_tournament_id',
                              nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), name='tournament_user_user_id', nullable=False)

    tournament = db.relationship('Tournaments', back_populates='tournament_users')
    user = db.relationship('User', back_populates='tournament_users')

    def __repr__(self):
        return '<TournamentUser {}>'.format(self.tournament_user_id)

    def get_id(self):
        return str(self.tournament_user_id)


class Matches(db.Model):
    match_id = db.Column(db.Integer, primary_key=True, index=True, unique=True, nullable=False)
    match_date = db.Column(db.DateTime, index=True)
    round = db.Column(db.Integer, nullable=False)
    round_match = db.Column(db.Integer, nullable=False)

    match_winner = db.Column(db.Integer, db.ForeignKey('user.user_id'), name='match_winner_id', nullable=True)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournaments.tournament_id'), name='match_tournament_id',
                              nullable=False)

    user = db.relationship('User', back_populates='matches')
    tournament = db.relationship('Tournaments', back_populates='matches')
    match_users = db.relationship('MatchUsers', back_populates='match')

    def __repr__(self):
        return '<Match {}>'.format(self.match_id)

    def get_id(self):
        return str(self.match_id)


class MatchUsers(db.Model):
    matchuser_id = db.Column(db.Integer, primary_key=True, index=True, unique=True, nullable=False)

    match_user = db.Column(db.Integer, db.ForeignKey('user.user_id'), name='match_user_id', nullable=False)
    match_id = db.Column(db.Integer, db.ForeignKey('matches.match_id'), name='match_id', nullable=False)

    user = db.relationship('User', back_populates='match_users')
    match = db.relationship('Matches', back_populates='match_users')

    def __repr__(self):
        return '<MatchUser {}>'.format(self.matchuser_id)

    def get_id(self):
        return str(self.matchuser_id)


class FavouriteGames(db.Model):
    favourite_id = db.Column(db.Integer, primary_key=True, index=True, unique=True, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), name='favourite_user_id', nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey('games.game_id'), name='favourite_game_id', nullable=False)

    user = db.relationship('User', back_populates='favourite_games')
    game = db.relationship('Games', back_populates='favourite_games')

    def __repr__(self):
        return '<FavouriteGames {}>'.format(self.favourite_id)

    def get_id(self):
        return str(self.favourite_id)


class Practises(db.Model):
    practise_id = db.Column(db.Integer, primary_key=True, index=True, unique=True, nullable=False)
    practise_date = db.Column(db.Date, index=True, nullable=False)
    practise_time = db.Column(db.Time, index=True, nullable=False)
    practise_name = db.Column(db.String(64), index=True, unique=True)
    practise_description = db.Column(db.String(140), default='Team Practise')

    team_id = db.Column(db.Integer, db.ForeignKey('teams.team_id'), name='practise_team_id', nullable=False)

    team = db.relationship('Teams', back_populates='practises')

    def __repr__(self):
        return '<Practise {}>'.format(self.practise_id)

    def get_id(self):
        return str(self.practise_id)


@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))  # returns the user id as an integer