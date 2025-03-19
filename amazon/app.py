from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Secret key for flash messages
app.secret_key = "your_secret_key"

# Ensure the instance folder exists
os.makedirs(app.instance_path, exist_ok=True)

# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db = SQLAlchemy(app)

# Define User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

# ✅ Ensure the database exists
with app.app_context():
    db.create_all()

# Route to render the signup form
@app.route('/')
def signup():
    return render_template('index.html')

# Route to handle form submission
@app.route('/register', methods=['POST'])
def register():
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']
    password_check = request.form['password-check']

    # ✅ Password validation
    if len(password) < 6:
        flash("Password must be at least 6 characters long", "error")
        return redirect(url_for('signup'))
    
    if password != password_check:
        flash("Passwords do not match!", "error")
        return redirect(url_for('signup'))

    # ✅ Check if email is already registered
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        flash("Email is already registered!", "error")
        return redirect(url_for('signup'))

    # ✅ Create new user
    new_user = User(name=name, email=email, password=password)
    db.session.add(new_user)
    db.session.commit()

    flash("Account created successfully!", "success")
    return redirect(url_for('signup'))  # Redirect to signup page after registration

@app.route('/templates/assets/<path:filename>')
def serve_templates_assets(filename):
    return send_from_directory('templates/assets', filename)

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
