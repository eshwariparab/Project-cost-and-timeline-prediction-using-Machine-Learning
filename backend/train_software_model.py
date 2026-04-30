import pandas as pd
import joblib
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

print("Loading Desharnais software dataset...")

# Load Desharnais dataset
data = pd.read_csv("02.desharnais.csv")
print("Dataset shape:", data.shape)
print(f"Columns: {list(data.columns)}")

# Features for software project prediction
# Using: TeamExp, ManagerExp, Transactions, Entities, PointsNonAdjust, Adjustment, PointsAjust, Language
X = data[[
    "TeamExp",
    "ManagerExp",
    "Transactions",
    "Entities",
    "PointsNonAdjust",
    "Adjustment",
    "PointsAjust",
    "Language"
]]

# Target: Effort (person-hours) for cost estimation
# Cost in rupees: Assuming 1 person-hour = Rs 1000 average
y_cost = data["Effort"] * 1000  # Convert effort to cost in rupees

# Target: Length (months) for time estimation  
y_time = data["Length"]  # Already in months

print(f"\nCost range: Rs{y_cost.min():.2f} - Rs{y_cost.max():.2f}")
print(f"Time range: {y_time.min():.2f} - {y_time.max():.2f} months")

# Split data for evaluation
X_train, X_test, y_cost_train, y_cost_test, y_time_train, y_time_test = train_test_split(
    X, y_cost, y_time, test_size=0.2, random_state=42
)

print("\nTraining Software Cost Prediction Model...")
cost_model = RandomForestRegressor(
    n_estimators=200,
    max_depth=15,
    min_samples_split=3,
    min_samples_leaf=1,
    random_state=42,
    n_jobs=-1
)
cost_model.fit(X_train, y_cost_train)

# Evaluate cost model
cost_pred = cost_model.predict(X_test)
cost_mae = mean_absolute_error(y_cost_test, cost_pred)
cost_rmse = np.sqrt(mean_squared_error(y_cost_test, cost_pred))
cost_r2 = r2_score(y_cost_test, cost_pred)

print(f"Software Cost Model - MAE: Rs{cost_mae:.2f}, RMSE: Rs{cost_rmse:.2f}, R2: {cost_r2:.4f}")

print("\nTraining Software Time Prediction Model...")
time_model = RandomForestRegressor(
    n_estimators=200,
    max_depth=15,
    min_samples_split=3,
    min_samples_leaf=1,
    random_state=42,
    n_jobs=-1
)
time_model.fit(X_train, y_time_train)

# Evaluate time model
time_pred = time_model.predict(X_test)
time_mae = mean_absolute_error(y_time_test, time_pred)
time_rmse = np.sqrt(mean_squared_error(y_time_test, time_pred))
time_r2 = r2_score(y_time_test, time_pred)

print(f"Software Time Model - MAE: {time_mae:.2f} months, RMSE: {time_rmse:.2f} months, R2: {time_r2:.4f}")

# Save models
joblib.dump(cost_model, "software_cost_model.pkl")
joblib.dump(time_model, "software_time_model.pkl")

print("\nSoftware models saved successfully!")
print("   - software_cost_model.pkl")
print("   - software_time_model.pkl")

print(f"\nFeature importance (Software Cost Model):")
feature_names = ["TeamExp", "ManagerExp", "Transactions", "Entities", 
                 "PointsNonAdjust", "Adjustment", "PointsAjust", "Language"]
for name, importance in sorted(zip(feature_names, cost_model.feature_importances_), 
                                key=lambda x: x[1], reverse=True):
    print(f"   {name}: {importance:.4f}")
