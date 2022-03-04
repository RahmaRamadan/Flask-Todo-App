from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_required, LoginManager, current_user, logout_user
import os
from flask_bcrypt import Bcrypt


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
# ---------------------------Models--------------------------
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    complete = db.Column(db.Boolean)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(20), nullable=False)

# -------------------------home-----------------------------------


@app.route('/')
def index():
    # show all todos
    todo_list = Todo.query.all()
    print(todo_list)
    return render_template('base.html', todo_list=todo_list)

# ---------------------------login------------------------------------


@app.route('/login', methods=["POST", "GET"])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    # post
    user = User.query.filter_by(username=request.form.get('username')).first()
    if not user or user.password != request.form.get('password'):
        return render_template('login.html', errors=['username or password not found'])

    else:
        return redirect('/')

# -------------------------register-----------------------------------


@app.route('/register', methods=["POST", "GET"])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    # post
    all = User.query.all()
    user1 = User.query.filter_by(username=request.form.get('username')).first()
    if user1:
        return render_template('register.html', errors=['user already exists'])
    else:
        user = User(
            username=request.form.get('username'),
            password=request.form.get("password")
        )
        db.session.add(user)
        db.session.commit()
        return render_template('login.html')


# -------------------------logout-----------------------------------

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# -------------------------add-----------------------------------


@app.route('/add', methods=["POST"])
def add():
    title = request.form.get("title")
    new_todo = Todo(title=title, complete=False)
    db.session.add(new_todo)
    db.session.commit()
    return redirect(url_for("index"))

# -------------------------update---------------------------------


@app.route('/update/<int:todo_id>')
def update(todo_id):
    todo = Todo.query.filter_by(id=todo_id).first()
    todo.complete = not todo.complete
    db.session.commit()
    return redirect(url_for("index"))

# -------------------------delete---------------------------------


@app.route('/delete/<int:todo_id>')
def delete(todo_id):
    todo = Todo.query.filter_by(id=todo_id).first()
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for("index"))


# ------------------------------------------------------------
if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
