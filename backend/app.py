from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
import joblib
import numpy as np
import os
from datetime import datetime

try:
    from flask_cors import CORS
    CORS_AVAILABLE = True
except ImportError:
    CORS_AVAILABLE = False

from database import db, User, Prediction

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, "predictions.db")

app = Flask(
    __name__,
    template_folder="../frontend/templates",
    static_folder="../frontend/static"
)

# Configuration
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DATABASE_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_PERMANENT'] = True
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = 86400

# Initialize database
db.init_app(app)

# Fix SQLite foreign key support
from sqlalchemy import event
from sqlalchemy.pool import Pool

@event.listens_for(Pool, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    if 'sqlite' in str(dbapi_conn):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

# Enable CORS for API requests if available
if CORS_AVAILABLE:
    CORS(app)

# Create database tables
with app.app_context():
    db.create_all()
    print("Database initialized")

# Project type mapping
PROJECT_TYPE_MAP = {
    'software': 0,
    'construction': 1,
    'hybrid': 2
}

# Load models and encoders
try:
    # Construction models
    cost_model = joblib.load(os.path.join(BASE_DIR, "cost_model.pkl"))
    time_model = joblib.load(os.path.join(BASE_DIR, "time_model.pkl"))
    policy_encoder = joblib.load(os.path.join(BASE_DIR, "policy_reason_encoder.pkl"))
    
    # Software models
    software_effort_gb_model = joblib.load(os.path.join(BASE_DIR, "software_effort_gb_model.pkl"))
    software_effort_rf_model = joblib.load(os.path.join(BASE_DIR, "software_effort_rf_model.pkl"))
    print("All models and encoders loaded successfully")
except Exception as e:
    print(f"Error loading models: {e}")
    print("Please run train_model.py and train_software_effort_model.py first to generate models")
    cost_model = None
    time_model = None
    policy_encoder = None
    software_effort_gb_model = None
    software_effort_rf_model = None

# Effort range for clipping (optional; run train_software_effort_model.py to create)
software_effort_range = None
try:
    software_effort_range = joblib.load(os.path.join(BASE_DIR, "software_effort_range.pkl"))
except Exception:
    pass

# Helper function to check if user is logged in
def is_logged_in():
    return 'user_id' in session

# Helper function to require login
def require_login():
    if not is_logged_in():
        return jsonify({"error": "Authentication required"}), 401
    return None

# Routes
@app.route("/")
def home():
    if is_logged_in():
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        data = request.json if request.is_json else request.form
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username or not password:
            if request.is_json:
                return jsonify({"error": "Username and password required"}), 400
            flash("Username and password required", "error")
            return redirect(url_for('login'))
        
        try:
            user = User.query.filter_by(username=username).first()
            
            if user and user.check_password(password):
                session.permanent = True
                session['user_id'] = user.id
                session['username'] = user.username
                if request.is_json:
                    return jsonify({"success": True, "message": "Login successful"})
                return redirect(url_for('dashboard'))
            else:
                if request.is_json:
                    return jsonify({"error": "Invalid username or password"}), 401
                flash("Invalid username or password", "error")
                return redirect(url_for('login'))
        except Exception as e:
            print(f"Login error: {e}")
            if request.is_json:
                return jsonify({"error": "Login failed. Please try again."}), 500
            flash("Login failed. Please try again.", "error")
            return redirect(url_for('login'))
    
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        data = request.json if request.is_json else request.form
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        # Validation
        if not username or not email or not password:
            if request.is_json:
                return jsonify({"error": "All fields are required"}), 400
            flash("All fields are required", "error")
            return redirect(url_for('register'))
        
        if len(password) < 6:
            if request.is_json:
                return jsonify({"error": "Password must be at least 6 characters"}), 400
            flash("Password must be at least 6 characters", "error")
            return redirect(url_for('register'))
        
        try:
            # Check if user already exists
            if User.query.filter_by(username=username).first():
                if request.is_json:
                    return jsonify({"error": "Username already exists"}), 400
                flash("Username already exists", "error")
                return redirect(url_for('register'))
            
            if User.query.filter_by(email=email).first():
                if request.is_json:
                    return jsonify({"error": "Email already exists"}), 400
                flash("Email already exists", "error")
                return redirect(url_for('register'))
            
            # Create new user
            user = User(username=username, email=email)
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            session.permanent = True
            session['user_id'] = user.id
            session['username'] = user.username
            
            if request.is_json:
                return jsonify({"success": True, "message": "Registration successful"})
            return redirect(url_for('dashboard'))
        except Exception as e:
            db.session.rollback()
            print(f"Registration error: {e}")
            if request.is_json:
                return jsonify({"error": "Registration failed"}), 500
            flash("Registration failed. Please try again.", "error")
            return redirect(url_for('register'))
    
    return render_template("register.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route("/dashboard")
def dashboard():
    if not is_logged_in():
        return redirect(url_for('login'))
    return render_template("index.html")

@app.route("/predict-software")
def predict_software():
    """Render software effort prediction page"""
    if not is_logged_in():
        return redirect(url_for('login'))
    return render_template("software_effort.html")

@app.route("/predict-construction")
def predict_construction():
    """Render construction cost prediction page"""
    if not is_logged_in():
        return redirect(url_for('login'))
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    # Check authentication
    auth_error = require_login()
    if auth_error:
        return auth_error
    
    try:
        data = request.json
        project_type = data.get("project_type", "").lower()

        if project_type == "construction":
            if cost_model is None or time_model is None:
                return jsonify({"error": "Construction models not loaded. Please train models first."}), 500

            # Validate required fields for construction project (must match construction_dataset.csv)
            required_fields = [
                "project_size_sqft",
                "num_workers",
                "material_quality",
                "project_complexity",
                "equipment_count",
                "team_experience_years",
            ]
            for field in required_fields:
                if field not in data:
                    return jsonify({"error": f"Missing required field: {field}"}), 400

            # Create feature array in the same order as training
            features = np.array([[
                float(data["project_size_sqft"]),
                float(data["num_workers"]),
                float(data["material_quality"]),
                float(data["project_complexity"]),
                float(data["equipment_count"]),
                float(data["team_experience_years"]),
            ]])

            # Make predictions
            cost = cost_model.predict(features)[0]
            time = time_model.predict(features)[0]

            # Save prediction to database
            try:
                prediction = Prediction(
                    user_id=session['user_id'],
                    project_type='construction',
                    project_size=float(data.get("project_size_sqft", 0)),
                    team_size=int(data.get("num_workers", 0)),
                    experience=float(data.get("team_experience_years", 0)),
                    complexity=int(data.get("project_complexity", 0)),
                    risk_factor=float(data.get("material_quality", 0)),
                    estimated_budget=cost,
                    predicted_cost=cost,
                    predicted_time=time,
                )
                db.session.add(prediction)
                db.session.commit()
            except Exception as e:
                print(f"Error saving prediction: {e}")
                db.session.rollback()

            return jsonify({
                "success": True,
                "predicted_cost": round(cost, 2),
                "predicted_time": round(time, 2)
            })

        elif project_type == "software":
            if software_effort_gb_model is None:
                return jsonify({"error": "Software effort models not loaded. Please train models first."}), 500

            # Validate required fields for software project
            required_fields = ["team_exp", "manager_exp", "transactions", "entities",
                              "points_non_adjust", "adjustment", "language_level"]
            for field in required_fields:
                if field not in data:
                    return jsonify({"error": f"Missing required field: {field}"}), 400

            # Create feature array in the correct order: TeamExp, ManagerExp, Transactions, Entities, PointsNonAdjust, Adjustment, LanguageLevel
            features = np.array([[
                float(data["team_exp"]),
                float(data["manager_exp"]),
                float(data["transactions"]),
                float(data["entities"]),
                float(data["points_non_adjust"]),
                float(data["adjustment"]),
                float(data["language_level"])
            ]])

            # Make prediction using Gradient Boosting model
            effort = software_effort_gb_model.predict(features)[0]
            effort = max(0, effort)
            # Clip to training range to avoid unrealistic extrapolation
            if software_effort_range:
                effort = max(software_effort_range["min"], min(software_effort_range["max"], effort))

            # More realistic conversions:
            # - Cost: effort(hours) * hourly rate, with small multipliers for adjustment/language/experience.
            # - Time: calendar days estimated from person-days and an "effective team size" proxy derived
            #         from team/manager experience + language level (since dataset has no explicit team size).
            # NOTE: Effort is already influenced by "Adjustment" (it's a feature of the ML model),
            # so we avoid multiplying cost by adjustment again (double-counting).
            HOURLY_RATE = 250  # Rs/hour baseline (adjust to your context)

            team_exp = float(data["team_exp"])
            manager_exp = float(data["manager_exp"])
            adjustment = float(data["adjustment"])
            language_level = float(data["language_level"])

            language_factor = {1.0: 0.95, 2.0: 1.00, 3.0: 1.08}.get(language_level, 1.00)
            # Higher experience often means higher hourly cost but better throughput; keep mild effect.
            seniority_cost_factor = 0.90 + 0.03 * (team_exp - 2) + 0.02 * (manager_exp - 3)
            seniority_cost_factor = max(0.85, min(1.25, seniority_cost_factor))

            # Keep cost multipliers mild to avoid unrealistic inflation.
            seniority_cost_factor = max(0.90, min(1.15, seniority_cost_factor))
            cost_from_effort = effort * HOURLY_RATE * language_factor * seniority_cost_factor

            person_days = effort / 8.0
            effective_team_size = 1.0 + 0.35 * (team_exp - 2) + 0.20 * (manager_exp - 3) + 0.25 * (language_level - 2)
            effective_team_size = max(1.0, min(8.0, effective_team_size))
            calendar_days = person_days / effective_team_size

            # Save prediction to database
            try:
                prediction = Prediction(
                    user_id=session['user_id'],
                    project_type='software',
                    project_size=float(data.get("points_non_adjust", 0)),
                    team_size=int(data.get("team_exp", 0)),
                    experience=float(data.get("manager_exp", 0)),
                    complexity=int(data.get("entities", 0)),
                    risk_factor=float(data.get("adjustment", 0)),
                    estimated_budget=float(data.get("points_non_adjust", 0)) * 100,
                    predicted_cost=cost_from_effort,
                    predicted_time=calendar_days
                )
                db.session.add(prediction)
                db.session.commit()
            except Exception as e:
                print(f"Error saving prediction: {e}")
                db.session.rollback()

            return jsonify({
                "success": True,
                "predicted_effort": round(effort, 0),
                "predicted_cost": round(cost_from_effort, 2),
                "predicted_time": round(calendar_days, 2),
                "predicted_person_days": round(person_days, 2)
            })

        else:
            return jsonify({"error": "Invalid project type. Must be 'construction' or 'software'"}), 400

    except ValueError as e:
        return jsonify({"error": f"Invalid input: {str(e)}"}), 400
    except Exception as e:
        print(f"Prediction error: {e}")
        return jsonify({"error": "An error occurred during prediction"}), 500

@app.route("/predictions", methods=["GET"])
def get_predictions():
    """Get all predictions for the logged-in user"""
    auth_error = require_login()
    if auth_error:
        return auth_error
    
    try:
        user_id = session['user_id']
        predictions = Prediction.query.filter_by(user_id=user_id)\
            .order_by(Prediction.created_at.desc())\
            .limit(50)\
            .all()
        
        return jsonify({
            "predictions": [p.to_dict() for p in predictions],
            "count": len(predictions)
        })
    except Exception as e:
        print(f"Error fetching predictions: {e}")
        return jsonify({"error": "Failed to fetch predictions"}), 500

@app.route("/health")
def health():
    return jsonify({
        "status": "healthy",
        "models_loaded": cost_model is not None and time_model is not None,
        "database": "connected" if db else "disconnected"
    })

if __name__ == "__main__":
    app.run(debug=True, port=5000, host="0.0.0.0")
