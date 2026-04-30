"""
Database and Login System Diagnostic Script
Checks for errors in database structure, user logins, and authentication
"""
import os
import sys
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.security import check_password_hash, generate_password_hash

# Import app context
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app import app, db
from database import User, Prediction

def check_database():
    print("=" * 80)
    print("DATABASE AND LOGIN SYSTEM DIAGNOSTIC")
    print("=" * 80)
    
    errors_found = []
    warnings_found = []
    
    with app.app_context():
        # 1. Check database connection
        print("\n[1] Checking Database Connection...")
        try:
            db.create_all()  # Ensure tables exist
            engine = db.engine
            inspector = inspect(engine)
            print("    [OK] Database connection successful")
            print(f"    Database path: {engine.url}")
        except Exception as e:
            error_msg = f"Database connection failed: {e}"
            errors_found.append(error_msg)
            print(f"    [ERROR] {error_msg}")
            return errors_found, warnings_found
        
        # 2. Check if tables exist
        print("\n[2] Checking Database Tables...")
        try:
            tables = inspector.get_table_names()
            required_tables = ['users', 'predictions']
            
            for table in required_tables:
                if table in tables:
                    print(f"    [OK] Table '{table}' exists")
                else:
                    error_msg = f"Table '{table}' is missing"
                    errors_found.append(error_msg)
                    print(f"    [ERROR] {error_msg}")
        except Exception as e:
            error_msg = f"Failed to check tables: {e}"
            errors_found.append(error_msg)
            print(f"    [ERROR] {error_msg}")
        
        # 3. Check table structure
        print("\n[3] Checking Table Structure...")
        try:
            if 'users' in tables:
                users_columns = [col['name'] for col in inspector.get_columns('users')]
                required_user_columns = ['id', 'username', 'email', 'password_hash', 'created_at']
                
                print("    Users table columns:")
                for col in users_columns:
                    marker = "[OK]" if col in required_user_columns else "[WARN]"
                    print(f"      {marker} {col}")
                
                missing_cols = set(required_user_columns) - set(users_columns)
                if missing_cols:
                    error_msg = f"Missing columns in 'users' table: {missing_cols}"
                    errors_found.append(error_msg)
                    print(f"    [ERROR] {error_msg}")
                
                # Check column types
                print("\n    Column types:")
                for col in inspector.get_columns('users'):
                    col_name = col['name']
                    col_type = str(col['type'])
                    print(f"      {col_name}: {col_type}")
            
            if 'predictions' in tables:
                pred_columns = [col['name'] for col in inspector.get_columns('predictions')]
                print("\n    Predictions table columns:")
                for col in pred_columns:
                    print(f"      [OK] {col}")
        except Exception as e:
            error_msg = f"Failed to check table structure: {e}"
            errors_found.append(error_msg)
            print(f"    [ERROR] {error_msg}")
        
        # 4. Check existing users
        print("\n[4] Checking Existing Users...")
        try:
            users = User.query.all()
            user_count = len(users)
            print(f"    Total users in database: {user_count}")
            
            if user_count == 0:
                warnings_found.append("No users found in database")
                print("    [WARN] No users found in database")
            else:
                print("\n    User details:")
                for user in users:
                    print(f"      ID: {user.id}")
                    print(f"      Username: {user.username}")
                    print(f"      Email: {user.email}")
                    print(f"      Created: {user.created_at}")
                    
                    # Check password hash format
                    if user.password_hash:
                        if len(user.password_hash) < 20:
                            error_msg = f"User '{user.username}' has suspiciously short password hash"
                            errors_found.append(error_msg)
                            print(f"      [ERROR] Password hash seems too short")
                        else:
                            print(f"      [OK] Password hash exists (length: {len(user.password_hash)})")
                    else:
                        error_msg = f"User '{user.username}' has no password hash"
                        errors_found.append(error_msg)
                        print(f"      [ERROR] No password hash found")
                    
                    # Check for duplicate usernames/emails
                    duplicate_users = User.query.filter_by(username=user.username).all()
                    if len(duplicate_users) > 1:
                        error_msg = f"Duplicate username found: {user.username}"
                        errors_found.append(error_msg)
                        print(f"      [ERROR] Duplicate username detected")
                    
                    duplicate_emails = User.query.filter_by(email=user.email).all()
                    if len(duplicate_emails) > 1:
                        error_msg = f"Duplicate email found: {user.email}"
                        errors_found.append(error_msg)
                        print(f"      [ERROR] Duplicate email detected")
                    
                    print()
        except Exception as e:
            error_msg = f"Failed to check users: {e}"
            errors_found.append(error_msg)
            print(f"    [ERROR] {error_msg}")
        
        # 5. Test password hashing
        print("\n[5] Testing Password Hashing...")
        try:
            test_password = "test_password_123"
            test_hash = generate_password_hash(test_password)
            
            if check_password_hash(test_hash, test_password):
                print("    [OK] Password hashing and verification working correctly")
            else:
                error_msg = "Password verification failed"
                errors_found.append(error_msg)
                print(f"    [ERROR] {error_msg}")
            
            if len(test_hash) < 20:
                error_msg = "Generated password hash is too short"
                errors_found.append(error_msg)
                print(f"    [ERROR] {error_msg}")
        except Exception as e:
            error_msg = f"Password hashing test failed: {e}"
            errors_found.append(error_msg)
            print(f"    [ERROR] {error_msg}")
        
        # 6. Check predictions
        print("\n[6] Checking Predictions...")
        try:
            predictions = Prediction.query.all()
            pred_count = len(predictions)
            print(f"    Total predictions in database: {pred_count}")
            
            if pred_count > 0:
                # Check for orphaned predictions (user_id doesn't exist)
                orphaned = 0
                for pred in predictions:
                    user_exists = User.query.filter_by(id=pred.user_id).first()
                    if not user_exists:
                        orphaned += 1
                
                if orphaned > 0:
                    warning_msg = f"Found {orphaned} orphaned predictions (user_id doesn't exist)"
                    warnings_found.append(warning_msg)
                    print(f"    [WARN] {warning_msg}")
                else:
                    print("    [OK] All predictions have valid user references")
        except Exception as e:
            error_msg = f"Failed to check predictions: {e}"
            errors_found.append(error_msg)
            print(f"    [ERROR] {error_msg}")
        
        # 7. Test database constraints
        print("\n[7] Testing Database Constraints...")
        try:
            # Try to create a user with duplicate username
            test_user = User(username="test_constraint", email="test@test.com")
            test_user.set_password("test123")
            db.session.add(test_user)
            db.session.commit()
            
            # Try to create another with same username
            duplicate_user = User(username="test_constraint", email="test2@test.com")
            duplicate_user.set_password("test123")
            db.session.add(duplicate_user)
            try:
                db.session.commit()
                error_msg = "Unique constraint on username is not working"
                errors_found.append(error_msg)
                print(f"    [ERROR] {error_msg}")
                # Clean up
                db.session.delete(duplicate_user)
                db.session.commit()
            except Exception:
                print("    [OK] Unique constraint on username working correctly")
                db.session.rollback()
            
            # Clean up test user
            db.session.delete(test_user)
            db.session.commit()
            
        except Exception as e:
            error_msg = f"Constraint test failed: {e}"
            errors_found.append(error_msg)
            print(f"    [ERROR] {error_msg}")
            db.session.rollback()
        
        # 8. Check database file permissions
        print("\n[8] Checking Database File...")
        try:
            db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
            if os.path.exists(db_path):
                file_size = os.path.getsize(db_path)
                print(f"    [OK] Database file exists: {db_path}")
                print(f"    File size: {file_size} bytes")
                
                # Check if file is readable/writable
                if os.access(db_path, os.R_OK):
                    print("    [OK] Database file is readable")
                else:
                    error_msg = "Database file is not readable"
                    errors_found.append(error_msg)
                    print(f"    [ERROR] {error_msg}")
                
                if os.access(db_path, os.W_OK):
                    print("    [OK] Database file is writable")
                else:
                    error_msg = "Database file is not writable"
                    errors_found.append(error_msg)
                    print(f"    [ERROR] {error_msg}")
            else:
                warnings_found.append("Database file doesn't exist yet (will be created on first use)")
                print("    [WARN] Database file doesn't exist yet")
        except Exception as e:
            error_msg = f"Failed to check database file: {e}"
            errors_found.append(error_msg)
            print(f"    [ERROR] {error_msg}")
    
    # Summary
    print("\n" + "=" * 80)
    print("DIAGNOSTIC SUMMARY")
    print("=" * 80)
    
    if len(errors_found) == 0 and len(warnings_found) == 0:
        print("\n[SUCCESS] No errors or warnings found! Database and login system are working correctly.")
    else:
        if errors_found:
            print(f"\n[ERRORS FOUND: {len(errors_found)}]")
            for i, error in enumerate(errors_found, 1):
                print(f"  {i}. {error}")
        
        if warnings_found:
            print(f"\n[WARNINGS: {len(warnings_found)}]")
            for i, warning in enumerate(warnings_found, 1):
                print(f"  {i}. {warning}")
    
    print("\n" + "=" * 80)
    
    return errors_found, warnings_found

if __name__ == "__main__":
    errors, warnings = check_database()
    sys.exit(1 if errors else 0)
