from app import app, db
from flask import render_template, flash, redirect, url_for, request
from app.forms import LoginForm, RegistrationForm, EditProfileForm, GameSearchForm, UserSearchForm,\
    CreateTeamForm, TeamSearchForm, PostForm, CreateTournamentForm, UploadPfpForm, TournamentSearchForm, \
    AddWinnerForm, CommentForm, AddMatchDetailsForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Games, Teams, TeamUsers, Posts, Following, Likes, Tournaments, FavouriteGames, \
    TournamentUsers, Comments, Matches, MatchUsers
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename
import csv # now redundant, used for converting the csv file to db
import datetime as dt
from datetime import datetime
import os
import math

@app.route('/')
@app.route('/index')
@login_required
def index():
    following = Following.query.filter_by(user_id=current_user.user_id).all()
    followed_users = []

    # get all users followed
    for user in following:
        user = User.query.filter_by(user_id=user.following_id).first()
        followed_users.append(user)
    print(followed_users)



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
    spons = False
    if form.validate_on_submit():
        if form.code.data == 'STAFF2024':
            user = User(username=form.username.data, email=form.email.data, role='Staff')
        elif form.code.data == 'SPONSOR2024':
            user = User(username=form.username.data, email=form.email.data, role='Sponsor')
            spons = True
        else:
            user = User(username=form.username.data, email=form.email.data, role='Student')

        email = form.email.data
        email_domain = email.split('@')[1]
        print(email_domain)

        if email_domain != 'stpauls.qld.edu.au' and spons == False:
            flash('Invalid email domain. Please use your school email.')
            return redirect(url_for('register'))

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
        current_user.grade = form.grade.data
        current_user.availability = form.availability.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('index'))
    else:
        flash('Something went wrong. Please try again.')

    return render_template('edit_profile.html', title="Edit Profile", form=form)

@app.route('/upload_pfp', methods=['GET', 'POST'])
@login_required
def upload_pfp():
    form = UploadPfpForm()

    if form.validate_on_submit():
        if current_user.pfp:
            os.remove('app/static/pfps/' + current_user.pfp)
        file_name = secure_filename(form.pfp.data.filename)
        if 'app/static/pfps/' + file_name:
            file_name = '1' + file_name
        form.pfp.data.save('app/static/pfps/' + file_name)
        current_user.pfp = file_name
        db.session.commit()
        flash('Profile Picture Uploaded')
        return redirect(url_for('user', username=current_user.username))
    return render_template('upload_pfp.html', title="Upload Profile Picture", form=form)

@app.route('/user/<username>', methods=['GET', 'POST'])
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    username = user.username

    # checks if following users
    if Following.query.filter_by(user_id=current_user.user_id, following_id=user.user_id).count() > 0:
        is_following = True
    else:
        is_following = False

    # checks if users are mutuals
    if is_following and Following.query.filter_by(user_id=user.user_id, following_id=current_user.user_id).count() > 0:
        mutuals = True
    else:
        mutuals = False

    # gets all tournaments won
    tournaments = Tournaments.query.filter_by(winner=user.user_id).all()

    # gets favourited games
    fave_id = FavouriteGames.query.filter_by(user_id=user.user_id).all()
    favourites = []
    for favourite in fave_id:
        game = Games.query.filter_by(game_id=favourite.game_id).first()
        favourites.append(game)


    posts = Posts.query.filter_by(user_id=user.user_id).order_by(Posts.post_date.desc()).all()
    return render_template('user.html', user=user, posts=posts, username=username, is_following=is_following, mutuals=mutuals, tournaments=tournaments, favourites=favourites)

@app.route('/following/<username>')
@login_required
def following(username):
    user = User.query.filter_by(username=username).first_or_404()

    # gets list of people you follow
    following = Following.query.filter_by(user_id=user.user_id).all()
    following_list = []
    for follow in following:
        follow = User.query.filter_by(user_id=follow.following_id).first()
        following_list.append(follow)

    return render_template('following.html', user=user, following=following_list)

@app.route('/followers/<username>')
@login_required
def followers(username):
    user = User.query.filter_by(username=username).first_or_404()

    # gets list of people who follow you

    followers = Following.query.filter_by(following_id=user.user_id).all()
    followers_list = []
    for follower in followers:
        follower = User.query.filter_by(user_id=follower.user_id).first()
        followers_list.append(follower)

    return render_template('followers.html', user=user, followers=followers_list)


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

        if year != None:
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

    posts = Posts.query.filter_by(post_type=game.game_title + ' for ' + game.platform).order_by(Posts.post_date.desc()).all()

    user = current_user
    favourite = FavouriteGames.query.filter_by(user_id=user.user_id, game_id=game.game_id).count()

    return render_template('game.html', game=game, posts=posts, favourite=favourite)

@app.route('/game_post/<game_id>', methods=['GET', 'POST'])
@login_required
def game_post(game_id):
    game = Games.query.filter_by(game_id=game_id).first_or_404()

    form = PostForm()
    if form.validate_on_submit():
        post_title = form.post_title.data
        post_content = form.post_content.data
        post_type = game.game_title + ' for ' + game.platform

        post_date = dt.datetime.now()
        user_id = current_user.user_id

        post = Posts(post_title=post_title, post_content=post_content, post_date=post_date, post_type=post_type, user_id=user_id)

        db.session.add(post)
        db.session.commit()
        flash('Post created successfully')
        return redirect(url_for('game', game_id=game_id))
    else:
        flash('Something went wrong. Please try again.')

    return render_template('game_post.html', title="Create Post", form=form, game=game)

@app.route('/favourite_game/<game_id>', methods=['GET', 'POST'])
@login_required
def favourite_game(game_id):
    game = Games.query.filter_by(game_id=game_id).first_or_404()
    user = current_user

    if FavouriteGames.query.filter_by(user_id=user.user_id, game_id=game.game_id).count() > 0:
        # remove from favourites
        favourite = FavouriteGames.query.filter_by(user_id=user.user_id, game_id=game.game_id).first()
        db.session.delete(favourite)
        db.session.commit()
        flash('Game removed from favourites')
    else:
        # add to favourites
        favourite = FavouriteGames(user_id=user.user_id, game_id=game.game_id)
        db.session.add(favourite)
        db.session.commit()
        flash('Game added to favourites')

    return redirect(url_for('game', game_id=game_id))

### FOLLOWING HANDLING ###

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

@app.route('/follow/<username>', methods=['GET', 'POST'])
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first_or_404()
    user_id = current_user.user_id
    following_id = user.user_id

    if user_id == following_id:
        flash('You cannot follow yourself. Nice try though.')
        return redirect(url_for('user', username=username))
    else:
        follow = Following(user_id=user_id, following_id=following_id)
        db.session.add(follow)
        db.session.commit()
        flash('You are now following ' + username)
        return redirect(url_for('user', username=username))

@app.route('/unfollow/<username>', methods=['GET', 'POST'])
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first_or_404()
    user_id = current_user.user_id
    following_id = user.user_id

    if user_id == following_id:
        flash("You cannot unfollow yourself. You can't even follow yourself??? How did you get here mate.")
        return redirect(url_for('user', username=username))
    else:
        follow = Following.query.filter_by(user_id=user_id, following_id=following_id).first()
        db.session.delete(follow)
        db.session.commit()
        flash('You are no longer following ' + username)
        return redirect(url_for('user', username=username))




### TEAM HANDLING ###
@app.route('/create_team', methods=['GET', 'POST'])
@login_required
def create_team():
    form = CreateTeamForm()

    if form.validate_on_submit():
        team_name = form.team_name.data
        team_description = form.team_description.data
        limit = form.limit.data

        if limit < 2:
            flash('Team limit must be greater than 1')
            return redirect(url_for('create_team'))
        if limit > 20:
            flash('Team limit must be less than 20')
            return redirect(url_for('create_team'))

        availability = form.availability.data
        if availability == 'Any Availability':
            availability = 'Any'

        skill_level = form.skill_level.data
        if skill_level == 'Any Skill Level':
            skill_level = 'Any'
        admin_id = current_user.user_id

        team = Teams(team_name=team_name, team_description=team_description, limit=limit, availability=availability, skill_level=skill_level, admin_id=admin_id)

        db.session.add(team)
        db.session.commit()
        print(team.team_id)
        team_user = TeamUsers(team_id=team.team_id, user_id=current_user.user_id)
        print(team_user.team_id, team_user.user_id)
        db.session.add(team_user)
        db.session.commit()
        flash('Team created successfully')
        return redirect(url_for('index'))
    else:
        print(form.errors)
        flash('Something went wrong. Please try again.')

    return render_template('create_team.html', title="Create Team", form=form)

@app.route('/team_search', methods=['GET', 'POST'])
@login_required
def team_search():
    form = TeamSearchForm()

    if form.validate_on_submit():
        teams = Teams.query.filter(Teams.team_name.contains(form.team_name.data)).all()
        skill_level = form.skill_level.data
        availability = form.availability.data

        if skill_level != 'Any Skill Level':
            filtered_teams = []
            for team in teams:
                if team.skill_level == skill_level:
                    filtered_teams.append(team)
            teams = filtered_teams

        if availability != 'Any Availability':
            filtered_teams = []
            for team in teams:
                if team.availability == availability:
                    filtered_teams.append(team)
            teams = filtered_teams

        if form.limit.data != None:
            filtered_teams = []
            for team in teams:
                if team.limit >= form.limit.data:
                    filtered_teams.append(team)
            teams = filtered_teams

        if teams is None:
            flash('No results found. Please try again.')
            return render_template('search_teams.html', title="Search Teams", form=form)
        else:
            return render_template('team_results.html', teams=teams)
    else:
        flash('Something went wrong. Please try again.')
        print(form.errors)
    return render_template('team_search.html', title="Search Teams", form=form)

@app.route('/team/<team_id>')
@login_required
def team(team_id):
    if TeamUsers.query.filter_by(team_id=team_id, user_id=current_user.user_id).count() > 0:
        my_team = True
    else:
        my_team = False
    team = Teams.query.filter_by(team_id=team_id).first_or_404()
    team_users = TeamUsers.query.filter_by(team_id=team_id).all()
    users = []
    for team_user in team_users:
        print(team_user.user_id)
        user = User.query.filter_by(user_id=team_user.user_id).first()
        users.append(user)
    print(users)
    return render_template('team.html', team=team, team_users=team_users, users=users, my_team=my_team)

@app.route('/join_team/<team_id>', methods=['GET', 'POST'])
@login_required
def join_team(team_id):
    user = current_user
    team = Teams.query.filter_by(team_id=team_id).first_or_404()

    # check if user is already in team
    if TeamUsers.query.filter_by(team_id=team_id, user_id=user.user_id).count() > 0:
        flash('You are already in this team!')
        return redirect(url_for('team', team_id=team_id))

    team_users = TeamUsers.query.filter_by(team_id=team_id).all()

    if team.skill_level != 'Any Skill Level' and team.skill_level != user.skill_level:
        flash('This team does not take applications from someone of your skill level. Sorry!')
        return redirect(url_for('team', team_id=team_id))

    if team.availability != 'Any Availability' and team.availability != user.availability:
        flash('This team does not take applications from someone with your availability. Sorry!')
        return redirect(url_for('team', team_id=team_id))

    if len(team_users) >= team.limit:
        flash('This team is full. Sorry!')
        return redirect(url_for('team', team_id=team_id))

    team_user = TeamUsers(team_id=team_id, user_id=user.user_id)
    db.session.add(team_user)
    db.session.commit()
    flash('Welcome to the team!!')
    return redirect(url_for('team', team_id=team_id))

@app.route('/leave_team/<team_id>', methods=['GET', 'POST'])
@login_required
def leave_team(team_id):
    user = current_user
    team = Teams.query.filter_by(team_id=team_id).first_or_404()

    # check if user is in team
    if TeamUsers.query.filter_by(team_id=team_id, user_id=user.user_id).count() == 0:
        flash('You are not in this team!')
        return redirect(url_for('team', team_id=team_id))

    team_user = TeamUsers.query.filter_by(team_id=team_id, user_id=user.user_id).first()
    db.session.delete(team_user)
    db.session.commit()
    flash('You have left the team')
    return redirect(url_for('team', team_id=team_id))

### POST HANDLING ###
@app.route('/create_post', methods=['GET', 'POST'])
@login_required
def create_post():
    form = PostForm()

    if form.validate_on_submit():
        post_title = form.post_title.data
        post_content = form.post_content.data
        post_type = form.post_type.data

        post_date = dt.datetime.now()
        user_id = current_user.user_id

        post = Posts(post_title=post_title, post_content=post_content, post_date=post_date, post_type=post_type, user_id=user_id)

        db.session.add(post)
        db.session.commit()
        flash('Post created successfully')
        return redirect(url_for('index'))
    else:
        flash('Something went wrong. Please try again.')

    return render_template('create_post.html', title="Create Post", form=form)

@app.route('/delete_post/<post_id>', methods=['GET', 'POST'])
@login_required
def delete_post(post_id):
    post = Posts.query.filter_by(post_id=post_id).first_or_404()
    if post.user_id != current_user.user_id:
        flash('You cannot delete this post')
        return redirect(url_for('post', post_id=post_id))

    db.session.delete(post)
    db.session.commit()
    flash('Post deleted successfully')
    return redirect(url_for('index'))


@app.route('/post/<post_id>', methods=['GET', 'POST'])
@login_required
def post(post_id):
    post = Posts.query.filter_by(post_id=post_id).first_or_404()
    creator = User.query.filter_by(user_id=post.user_id).first()

    is_liked = Likes.query.filter_by(user_id=current_user.user_id, post_id=post_id).count()
    my_post = Posts.query.filter_by(post_id=post_id, user_id=current_user.user_id).count()

    comments = Comments.query.filter_by(post_id=post_id).all()

    return render_template('post.html', post=post, creator=creator, is_liked=is_liked, my_post=my_post, comments=comments)

@app.route('/like/<post_id>', methods=['GET', 'POST'])
@login_required
def like(post_id):
    is_liked = Likes.query.filter_by(user_id=current_user.user_id, post_id=post_id).count()

    if is_liked == 0:
        if Posts.query.filter_by(post_id=post_id, user_id=current_user.user_id).count() > 0:
            flash('You cannot like your own post.')
            return redirect(url_for('post', post_id=post_id))

        like = Likes(user_id=current_user.user_id, post_id=post_id)
        db.session.add(like)
        db.session.commit()
        flash('You have liked this post')
    else:
        like = Likes.query.filter_by(user_id=current_user.user_id, post_id=post_id).first()
        db.session.delete(like)
        db.session.commit()
        flash('You have unliked this post')

    return redirect(url_for('post', post_id=post_id))

### COMMENT HANDLING ###

@app.route('/post_comment/<post_id>', methods=['GET', 'POST'])
@login_required
def post_comment(post_id):
    form = CommentForm()
    post = Posts.query.filter_by(post_id=post_id).first_or_404()
    post_user = User.query.filter_by(user_id=post.user_id).first()

    if form.validate_on_submit():
        comment_content = form.comment_content.data
        comment_date = dt.datetime.now()
        user_id = current_user.user_id
        username = current_user.username

        comment = Comments(comment_content=comment_content, comment_date=comment_date, user_id=user_id, post_id=post_id, username=username)

        db.session.add(comment)
        db.session.commit()
        flash('Comment created successfully')
        return redirect(url_for('post', post_id=post_id))
    else:
        flash('Something went wrong. Please try again.')
        print(form.errors)

    return render_template('post_comment.html', title="Create Comment", form=form, post=post, post_user=post_user)

### TOURNAMENT HANDLING ###

@app.route('/create_tournament', methods=['GET', 'POST'])
@login_required
def create_tournament():
    user = current_user
    form = CreateTournamentForm()
    if user.role != 'Staff':
        flash('You are not authorised to create a tournament.')
        return redirect(url_for('index'))

    if form.validate_on_submit():
        tournament_name = form.tournament_name.data
        tournament_description = form.tournament_description.data
        tournament_start = form.tournament_start.data
        tournament_end = form.tournament_end.data
        tournament_skill_level = form.tournament_skill_level.data
        tournament_min_grade = form.tournament_min_grade.data
        participants = form.participants.data

        # make sure participants is a power of 2
        base = 2
        output = math.log(participants, base)
        if output != int(output):
            flash('Participants must be a power of 2')
            return redirect(url_for('create_tournament'))


        tournament = Tournaments(tournament_name=tournament_name, tournament_description=tournament_description,
                                 tournament_start=tournament_start, tournament_end=tournament_end,
                                 tournament_skill_level=tournament_skill_level,
                                 tournament_min_grade=tournament_min_grade, participants=participants)
        db.session.add(tournament)
        db.session.commit()
        flash('Tournament created successfully')

        # add matches
        rounds = int(math.log(participants, 2))

        for i in range(1, rounds+1):
            matches = int(participants / 2)
            for j in range(1, matches+1):
                match = Matches(tournament_id=tournament.tournament_id, round=i, round_match=j)
                db.session.add(match)
                db.session.commit()
            participants = participants / 2
        return redirect(url_for('index'))
    else:
        flash('Something went wrong. Please try again.')
        print(form.errors)

    return render_template('create_tournament.html', title="Create Tournament", form=form)

@app.route('/tournament_search', methods=['GET', 'POST'])
@login_required
def tournament_search():
    form = TournamentSearchForm()
    role = current_user.role

    if form.validate_on_submit():
        tournament_name = form.tournament_name.data
        tournaments = Tournaments.query.filter(Tournaments.tournament_name.contains(tournament_name)).all()

        tournament_skill_level = form.tournament_skill_level.data
        tournament_min_grade = form.tournament_min_grade.data
        tournament_start = form.tournament_start.data
        tournament_end = form.tournament_end.data

        if tournament_skill_level != 'Any Skill Level':
            filtered_tournaments = []
            for tournament in tournaments:
                if tournament.tournament_skill_level == tournament_skill_level:
                    filtered_tournaments.append(tournament)
            tournaments = filtered_tournaments

        if tournament_min_grade:
            filtered_tournaments = []
            for tournament in tournaments:
                if tournament.tournament_min_grade == tournament_min_grade:
                    filtered_tournaments.append(tournament)
            tournaments = filtered_tournaments

        if tournament_start != None:
            filtered_tournaments = []
            for tournament in tournaments:
                if tournament.tournament_start == tournament_start:
                    filtered_tournaments.append(tournament)
            tournaments = filtered_tournaments

        if tournament_end != None:
            filtered_tournaments = []
            for tournament in tournaments:
                if tournament.tournament_end == tournament_end:
                    filtered_tournaments.append(tournament)
            tournaments = filtered_tournaments

        return render_template('tournament_results.html', tournaments=tournaments)
    else:
        flash('Something went wrong. Please try again.')
        print(form.errors)

    return render_template('tournament_search.html', title="Search Tournaments", form=form, role=role)

@app.route('/tournament/<tournament_id>')
@login_required
def tournament(tournament_id):
    tournament = Tournaments.query.filter_by(tournament_id=tournament_id).first_or_404()
    user = current_user
    in_tournament = TournamentUsers.query.filter_by(tournament_id=tournament_id, user_id=user.user_id).count()
    participant_id = TournamentUsers.query.filter_by(tournament_id=tournament_id).all()
    participants = []
    for participant in participant_id:
        user = User.query.filter_by(user_id=participant.user_id).first()
        participants.append(user)

    # get all matches
    matches = Matches.query.filter_by(tournament_id=tournament_id).all()

    return render_template('tournament.html', tournament=tournament, user=user, in_tournament=in_tournament, participants=participants, matches=matches)

@app.route('/join_tournament/<tournament_id>')
@login_required
def join_tournament(tournament_id):
    tournament = Tournaments.query.filter_by(tournament_id=tournament_id).first_or_404()
    user = current_user

    if user.role != 'Student':
        flash(f'{user.role} cannot join tournaments.')
        return redirect(url_for('index'))

    # requirements
    skill_level = tournament.tournament_skill_level
    min_grade = tournament.tournament_min_grade


    in_tournament = TournamentUsers.query.filter_by(tournament_id=tournament_id, user_id=user.user_id).count()

    if in_tournament > 0:
        flash('You have left this tournament')
        tournament_user = TournamentUsers.query.filter_by(tournament_id=tournament_id, user_id=user.user_id).first()
        db.session.delete(tournament_user)
        db.session.commit()
        return redirect(url_for('tournament', tournament_id=tournament_id))
    else:
        if user.skill_level != skill_level and skill_level != 'Any Skill Level':
            flash('You do not meet the skill level requirements for this tournament')
            return redirect(url_for('tournament', tournament_id=tournament_id))
        if int(user.grade) < int(min_grade):
            flash('You do not meet the grade requirements for this tournament')
            return redirect(url_for('tournament', tournament_id=tournament_id))

        tournament_user = TournamentUsers(tournament_id=tournament_id, user_id=user.user_id)
        db.session.add(tournament_user)
        db.session.commit()
        flash('You have joined this tournament')
        return redirect(url_for('tournament', tournament_id=tournament_id))

@app.route('/add_winner/<tournament_id>', methods=['GET', 'POST'])
@login_required
def add_winner(tournament_id):
    form = AddWinnerForm()
    user = current_user
    if user.role != 'Staff':
        flash('You are not authorised to add a winner.')
        return redirect(url_for('index'))

    tournament = Tournaments.query.filter_by(tournament_id=tournament_id).first_or_404()
    if tournament.winner:
        flash('This tournament already has a winner')
        return redirect(url_for('tournament', tournament_id=tournament_id))

    if form.validate_on_submit():
        winner = form.winner.data
        winner_id = User.query.filter_by(username=winner).first().user_id

        if winner_id == None:
            flash('User not found')
            return redirect(url_for('add_winner', tournament_id=tournament_id))

        tournament = Tournaments.query.filter_by(tournament_id=tournament_id).first()
        tournament.winner = winner_id
        db.session.commit()
        flash('Winner added successfully')
        return redirect(url_for('tournament', tournament_id=tournament_id))
    else:
        flash('Something went wrong. Please try again.')
        print(form.errors)
    return render_template('add_winner.html', title="Add Winner", form=form)


### MATCH HANDLING ###
@app.route('/match/<match_id>')
@login_required
def match(match_id):
    match = Matches.query.filter_by(match_id=match_id).first_or_404()
    tournament = Tournaments.query.filter_by(tournament_id=match.tournament_id).first()
    user = current_user

    # get players in match
    match_users = MatchUsers.query.filter_by(match_id=match_id).all()
    players = []
    for match_user in match_users:
        player = User.query.filter_by(user_id=match_user.match_user).first()
        players.append(player)


    return render_template('match.html', match=match, tournament=tournament, user=user, match_users=match_users, players=players)

@app.route('/add_match_details/<match_id>', methods=['GET', 'POST'])
@login_required
def add_match_details(match_id):
    form = AddMatchDetailsForm()

    # get the match and the tournament
    match = Matches.query.filter_by(match_id=match_id).first_or_404()
    tournament = Tournaments.query.filter_by(tournament_id=match.tournament_id).first()

    # get all players in the tournament
    tournament_users = TournamentUsers.query.filter_by(tournament_id=tournament.tournament_id).all()

    choices = []
    for user in tournament_users:
        user = User.query.filter_by(user_id=user.user_id).first()
        choices.append((user.user_id, user.username))

    form.player1.choices = choices
    form.player2.choices = choices
    print(form.player1.choices)
    print(form.player2.choices)

    if current_user.role != 'Staff':
        flash('You are not authorised to add match members.')
        return redirect(url_for('index'))

    if form.validate_on_submit():
        player1_id = form.player1.data
        player2_id = form.player2.data
        match_date = form.match_date.data

        player1 = User.query.filter_by(user_id=player1_id).first()
        player2 = User.query.filter_by(user_id=player2_id).first()

        if player1_id == player2_id:
            flash('Players cannot be the same')
            return redirect(url_for('add_match_details', match_id=match_id))

        ## ADD IF PLAYER IS ALREADY IN MATCH ##

        if player1 == None or player2 == None:
            flash('One or more players not found')
            return redirect(url_for('add_match_details', match_id=match_id))

        match_user1 = MatchUsers(match_id=match_id, match_user=player1_id)
        match_user2 = MatchUsers(match_id=match_id, match_user=player2_id)
        match.match_date = match_date
        print(match.match_date)



        db.session.add(match_user1)
        db.session.add(match_user2)
        db.session.add(match.match_date)
        db.session.commit()
        flash('Players added to match')
        return redirect(url_for('match', match_id=match_id))
    else:
        flash('Something went wrong. Please try again.')
        print(form.errors)

    return render_template('add_match_details.html', title="Add Match Members", form=form, choices=choices, match=match)

### PRACTISE HANDLING ###

### DATA CHECKING ###
@app.route('/check_data')
def check_data():
    for game in Games.query.all():
        # check if duplicate full data rows exist
        if Games.query.filter_by(game_title=game.game_title, platform=game.platform, year=game.year, genre=game.genre, publisher=game.publisher, global_sales=game.global_sales, sales_ranking=game.sales_ranking).count() > 1:
            print(game)
            print('Duplicate full data row')
    print("Done checking data integrity")
    return redirect(url_for('index'))

@app.route('/test_formulae')
def test_formulae():
    participants = 16
    rounds = int(math.log(participants, 2))
    print("NUMBER OF ROUNDS")
    print(rounds)

    for i in range(1, rounds+1):
        print("ROUND " + str(i))
        matches = int(participants / 2)
        print("Matches: " + str(matches))
        for j in range(1, matches+1):
            print("Match " + str(j))
        participants = participants / 2

    return redirect(url_for('index'))

