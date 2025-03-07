from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config['SECRET_KEY'] = 'your_secret_key'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Model User
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    is_blocked = db.Column(db.Boolean, default=False)  

# Model Task
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class BlockUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    submit = SubmitField('Block User')

class ResetPasswordForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    new_password = StringField('New Password', validators=[DataRequired()])
    submit = SubmitField('Reset Password')

# Tạo database
with app.app_context():
    db.create_all()

@app.route('/')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    tasks = Task.query.filter_by(user_id=current_user.id).paginate(page=page, per_page=per_page, error_out=False)
    return render_template('index.html', tasks=tasks)

@app.route('/add', methods=['POST'])
@login_required
def add():
    task_content = request.form['task']
    new_task = Task(content=task_content, user_id=current_user.id)
    db.session.add(new_task)
    db.session.commit()
    return redirect('/')

@app.route('/delete/<int:id>')
@login_required
def delete(id):
    task = Task.query.get_or_404(id)
    if task.user_id == current_user.id:
        db.session.delete(task)
        db.session.commit()
    return redirect('/')

@app.route('/edit', methods=['POST'])
@login_required
def edit():
    task_id = request.form['taskId']
    new_content = request.form['content']
    
    task = Task.query.get_or_404(task_id)
    if task.user_id == current_user.id:
        task.content = new_content
        db.session.commit()
    return redirect('/')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        if User.query.filter_by(username=username).first():
            flash('Tài khoản đã tồn tại!')
            return redirect(url_for('register'))

        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('Đăng ký thành công! Hãy đăng nhập.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    block_form = BlockUserForm()
    reset_form = ResetPasswordForm()

    

    if reset_form.validate_on_submit():
        user = User.query.filter_by(username=reset_form.username.data).first()
        if user:
            hashed_password = generate_password_hash(reset_form.new_password.data, method='pbkdf2:sha256')  # Hash mật khẩu mới trước khi lưu
            user.password = hashed_password
            db.session.commit()
            flash('Password has been reset', 'success')
        else:
            flash('User not found', 'danger')
        return redirect(url_for('admin'))
    
    if block_form.validate_on_submit():
        user = User.query.filter_by(username=block_form.username.data).first()
        if user:
            user.is_blocked = True
            db.session.commit()
            flash('User has been blocked', 'success')
        else:
            flash('User not found', 'danger')
        return redirect(url_for('admin'))
    
    users = User.query.all()
    return render_template('admin.html', block_form=block_form, reset_form=reset_form, users=users)



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if username == 'admin' and password == '123':
            return redirect(url_for('admin'))

        if user and user.is_blocked:
            flash('Your account has been blocked', 'danger')
            return redirect(url_for('login'))

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('index'))

        flash('Sai tài khoản hoặc mật khẩu!')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Bạn đã đăng xuất!')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
