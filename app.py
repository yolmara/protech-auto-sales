import os
import uuid

from flask import (Flask, flash, redirect, render_template, request, session,
                   url_for)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'coder.03'

# Configure database
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Upload Settings
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# instantiate the database
db = SQLAlchemy(app)

# Define the Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(30), nullable=False) #m.facebook.com/profile.php?id=330743793448238


class Car(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String(500), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    price = db.Column(db.String(50), nullable=False)

#----------------------------------------------------------------------------------------------------------------------------------------
# Home page
@app.route('/')
def home():
    return render_template('index.html')

# Cars page
@app.route('/cars')
def show_cars():
    cars = Car.query.all()
    return render_template('cars.html', cars=cars)

# Contact Page
@app.route('/contact')
def contact():
    return render_template('contact.html')

# add-test-cars
#@app.route('/add-test-cars')
#def add_test_cars():
    # Check if test data already exists
    #if Car.query.first():
        #return "⚠️ Test data already exists."

        
    # Sample cars
    #car1 = Car(image='uploads\bmwM2.jpg', description='2017 BMW-M2 - 580hp - Great condition', price='$68000')
    #car2 = Car(image='uploads\cedes_hatchback.jpg', description='2013 blue mercedes hatchback', price='$35000')
    #car3 = Car(image='uploads\vintageblue.jpg', description='Classic Vintage - excellent condition', price='$102000')

    # Add to database
    #db.session.add_all([car1, car2, car3, car4])
    #db.session.commit()

    #return  "✅ Test cars added!"

# Clear car database
@app.route('/clear-cars')
def clear_cars():
    db.session.query(Car).delete()
    db.session.commit()
    return 'All Car records deleted'

# Upload route
@app.route('/0a-8d-6m-4i-2n-upload-url', methods=['GET', 'POST'])
def upload():
    if 'user_id' not in session:
        flash('You must be logged in to view the upload page')
        return redirect(url_for('admin_login'))

    if request.method == 'POST':
        image_url = request.form['image']  # URL from Uploadcare
        description = request.form['description']
        price = request.form['price']

        if image_url and description and price:
            new_car = Car(image=image_url, description=description, price=price)
            db.session.add(new_car)
            db.session.commit()

            flash('🚗 Car added successfully')
            return redirect(url_for('show_cars'))

        flash('❌ Missing fields.')

    return render_template('upload.html')


# Admin Registration
SECRET_KEY = 'protech_25'

@app.route(f'/register-{SECRET_KEY}', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password)

        # Process Registration
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already taken!')
            return redirect(url_for('admin_login'))
        
        new_user = User(username=username, password = hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('registered Successfully')
        return redirect(url_for('admin_login'))
    
    return render_template('registration.html')


# Admin Login
@app.route('/ptac-admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash('Login Successful!')
            return redirect(url_for('upload'))
        else:
            flash('Incorrect username or password')
            return redirect(url_for('admin_login'))
    
    return render_template('login.html')

# Admin Logout
@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    flash('Logged out')

    return redirect(url_for('admin_login'))

@app.route('/delete-cars', methods=['GET', 'POST'])
def delete_cars():
    if 'user_id' not in session:
        flash('You must be logged in to delete images')
        return redirect(url_for('admin_login'))

    cars = Car.query.all()

    if request.method == 'POST':
        car_ids = request.form.getlist('car_ids')
        for car_id in car_ids:
            delete_car = Car.query.get(car_id)
            if delete_car:
                # Delete image file from filesystem
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], os.path.basename(delete_car.image))
                if os.path.exists(image_path):
                    os.remove(image_path)
                # Delete database record
                db.session.delete(delete_car)
        db.session.commit()
        flash('Selected cars deleted successfully')
        return redirect(url_for('upload'))

    return render_template('delete_cars.html', cars=cars)

#Delete Users
@app.route('/delete-users', methods=['GET','POST'])
def delete_users():
    if 'user_id' not in session:
        flash('You must be logged in to delete users')
        return redirect(url_for('admin_login'))

    users = User.query.all()

    if request.method == 'POST':
        user_ids = request.form.getlist('user_ids')

        for user_id in user_ids:
            user = User.query.get(user_id)
            if user:
                db.session.delete(user)
        db.session.commit()
        flash('Selected Users deleted Successfully!')
        return redirect(url_for('delete_users'))

    return render_template('delete_users.html', users=users)

# Delete Selected Cars Route
#@app.route('/delete-selected-cars', methods=['GET','POST'])
#def delete_selected_cars():
#    if request.method == 'POST':
#        car_ids = request.form.getlist('car_ids')
#        for car_id in car_ids:
#            delete_car = Car.query.get('car_id')
#            if delete_car:
#                db.session.delete(delete_car)
#        db.session.commit()
#        flash('Selected Cars Deleted Successfully')
#        return redirect(url_for('show_cars'))
#    return redirect(url_for('delete_cars'))

@app.route('/test-db')
def test_db():
    try:
        # Try querying the database
        users = User.query.all()
        return f"✅ Connected to DB. Users found: {len(users)}"
    except Exception as e:
        return f"❌ Database Error: {str(e)}"

@app.route('/init-db')
def init_db():
    try:
        db.create_all()
        return '✅ Database initialized!'
    except Exception as e:
        return f'❌ Error: {e}'


if __name__ == '__main__':

    with app.app_context():
        db.create_all()

    app.run(debug=True)
