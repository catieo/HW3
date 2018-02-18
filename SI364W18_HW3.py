## SI 364 - Winter 2018
## HW 3

####################
## Import statements
####################

from flask import Flask, render_template, session, redirect, url_for, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, ValidationError
from wtforms.validators import Required, Length
from flask_sqlalchemy import SQLAlchemy

############################
# Application configurations
############################
app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string from si364'
## TODO 364: Create a database in postgresql in the code line below, and fill in your app's database URI. It should be of the format: postgresql://localhost/YOUR_DATABASE_NAME

## Your final Postgres database should be your uniqname, plus HW3, e.g. "jczettaHW3" or "maupandeHW3"
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://catieo@localhost/catieoHW3"
## Provided:
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

##################
### App setup ####
##################
db = SQLAlchemy(app) # For database use


#########################
#########################
######### Everything above this line is important/useful setup,
## not problem-solving.##
#########################
#########################

#########################
##### Set up Models #####
#########################
class Tweet(db.Model):
    __tablename__ = "tweets"
    tweetId = db.Column(db.Integer, primary_key = True)
    text = db.Column(db.String(280))
    user_id = db.Column(db.Integer, db.ForeignKey('users.userId'))

    def __repr__(self):
        return "{} (ID: {})".format(self.text, self.tweetId)

class User(db.Model):
    __tablename__ = "users"
    userId = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    display_name = db.Column(db.String(124))
    tweets = db.relationship('Tweet', backref='User')

    def __repr__(self):
        return "{} | ID: {}".format(self.username, self.userId)


########################
##### Set up Forms #####
########################

class TweetForm(FlaskForm):
    text = StringField('Enter the text of the tweet (no more than 280 chars):', validators=[Required(), Length(max=280, message="Tweet must not be more than 280 characters.")])
    username = StringField('Enter the username of the twitter user (no "@"!):', validators=[Required(), Length(max=64, message="Username must not be more than 64 characters.")])
    display_name = StringField('Enter the display name for the twitter user (must be at least 2 words):', validators=[Required(), ])
    submit = SubmitField('Submit')

    def validate_username(self, field):
        if field.data[0] == '@':
             raise(ValidationError("Don't start your username with @!"))

    def validate_display_name(self, field):
        split_name = field.data.split()
        if len(split_name) < 2:
            raise(ValidationError("Display name must be two words."))

###################################
##### Routes & view functions #####
###################################

## Error handling routes - PROVIDED
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

#############
## Main route
#############

@app.route('/', methods=['GET', 'POST'])
def index():
    form = TweetForm()
    num_tweets = len(Tweet.query.all())
    if form.validate_on_submit():
        tweet = form.text.data
        username = form.username.data
        display_name = form.display_name.data
        user = User.query.filter_by(username=username).first()
        if user:
            print("User exists!")
        else:
            user = User(username=username, display_name=display_name)
            db.session.add(user)
            db.session.commit()
        user_id = user.userId
        if Tweet.query.filter_by(user_id=user_id, text=tweet).first():
            return redirect(url_for('see_all_tweets'))
        t = Tweet(text = tweet, user_id = user_id)
        db.session.add(t)
        db.session.commit()
        print("Tweet successfully added to database.")
        return redirect(url_for('index'))
    # PROVIDED: If the form did NOT validate / was not submitted
    errors = [v for v in form.errors.values()]
    if len(errors) > 0:
        flash("!!!! ERRORS IN FORM SUBMISSION - " + str(errors))
    return render_template('index.html', num_tweets=num_tweets, form=form) # TODO 364: Add more arguments to the render_template invocation to send data to index.html

@app.route('/all_tweets')
def see_all_tweets():
    tweet_list = Tweet.query.all()
    all_tweets = []
    for tweet in tweet_list:
        user = User.query.filter_by(userId=tweet.user_id).first()
        temp = (tweet.text, user.username)
        all_tweets.append(temp)
    return render_template('all_tweets.html', all_tweets=all_tweets)


@app.route('/all_users')
def see_all_users():
    users = User.query.all()
    return render_template('all_users.html', users=users)


@app.route('/longest_tweet')
def get_longest_tweet():
    tweet_list = Tweet.query.all()
    longest_tweets = {}
    for tweet in tweet_list:
        count = 0
        whitespace = " "
        for ch in tweet.text:
            if ch != whitespace:
                count += 1
        longest_tweets[tweet.text] = count
    sorted_longest_tweets = sorted(longest_tweets.items(), key = lambda x: x[1], reverse=True)
    text = sorted_longest_tweets[0][0]
    longest_tweet = Tweet.query.filter_by(text=text).first()
    u = User.query.filter_by(userId = longest_tweet.user_id).first()
    user = u.username
    return render_template('longest_tweet.html', text=text, user=user)
# NOTE:
# This view function should compute and render a template (as shown in the sample application) that shows the text of the tweet currently saved in the database which has the most NON-WHITESPACE characters in it, and the username AND display name of the user that it belongs to.
# NOTE: This is different (or could be different) from the tweet with the most characters including whitespace!
# Any ties should be broken alphabetically (alphabetically by text of the tweet). HINT: Check out the chapter in the Python reference textbook on stable sorting.
# Check out /longest_tweet in the sample application for an example.

# HINT 2: The chapters in the Python reference textbook on:
## - Dictionary accumulation, the max value pattern
## - Sorting
# may be useful for this problem!


if __name__ == '__main__':
    db.create_all() # Will create any defined models when you run the application
    app.run(use_reloader=True,debug=True) # The usual
