from flask import Flask,render_template, redirect, url_for, flash, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text
from form import AddTasksForm,EditTasksForm
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
import os
from dotenv import load_dotenv


load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    DEBUG = os.getenv('FLASK_ENV') == 'development'

app=Flask(__name__)

app.config.from_object(Config)
Bootstrap5(app)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    tasks = db.relationship('Tasks', backref='user', lazy=True)
   


class Tasks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_name = db.Column(db.String(250), unique=False)
    date = db.Column(db.String(250), nullable=False)
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
@app.route('/')
def home():
    return render_template('index.html')


@app.route("/tasks")
@login_required
def get_all_tasks():
    tasks = Tasks.query.filter_by(user_id=current_user.id).all()  # Retrieve tasks associated with the current user
    return render_template("tasks.html", all_tasks=tasks, current_user=current_user)


@app.route("/add", methods=["GET", "POST"])
@login_required
def new_task():
    form = AddTasksForm()
    if form.validate_on_submit():
        new_task = Tasks(
            task_name=form.task_name.data,
            date=date.today().strftime("%B %d, %Y"),
            user_id=current_user.id  # Set the user_id to the current user's id
        )
        db.session.add(new_task)
        db.session.commit()
        return redirect(url_for("get_all_tasks"))
    return render_template("add.html", form=form, current_user=current_user)

@app.route("/delete/<int:task_id>")
@login_required
def delete_task(task_id):
    task_to_delete = db.get_or_404(Tasks,task_id)
    db.session.delete(task_to_delete)
    db.session.commit() 
    return redirect(url_for('get_all_tasks'))


        
@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        result = db.session.execute(db.select(User).where(User.email == email))
        user = result.scalar()
        if not user:
            flash("That email does not exist, please signup.", 'warning')
            return redirect(url_for('login'))
        elif not check_password_hash(user.password, password):
            flash('Password incorrect, please try again.', 'danger')
            return redirect(url_for('login'))
        else:
            login_user(user)
            flash('Logged in successfully.', 'success')
            return redirect(url_for('get_all_tasks'))
    return render_template("login.html", current_user=current_user)



@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get('email')
        result = db.session.execute(db.select(User).where(User.email == email))
        user = result.scalar()
        if user:
            flash("You've already signed up with that email, log in instead!", 'error')
            return redirect(url_for('login'))
        hash_and_salted_password = generate_password_hash(
            request.form.get('password'),
            method='pbkdf2:sha256',
            salt_length=8
        )
        new_user = User(
            email=request.form.get('email'),
            password=hash_and_salted_password,
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        flash("Registration successful! You are now logged in.", 'success')
        return redirect(url_for("get_all_tasks"))
    return render_template("register.html", current_user=current_user)




@app.route("/edit/<int:task_id>", methods=["GET", "POST"])
@login_required
def edit_task(task_id):
    task_to_update = db.get_or_404(Tasks, task_id)  
    form=EditTasksForm()
    if form.validate_on_submit():
        task_to_update.task_name =form.task_name.data
        db.session.add(task_to_update)
        db.session.commit()
        return redirect(url_for('get_all_tasks', task_id=task_id)) 
    form.task_name.data=task_to_update.task_name
    return render_template('edit.html',form=form, current_user=current_user)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run()
