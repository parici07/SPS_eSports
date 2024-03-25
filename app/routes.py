from app import app, db
from flask import render_template, flash, redirect, url_for, request
from app.forms import LoginForm, RegistrationForm, EditProfileForm, GameSearchForm, UserSearchForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Games
from werkzeug.urls import url_parse
import csv # now redundant, used for converting the csv file to db

@app.route('/')
@app.route('/index')
@login_required
def index():
    return render_template('index.html', title="Home")


### LOGIN AND ASSOCIATED ROUTES ###

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))

        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)

    return render_template('login.html', title="Login", form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        if form.code.data == 'STAFF2024':
            user = User(username=form.username.data, email=form.email.data, role='Staff')
        elif form.code.data == 'SPONSOR2024':
            user = User(username=form.username.data, email=form.email.data, role='Sponsor')
        else:
            user = User(username=form.username.data, email=form.email.data, role='Student')

        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration Complete')
        return redirect(url_for('login'))
    return render_template('register.html', title="Register", form=form)

## PROFILE HANDLING ###

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.user_bio = form.user_bio.data
        current_user.pronouns = form.pronouns.data
        current_user.skill_level = form.skill_level.data
        current_user.grade = "N/A"
        current_user.availability = form.availability.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('index'))
    else:
        flash('Something went wrong. Please try again.')

    return render_template('edit_profile.html', title="Edit Profile", form=form)

@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html', user=user)


### GAME SEARCH HANDLING ###

@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    form = GameSearchForm()

    if form.validate_on_submit():
        print('Form validated')
        games = Games.query.filter(Games.game_title.contains(form.game_title.data)).all()
        genre = form.genre.data
        publisher = form.publisher.data
        year = form.year.data
        platform = form.platform.data

        if genre != 'All Genres':
            filtered_games = []
            for game in games:
                if game.genre == genre:
                    filtered_games.append(game)
            games = filtered_games

        if publisher != '':
            filtered_games = []
            for game in games:
                if game.publisher == publisher:
                    filtered_games.append(game)
            games = filtered_games

        if year != 0:
            filtered_games = []
            for game in games:
                if game.year == year:
                    filtered_games.append(game)
            games = filtered_games

        if platform != 'All Platforms':
            filtered_games = []
            for game in games:
                if game.platform == platform:
                    filtered_games.append(game)
            games = filtered_games


        if games is None:
            flash('No results found. Please try again.')
            return render_template('search.html', title="Search", form=form)
        else:
            return render_template('results.html', games=games)

    else:
        flash('Something went wrong. Please try again.')

    return render_template('search.html', title="Search", form=form)

@app.route('/game/<game_id>')
@login_required
def game(game_id):
    game = Games.query.filter_by(game_id=game_id).first_or_404()
    return render_template('game.html', game=game)


### FRIENDS HANDLING ###

@app.route('/user_search', methods=['GET', 'POST'])
@login_required
def user_search():
    form = UserSearchForm()

    if form.validate_on_submit():
        users = User.query.filter(User.username.contains(form.username.data)).all()
        if users is None:
            flash('No results found. Please try again.')
            return render_template('search_users.html', title="Search Users", form=form)
        else:
            return render_template('user_results.html', users=users)
    else:
        flash('Something went wrong. Please try again.')
    return render_template('user_search.html', title="Search Users", form=form)


### TEAM HANDLING ###

### TOURNAMENT HANDLING ###