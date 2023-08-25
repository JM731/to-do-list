from flask import Flask, render_template, redirect, url_for, flash, abort
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
import datetime
import pytz
import os
from forms import SignUpForm, LogInForm, AddTaskForm, TimezoneForm

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL", 'sqlite:///users.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)


class ToDoList(db.Model):
    __tablename__ = "to_do_list"
    id = db.Column(db.Integer, primary_key=True)
    user = relationship("User", back_populates='list')
    user_id = db.Column(db.Integer, ForeignKey('user.id'))
    name = db.Column(db.String(250), nullable=False)
    is_done = db.Column(db.Boolean, nullable=False)
    date = db.Column(db.DateTime, nullable=False)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(250), nullable=False)
    password = db.Column(db.String(250), nullable=False)
    timezone = db.Column(db.String(250), nullable=False)
    list = relationship("ToDoList", back_populates='user')


with app.app_context():
    db.create_all()


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


@app.route("/")
def home():
    return redirect(url_for("sign_up"))


@app.route("/register", methods=["GET", "POST"])
def sign_up():
    form = SignUpForm()
    if form.validate_on_submit():
        if db.session.query(User).filter_by(username=form.username.data).first():
            flash('This username is already in use.', 'username_in_use')
        elif form.password.data == form.password2.data:
            new_user = User(
                username=form.username.data,
                password=generate_password_hash(form.password.data, method='pbkdf2:sha256', salt_length=8),
                timezone="Europe/London"
            )
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for('to_do_list'))
        else:
            flash('Your password does not match.', 'passwords_match')
    return render_template("authenticate.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LogInForm()
    if form.validate_on_submit():
        log_user = db.session.query(User).filter_by(username=form.username.data).first()
        if log_user is None:
            flash("Invalid username.", "invalid_username")
        elif check_password_hash(log_user.password, form.password.data):
            login_user(log_user)
            return redirect(url_for('to_do_list'))
        else:
            flash('Wrong password.', 'wrong_password')
    return render_template("authenticate.html", form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route("/to-do-list", methods=["GET", "POST"])
@login_required
def to_do_list():
    task_form = AddTaskForm()
    timezone_form = TimezoneForm(timezone=current_user.timezone)
    if timezone_form.validate_on_submit():
        current_user.timezone = timezone_form.timezone.data
        db.session.commit()
    if task_form.validate_on_submit():
        new_task = ToDoList(user=current_user,
                            name=task_form.task_name.data,
                            is_done=False,
                            date=task_form.task_date.data)
        db.session.add(new_task)
        db.session.commit()
        return redirect(url_for('to_do_list'))
    utc_now = datetime.datetime.now(pytz.utc)
    user_timezone = pytz.timezone(current_user.timezone)
    user_now = utc_now.astimezone(user_timezone)
    user_now = user_now.replace(tzinfo=None)
    current_user_tasks = db.session.query(ToDoList).filter_by(user_id=current_user.id).all()
    return render_template("to_do_list.html",
                           tasks=current_user_tasks,
                           now=user_now,
                           form=task_form,
                           timezone_form=timezone_form)


@app.route("/delete-task/<id_>")
@login_required
def delete_task(id_):
    task = db.session.query(ToDoList).get(id_)
    if task:
        if task.user_id == current_user.id:
            db.session.delete(task)
            db.session.commit()
            return redirect(url_for('to_do_list'))
        return abort(403)
    return abort(404)


@app.route("/mark-task-done/<id_>")
@login_required
def mark_task_done(id_):
    task = db.session.query(ToDoList).get(id_)
    if task:
        if task.user_id == current_user.id:
            task.is_done = not task.is_done
            db.session.commit()
            return redirect(url_for('to_do_list'))
        return abort(403)
    return abort(404)


if __name__ == "__main__":
    app.run()
