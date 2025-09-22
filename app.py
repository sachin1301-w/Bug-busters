from flask import Flask, render_template, request, redirect, url_for, session, flash
import config
import mysql.connector as connector
from werkzeug.utils import secure_filename
import os
from ultralytics import YOLO
import bcrypt
from collections import Counter
from dotenv import load_dotenv
from PIL import Image

dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)

# Load .env if needed
load_dotenv()

# ===============================================================
# >> NEW: CAR PRICE DATA DICTIONARY PLACED HERE <<
# ===============================================================
car_prices_data = {
    "HONDA": {
        "City": {"Bonnet": 15000, "Bumper": 10000, "Dickey": 8000, "Door": 20000, "Fender": 5000, "Light": 3000, "Windshield": 8000},
        "Amaze": {"Bonnet": 12000, "Bumper": 8000, "Dickey": 6000, "Door": 18000, "Fender": 4000, "Light": 2500, "Windshield": 7000},
        "WR-V": {"Bonnet": 16000, "Bumper": 11000, "Dickey": 9000, "Door": 22000, "Fender": 6000, "Light": 3500, "Windshield": 9000},
        "Jazz": {"Bonnet": 14000, "Bumper": 9000, "Dickey": 7000, "Door": 19000, "Fender": 4500, "Light": 2800, "Windshield": 8000},
        "HR-V": {"Bonnet": 18000, "Bumper": 12000, "Dickey": 10000, "Door": 24000, "Fender": 7000, "Light": 4000, "Windshield": 10000},
        "Pilot": {"Bonnet": 22000, "Bumper": 15000, "Dickey": 13000, "Door": 28000, "Fender": 8000, "Light": 5000, "Windshield": 12000},
        "CR-V": {"Bonnet": 20000, "Bumper": 13000, "Dickey": 11000, "Door": 26000, "Fender": 7500, "Light": 4500, "Windshield": 11000},
        "Accord": {"Bonnet": 22000, "Bumper": 15000, "Dickey": 13000, "Door": 28000, "Fender": 8000, "Light": 5000, "Windshield": 12000},
        "Civic": {"Bonnet": 18000, "Bumper": 12000, "Dickey": 10000, "Door": 24000, "Fender": 7000, "Light": 4000, "Windshield": 10000}
    },
    "MARUTI SUZUKI": {
        "Swift": {"Bonnet": 10000, "Bumper": 7000, "Dickey": 5000, "Door": 15000, "Fender": 3000, "Light": 2000, "Windshield": 6000},
        "Baleno": {"Bonnet": 12000, "Bumper": 8000, "Dickey": 6000, "Door": 18000, "Fender": 4000, "Light": 2500, "Windshield": 7000},
        "Vitara Brezza": {"Bonnet": 14000, "Bumper": 9000, "Dickey": 7000, "Door": 20000, "Fender": 4500, "Light": 2800, "Windshield": 8000},
        "Wagon R": {"Bonnet": 12000, "Bumper": 8000, "Dickey": 6000, "Door": 18000, "Fender": 4000, "Light": 2500, "Windshield": 7000},
        "Ertiga": {"Bonnet": 16000, "Bumper": 11000, "Dickey": 9000, "Door": 22000, "Fender": 6000, "Light": 3500, "Windshield": 9000},
        "Grand Vitara": {"Bonnet": 18000, "Bumper": 12000, "Dickey": 10000, "Door": 24000, "Fender": 7000, "Light": 4000, "Windshield": 10000}
    },
    "TOYOTA": {
        "Corolla": {"Bonnet": 20000, "Bumper": 13000, "Dickey": 11000, "Door": 26000, "Fender": 7500, "Light": 4500, "Windshield": 11000},
        "Camry": {"Bonnet": 22000, "Bumper": 15000, "Dickey": 13000, "Door": 28000, "Fender": 8000, "Light": 5000, "Windshield": 12000},
        "Fortuner": {"Bonnet": 25000, "Bumper": 17000, "Dickey": 15000, "Door": 30000, "Fender": 9000, "Light": 6000, "Windshield": 14000},
        "Innova": {"Bonnet": 23000, "Bumper": 16000, "Dickey": 14000, "Door": 29000, "Fender": 8500, "Light": 5500, "Windshield": 13000},
        "Yaris": {"Bonnet": 18000, "Bumper": 12000, "Dickey": 10000, "Door": 24000, "Fender": 7000, "Light": 4000, "Windshield": 10000}
    },
    "HYUNDAI": {
        "i20": {"Bonnet": 15000, "Bumper": 10000, "Dickey": 8000, "Door": 20000, "Fender": 5000, "Light": 3000, "Windshield": 8000},
        "Creta": {"Bonnet": 18000, "Bumper": 12000, "Dickey": 10000, "Door": 24000, "Fender": 7000, "Light": 4000, "Windshield": 10000},
        "Verna": {"Bonnet": 16000, "Bumper": 11000, "Dickey": 9000, "Door": 22000, "Fender": 6000, "Light": 3500, "Windshield": 9000},
        "Venue": {"Bonnet": 17000, "Bumper": 11500, "Dickey": 9500, "Door": 23000, "Fender": 6500, "Light": 3750, "Windshield": 9500},
        "Tucson": {"Bonnet": 20000, "Bumper": 13000, "Dickey": 11000, "Door": 26000, "Fender": 7500, "Light": 4500, "Windshield": 11000}
    },
    "NISSAN": {
        "Altima": {"Bonnet": 18000, "Bumper": 13000, "Dickey": 11000, "Door": 24000, "Fender": 7000, "Light": 4000, "Windshield": 10000},
        "Rogue": {"Bonnet": 20000, "Bumper": 14000, "Dickey": 12000, "Door": 26000, "Fender": 7500, "Light": 4500, "Windshield": 11000},
        "Sentra": {"Bonnet": 17000, "Bumper": 12000, "Dickey": 10000, "Door": 22000, "Fender": 6500, "Light": 3750, "Windshield": 9500},
        "Pathfinder": {"Bonnet": 18000, "Bumper": 13000, "Dickey": 11000, "Door": 24000, "Fender": 7000, "Light": 4000, "Windshield": 10000},
        "Titan": {"Bonnet": 20000, "Bumper": 14000, "Dickey": 12000, "Door": 26000, "Fender": 7500, "Light": 4500, "Windshield": 11000}
    },
    "SKODA": {
        "Octavia": {"Bonnet": 20000, "Bumper": 14000, "Dickey": 12000, "Door": 26000, "Fender": 7500, "Light": 4500, "Windshield": 11000},
        "Superb": {"Bonnet": 22000, "Bumper": 15000, "Dickey": 13000, "Door": 28000, "Fender": 8000, "Light": 5000, "Windshield": 12000},
        "Rapid": {"Bonnet": 18000, "Bumper": 12000, "Dickey": 10000, "Door": 24000, "Fender": 7000, "Light": 4000, "Windshield": 10000},
        "Kodiaq": {"Bonnet": 22000, "Bumper": 15000, "Dickey": 13000, "Door": 28000, "Fender": 8000, "Light": 5000, "Windshield": 12000},
        "Karoq": {"Bonnet": 19000, "Bumper": 13500, "Dickey": 11500, "Door": 25000, "Fender": 7250, "Light": 4250, "Windshield": 10500}
    }
}


app = Flask(__name__)
app.secret_key = "220838d7b8826c175083b8a1d69f801fa936bda827d8c2acb569809c088d5396"

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "models")
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
UPLOAD_IMAGE = os.path.join(STATIC_DIR, "uploaded_image.jpg")
DETECTED_IMAGE = os.path.join(STATIC_DIR, "detected_image.jpg")

# Ensure static folder exists
os.makedirs(STATIC_DIR, exist_ok=True)

# ---------------- Database Connection ----------------
def connect_to_db():
    try:
        connection = connector.connect(**config.mysql_credentials)
        return connection
    except connector.Error as e:
        print(f"Database connection error: {e}")
        return None

# ---------------- Home Route ----------------
@app.route('/')
def home():
    return render_template('index.html')

# ---------------- Signup Route ----------------
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name')
        password = request.form.get('password')
        email = request.form.get('email')
        vehicle_id = request.form.get('vehicleId')
        contact_number = request.form.get('phoneNumber')
        address = request.form.get('address')
        car_brand = request.form.get('carBrand')
        model_name = request.form.get('carModel')

        if not all([name, password, email, vehicle_id, contact_number, address, car_brand, model_name]):
            flash("All fields are required!", "error")
            return render_template('signup.html')

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        connection = connect_to_db()
        if connection:
            try:
                with connection.cursor() as cursor:
                    query = """
                    INSERT INTO user_info (name, password, email, vehicle_id, contact_number, address, car_brand, model)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(query, (name, hashed_password, email, vehicle_id, contact_number, address, car_brand, model_name))
                    connection.commit()

                session['user_email'] = email
                flash("Signup successful!", "success")
                return redirect(url_for('dashboard'))

            except connector.IntegrityError as e:
                if 'Duplicate entry' in str(e):
                    flash("Email already exists. Please use a different email.", "error")
                else:
                    flash("Error during signup. Please try again.", "error")
            except connector.Error as e:
                print(f"Query error: {e}")
                flash("Error during signup. Please try again.", "error")
            finally:
                connection.close()
        else:
            flash("Database connection failed.", "error")

    return render_template('signup.html')

# ---------------- Login Route ----------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            flash("Email and password are required!", "error")
            return render_template('login.html')

        connection = connect_to_db()
        if connection:
            try:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT password FROM user_info WHERE email = %s", (email,))
                    result = cursor.fetchone()
                    if result and bcrypt.checkpw(password.encode('utf-8'), result[0].encode('utf-8')):
                        session['user_email'] = email
                        flash("Login successful!", "success")
                        return redirect(url_for('dashboard'))
                    else:
                        flash("Invalid email or password.", "error")
            except connector.Error as e:
                print(f"Query error: {e}")
                flash("Login error. Try again.", "error")
            finally:
                connection.close()
        else:
            flash("Database connection failed.", "error")

    return render_template('login.html')

# ---------------- Logout Route ----------------
@app.route('/logout')
def logout():
    session.pop('user_email', None)
    flash("Logged out successfully.", "info")
    return redirect(url_for('login'))

# ---------------- YOLO Model Load ----------------
model_path = os.path.join(MODELS_DIR, "best.pt")
model = YOLO(model_path)

# ---------------- Dashboard Route ----------------
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user_email' not in session:
        flash('Login required to access dashboard.', 'error')
        return redirect(url_for('login'))

    if request.method == 'POST':
        file = request.files.get('image')
        if not file:
            flash('Please upload an image.', 'error')
            return render_template('dashboard.html')

        filename = secure_filename(file.filename)
        if not filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            flash('Invalid file type. Please upload an image.', 'error')
            return render_template('dashboard.html')

        file.save(UPLOAD_IMAGE)

        # YOLO Prediction
        result = model(UPLOAD_IMAGE)
        detected_objects = result[0].boxes
        class_ids = [box.cls.item() for box in detected_objects]
        class_counts = Counter(class_ids)

        # Save detection image
        # Note: The plot function was changed in newer ultralytics versions. 
        # The following is a more robust way to save the plotted image.
        res_plotted = result[0].plot()
        pil_img = Image.fromarray(res_plotted)
        pil_img.save(DETECTED_IMAGE)

        # Fetch part prices
        part_prices = get_part_prices(session['user_email'], class_counts)

        return render_template('estimate.html',
                               original_image='uploaded_image.jpg',
                               detected_image='detected_image.jpg',
                               part_prices=part_prices)

    return render_template('dashboard.html')

# ===============================================================
# >> MODIFIED: THIS FUNCTION WAS REPLACED <<
# ===============================================================
# ---------------- Helper: Get Part Prices ----------------
def get_part_prices(email, class_counts):
    # Step 1: Get the user's car brand and model from the database
    connection = connect_to_db()
    if not connection:
        return {}

    car_brand = None
    car_model = None
    try:
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT car_brand, model FROM user_info WHERE email = %s", (email,))
            user_data = cursor.fetchone()
            if user_data:
                car_brand = user_data['car_brand']
                car_model = user_data['model']
    except connector.Error as e:
        print(f"DB error fetching user car: {e}")
        return {}
    finally:
        if connection.is_connected():
            connection.close()

    if not car_brand or not car_model:
        return {}

    # Step 2: Look up prices in the car_prices_data dictionary
    prices = {}
    for class_id, count in class_counts.items():
        part_name = get_part_name_from_id(class_id)
        if part_name:
            try:
                # Find the price in our dictionary
                price_per_part = car_prices_data[car_brand.upper()][car_model][part_name]
                total_price = price_per_part * count
                prices[part_name] = {'count': count, 'price': price_per_part, 'total': total_price}
            except KeyError:
                # This will catch errors if the brand, model, or part isn't in the dictionary
                print(f"Price not found for: {car_brand}, {car_model}, {part_name}")
                continue
    
    return prices

# ---------------- Helper: Map Class ID to Part Name ----------------
def get_part_name_from_id(class_id):
    class_names = ['Bonnet', 'Bumper', 'Dickey', 'Door', 'Fender', 'Light', 'Windshield']
    if 0 <= class_id < len(class_names):
        return class_names[int(class_id)]
    return None

# ---------------- Main ----------------
if __name__ == '__main__':
    app.run(debug=True)