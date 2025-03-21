from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.secret_key = "your_secret_key"


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite' 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Create a table in database
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)

with app.app_context():
    db.create_all()

# To route sign up page
@app.route('/signup')
def signup():
    return render_template('signup.html')

# To route home page
@app.route('/')
def home():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        return render_template('index.html', user=user)
    else:
        return render_template('index.html')
    
# to handle the sign up form submission
@app.route('/register', methods=['POST'])
def register():
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']
    password_check = request.form['password-check']

    if len(password) < 6:
        flash("Password must be at least 6 characters long", "error")
        return redirect(url_for('signup'))

    if password != password_check:
        flash("Passwords do not match!", "error")
        return redirect(url_for('signup'))

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        flash("Email is already registered!", "error")
        return redirect(url_for('signup'))

    hashed_password = generate_password_hash(password)
    new_user = User(name=name, email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    flash("Account created successfully!", "success")
    return redirect(url_for('login'))

# handle the login form submission
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash("Login successful!", "success")
            return redirect(url_for('home'))
        else:
            flash("Invalid email or password", "error")
            return render_template('login.html')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash("Logged out successfully!", "info")
    return redirect(url_for('home'))

@app.route('/templates/assets/<path:filename>')
def serve_templates_assets(filename):
    return send_from_directory('templates/assets', filename)

if __name__ == '__main__':
    app.run(debug=True)