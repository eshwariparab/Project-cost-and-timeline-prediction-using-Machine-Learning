from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    """User model for authentication"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to predictions
    predictions = db.relationship('Prediction', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert user to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat()
        }

class Prediction(db.Model):
    """Prediction model to store user predictions"""
    __tablename__ = 'predictions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # Project type and details
    project_type = db.Column(db.String(50), nullable=False)  # software, construction, etc.
    project_size = db.Column(db.Float, nullable=False)
    team_size = db.Column(db.Integer, nullable=False)
    experience = db.Column(db.Float, nullable=False)
    complexity = db.Column(db.Integer, nullable=False)
    risk_factor = db.Column(db.Float, nullable=False)
    estimated_budget = db.Column(db.Float, nullable=False)
    
    # Predictions
    predicted_cost = db.Column(db.Float, nullable=False)
    predicted_time = db.Column(db.Float, nullable=False)
    
    # Timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def to_dict(self):
        """Convert prediction to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'project_type': self.project_type,
            'project_size': self.project_size,
            'team_size': self.team_size,
            'experience': self.experience,
            'complexity': self.complexity,
            'risk_factor': self.risk_factor,
            'estimated_budget': self.estimated_budget,
            'predicted_cost': self.predicted_cost,
            'predicted_time': self.predicted_time,
            'created_at': self.created_at.isoformat()
        }
