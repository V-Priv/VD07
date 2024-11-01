from flask import render_template, request, redirect, url_for,flash
from flask_login import login_user, logout_user, current_user, login_required
from app.models import User
from app import app, db, bcrypt
from app.forms import RegistrationForm, LoginForm, UpdateAccountForm

@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html")


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        # Проверяем, существует ли пользователь с таким же email
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Этот email уже зарегистрирован. Пожалуйста, используйте другой.', 'danger')
            return redirect(url_for('register'))

        # Если email не занят, продолжаем регистрацию
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Вы успешно зарегистрировались', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('home'))
        else:
            flash('Введены неверные данные', 'danger')

    return render_template('login.html', form=form)


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        # Проверяем, изменил ли пользователь email
        if form.email.data != current_user.email:
            existing_user = User.query.filter_by(email=form.email.data).first()
            if existing_user:
                flash('Этот email уже зарегистрирован. Пожалуйста, используйте другой.', 'danger')
                return redirect(url_for('account'))

        # Обновляем данные пользователя
        current_user.username = form.username.data
        current_user.email = form.email.data

        # Проверяем, если пользователь ввел новый пароль
        if form.password.data:
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            current_user.password = hashed_password

        db.session.commit()

        flash('Ваш аккаунт был обновлен!', 'success')
        return redirect(url_for('profile'))

    # Заполняем форму текущими данными пользователя
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email

    return render_template('profile.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/profile')
@login_required
def account():
    return render_template('profile.html')
