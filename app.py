from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User, Feedback
from forms import RegisterForm, LoginForm
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgres:///flask_feedback"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "abc123"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

connect_db(app)

toolbar = DebugToolbarExtension(app)

@app.route('/')
def home_page():
    return redirect('/register')

@app.route('/register', methods=['GET', 'POST'])
def register_user():

    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data

        new_user = User.register(username, password, email, first_name, last_name)
        
        db.session.add(new_user)

        try:
            db.session.commit()
        except IntegrityError:
            form.username.errors.append('Username taken. Please pick another username.')
            return render_template('register.html', form=form)


        session['username'] = new_user.username
        return redirect('/secret')

    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login_user():

    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)
        if user:
            flash(f'Welcome Back {user.username}!', 'success')
            session['username'] = user.username
            return redirect('/secret')
        else:
            form.username.errors = ['Invalid username or password']
    return render_template('login.html', form=form)

@app.route('/logout')
def logout_user():
    session.pop('username')
    flash(f'{username} successfully logged out.', 'info')
    return redirect('/')

@app.route('/secret')
def show_secret():
    if 'username' not in session:
        flash('Please login first.', 'danger')
        return redirect('/')
    return render_template('secret.html')

@app.route('/users/<username>')
def show_information(username):
    if 'username' not in session:
        flash('Please login before continuing.', 'danger')
        return redirect('/login')
    if session['username'] == username:
        user = User.query.filter_by(username=username).first()
        return render_template('info.html', user=user)
    return redirect('/')

@app.route('/users/<username>/delete', methods=['POST'])
def delete_user(username):
    if 'username' not in session:
        flash('Please login before continuing.', 'info')
        return ('/login')

    if session['username'] == username:
        user = User.query.filter_by(username=username).first()
        db.session.delete('username')
        db.session.commit()
        flash(f'{username} has deleted their account.', 'success')
        return redirect('/')
    
    flash('Your account does not have permission to do that.', 'info')
    return redirect('/')