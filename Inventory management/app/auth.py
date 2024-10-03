from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from app.models import User
from app import bcrypt, db
from app.form import LoginForm, SignupForm


auth = Blueprint('auth',__name__)
 
@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()  # Create a LoginForm instance
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('views.home'))
        else:
            flash('Login unsuccessful. Please check email and password', 'danger')
    
    return render_template('login.html', form=form)  # Pass the form to the template


@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        
        # Check if the username or email is already taken
        existing_user_username = User.query.filter_by(username=form.username.data).first()
        existing_user_email = User.query.filter_by(email=form.email.data).first()
        
        if existing_user_username:
            flash("Username already exists. Please choose another username.", 'danger')
            return redirect(url_for('auth.signup'))
        elif existing_user_email:
            flash("Email already exists. Please choose another email.", 'danger')
            return redirect(url_for('auth.signup'))
        
        # If the username and email are unique, proceed to create the new user
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Your account has been created!', 'success')
        return redirect(url_for('auth.login'))
      # Flash errors if validation fails
    for field_name, errors in form.errors.items():
        for error in errors:
            flash(f"{error}", 'danger')
    
    return render_template('signup.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
