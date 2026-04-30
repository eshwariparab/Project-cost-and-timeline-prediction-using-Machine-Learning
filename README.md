# Project Cost and Timeline Prediction using Machine Learning

This project is a full-stack web application that leverages Machine Learning to predict the cost, time, and effort required for both **Software** and **Construction** projects. It features a Flask backend, a user-friendly frontend, and trained machine learning models (Gradient Boosting, Random Forest) to provide accurate estimates based on project parameters.

## Features

- **User Authentication:** Secure registration and login system.
- **Construction Project Prediction:** Estimates total cost and time based on project size, team size, experience, material quality, and complexity.
- **Software Project Prediction:** Estimates effort (hours), cost, time (calendar days), and person-days based on team experience, manager experience, entities, language level, and other parameters.
- **Dashboard & History:** View past predictions and their details in a personalized dashboard.
- **Machine Learning Powered:** Utilizes Scikit-Learn models trained on historical project datasets.

## Technology Stack

- **Backend:** Python, Flask, Flask-SQLAlchemy (SQLite), Joblib
- **Machine Learning:** Scikit-Learn, Pandas, NumPy
- **Frontend:** HTML, CSS, JavaScript

## Project Structure

```text
├── backend/
│   ├── app.py                      # Main Flask application
│   ├── database.py                 # SQLAlchemy database models
│   ├── predictions.db              # SQLite database (stores user and prediction data)
│   ├── train_model.py              # Script to train construction ML models
│   ├── train_software_model.py     # Script to train software ML models
│   ├── *.pkl                       # Saved trained ML models
│   └── *.csv                       # Datasets used for training
├── frontend/
│   ├── static/                     # CSS, JS, and image assets
│   └── templates/                  # HTML templates (login, register, dashboard, etc.)
└── README.md
```

## Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/eshwariparab/Project-cost-and-timeline-prediction-using-Machine-Learning.git
   cd Project-cost-and-timeline-prediction-using-Machine-Learning
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv .venv
   
   # On Windows:
   .venv\Scripts\activate
   
   # On Mac/Linux:
   source .venv/bin/activate
   ```

3. **Install Dependencies:**
   Ensure you have the required Python libraries installed:
   ```bash
   pip install Flask Flask-SQLAlchemy Flask-Cors scikit-learn pandas numpy joblib
   ```

4. **Train the Models (if not already trained):**
   Navigate to the `backend` directory and run the training scripts to generate the `.pkl` model files:
   ```bash
   cd backend
   python train_model.py
   python train_software_model.py
   ```

5. **Run the Application:**
   Start the Flask server from the `backend` directory:
   ```bash
   python app.py
   ```
   The application will be accessible at `http://localhost:5000`.

## Usage

1. Open your browser and go to `http://localhost:5000`.
2. Register a new account or log in with an existing one.
3. Choose the project type (Software or Construction) you wish to evaluate.
4. Input the required parameters (e.g., team size, experience, project size).
5. Click "Predict" to see the estimated cost, time, and effort.
6. Check your Dashboard to review your past predictions.
