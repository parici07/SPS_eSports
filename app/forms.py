from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, IntegerField, \
    DateField, FileField, TimeField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, optional
from app.models import User


#CHOICES#

SKILL_CHOICES = [('Beginner', 'Beginner'), ('Intermediate', 'Intermediate'),
                 ('Advanced', 'Advanced'), ('Expert', 'Expert'), ('Unsure', 'Unsure')]

TEAM_SKILL_CHOICES = [("Any Skill Level", "Any Skill Level"), ('Beginner', 'Beginner'),
                      ('Intermediate', 'Intermediate'), ('Advanced', 'Advanced'), ('Expert', 'Expert'),
                      ('Unsure', 'Unsure')]

GRADE_CHOICES = [('3', '3'), ('4', '4'), ('5', '5'), ('6', '6'), ('7', '7'), ('8', '8'), ('9', '9'),
                 ('10', '10'), ('11', '11'), ('12', '12'), ('Staff', 'Staff'), ('Sponsor', 'Sponsor')]

AVAILABLE_CHOICES = [('Monday', 'Monday'), ('Tuesday', 'Tuesday'), ('Wednesday', 'Wednesday'),
                     ('Thursday', 'Thursday'), ('Friday', 'Friday'), ('Saturday', 'Saturday'),
                     ('Sunday', 'Sunday'), ('Weekdays', 'Weekdays'), ('Weekends', 'Weekends'),
                     ('Anytime', 'Anytime'), ('After School', 'After School'),
                     ('Before School', 'Before School'), ('Unsure', 'Unsure')]

TEAM_AVAILABLE_CHOICES =[('Any Availability', 'Any Availability'), ('Monday', 'Monday'), ('Tuesday', 'Tuesday'),
                        ('Wednesday', 'Wednesday'), ('Thursday', 'Thursday'), ('Friday', 'Friday'),
                        ('Saturday', 'Saturday'), ('Sunday', 'Sunday'), ('Weekdays', 'Weekdays'),
                        ('Weekends', 'Weekends'), ('Anytime', 'Anytime'), ('After School', 'After School'),
                        ('Before School', 'Before School'), ('Unsure', 'Unsure')]

GENRE_CHOICES = [('All Genres', 'All Genres'),('Sports', 'Sports'), ('Platform', 'Platform'), ('Racing', 'Racing'),
                 ('Role-Playing', 'Role-Playing'), ('Puzzle', 'Puzzle'), ('Misc', 'Misc'),
                 ('Shooter', 'Shooter'), ('Simulation', 'Simulation'), ('Action', 'Action'),
                 ('Fighting', 'Fighting'), ('Adventure', 'Adventure'), ('Strategy', 'Strategy')]

PLATFORM_CHOICES = [('All Platforms', 'All Platforms'),('Wii', 'Wii'), ('NES', 'NES'), ('GB', 'GB'), ('DS', 'DS'), ('X360', 'X360'),
                    ('PS3', 'PS3'), ('PS2', 'PS2'), ('SNES', 'SNES'), ('GBA', 'GBA'), ('3DS', '3DS'),
                    ('PS4', 'PS4'), ('N64', 'N64'), ('PS', 'PS'), ('XB', 'XB'), ('PC', 'PC'),
                    ('2600', '2600'), ('PSP', 'PSP'), ('XOne', 'XOne'), ('GC', 'GC'), ('WiiU', 'WiiU'),
                    ('GEN', 'GEN'), ('DC', 'DC'), ('PSV', 'PSV'), ('SAT', 'SAT'), ('SCD', 'SCD'),
                    ('WS', 'WS'), ('NG', 'NG'), ('TG16', 'TG16'), ('3DO', '3DO'), ('GG', 'GG'),
                    ('PCFX', 'PCFX')]

POST_TOPIC_CHOICES = [('General', 'General'), ('Game', 'Game'), ('Team', 'Team'), ('Event', 'Event')]
class LoginForm(FlaskForm): # Login form for existing users
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('SIGN IN')

class RegistrationForm(FlaskForm): # Registration form for new users
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    code = StringField('Code')
    submit = SubmitField('REGISTER')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('This username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('This email is taken. Please choose a different one.')

class EditProfileForm(FlaskForm):
    user_bio = StringField('User Bio')
    pronouns = StringField('Pronouns')
    skill_level = SelectField('Skill Level', choices=SKILL_CHOICES)
    grade = SelectField('Grade', choices=GRADE_CHOICES)
    availability = SelectField('Availability', choices=AVAILABLE_CHOICES)
    submit = SubmitField('Submit')


class GameSearchForm(FlaskForm):
    game_title = StringField('Game Title', validators=[DataRequired()])
    genre = SelectField('Genre', choices=GENRE_CHOICES)
    publisher = StringField('Publisher')
    year = IntegerField('Year', validators=[optional()])
    platform = SelectField('Platform', choices=PLATFORM_CHOICES)
    submit = SubmitField('Search')

class UserSearchForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    submit = SubmitField('Search')

class TeamSearchForm(FlaskForm):
    team_name = StringField('Team Name')
    skill_level = SelectField('Skill Level', choices=TEAM_SKILL_CHOICES)
    availability = SelectField('Availability', choices=TEAM_AVAILABLE_CHOICES)
    limit = IntegerField('Limit', validators=[optional()])
    submit = SubmitField('Search')

class CreateTeamForm(FlaskForm):
    team_name = StringField('Team Name', validators=[DataRequired()])
    team_description = StringField('Team Description')
    limit = IntegerField('Limit', validators=[DataRequired()])
    availability = SelectField('Availability', choices=TEAM_AVAILABLE_CHOICES)
    skill_level = SelectField('Skill Level', choices=TEAM_SKILL_CHOICES)
    submit = SubmitField('Create Team')

class PostForm(FlaskForm):
    post_title = StringField('Post Title', validators=[DataRequired()])
    post_content = StringField('Post Content', validators=[DataRequired()])
    post_type = SelectField('Post Topic', choices=POST_TOPIC_CHOICES)
    submit = SubmitField('Post')

class CommentForm(FlaskForm):
    comment_content = StringField('Comment Content', validators=[DataRequired()])
    submit = SubmitField('Comment')

class CreateTournamentForm(FlaskForm):
    tournament_name = StringField('Tournament Name', validators=[DataRequired()])
    tournament_description = StringField('Tournament Description')
    tournament_start = DateField('Start Date',format='%Y-%m-%d', validators=[DataRequired()])
    tournament_end = DateField('End Date', format='%Y-%m-%d', validators=[DataRequired()])
    tournament_skill_level = SelectField('Skill Level', choices=TEAM_SKILL_CHOICES)
    tournament_min_grade = SelectField('Minimum Grade', choices=GRADE_CHOICES)
    participants = IntegerField('Participants', validators=[DataRequired()])
    submit = SubmitField('Create Tournament')





class UploadPfpForm(FlaskForm):
    pfp = FileField('Profile Picture', validators=[DataRequired()])
    submit = SubmitField('Upload')

class TournamentSearchForm(FlaskForm):
    tournament_name = StringField('Tournament Name')
    tournament_skill_level = SelectField('Skill Level', choices=TEAM_SKILL_CHOICES, validators=[optional()])
    tournament_min_grade = SelectField('Minimum Grade', choices=GRADE_CHOICES, validators=[optional()])
    tournament_start = DateField('Start Date',format='%Y-%m-%d', validators=[optional()])
    tournament_end = DateField('End Date', format='%Y-%m-%d', validators=[optional()])
    submit = SubmitField('Search')

class AddWinnerForm(FlaskForm):
    winner = StringField('Winner', validators=[DataRequired()])
    submit = SubmitField('Submit')

class AddMatchDetailsForm(FlaskForm):
    player1 = SelectField('Player 1', validators=[DataRequired()])
    player2 = SelectField('Player 2', validators=[DataRequired()])
    match_date = DateField('Match Date', format='%Y-%m-%d', validators=[DataRequired()])
    submit = SubmitField('Submit')

class AddMatchWinnerForm(FlaskForm):
    winner = SelectField('Winner', validators=[DataRequired()])
    submit = SubmitField('Submit')

class CreatePractiseForm(FlaskForm):
    practise_name = StringField('Practise Name', validators=[DataRequired()])
    practise_description = StringField('Practise Description')
    practise_date = DateField('Practise Date', format='%Y-%m-%d', validators=[DataRequired()])
    practise_time = TimeField('Practise Time', format='%H:%M', validators=[DataRequired()])
    submit = SubmitField('Create Practise')


