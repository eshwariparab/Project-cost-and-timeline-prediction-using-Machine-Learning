import pandas as pd
import joblib
import numpy as np
import os
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# Dataset: construction_dataset.csv is for civil/construction cost & time estimation
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

print("Loading construction dataset (construction_dataset.csv)...")

# Load construction dataset
data = pd.read_csv(os.path.join(BASE_DIR, "construction_dataset.csv"))
print("Dataset shape:", data.shape)
print(f"Columns: {list(data.columns)}")

# Features for prediction (must match CSV exactly)
X = data[[
    "Project_Size_sqft",
    "Num_Workers",
    "Material_Quality",
    "Project_Complexity",
    "Equipment_Count",
    "Team_Experience_Years"
]]

# Targets from dataset
y_cost = data["Total_Cost"]
y_time = data["Estimated_Time_Days"]

print(f"\nCost range: Rs{y_cost.min():.2f} - Rs{y_cost.max():.2f}")
print(f"Time range: {y_time.min():.2f} - {y_time.max():.2f} days")

# Split data for evaluation
X_train, X_test, y_cost_train, y_cost_test, y_time_train, y_time_test = train_test_split(
    X, y_cost, y_time, test_size=0.2, random_state=42
)

print("\nTraining Cost Prediction Model...")
cost_model = RandomForestRegressor(
    n_estimators=200,
    max_depth=20,
    min_samples_split=4,
    min_samples_leaf=2,
    random_state=42,
    n_jobs=-1
)
cost_model.fit(X_train, y_cost_train)

# Evaluate cost model
cost_pred = cost_model.predict(X_test)
cost_mae = mean_absolute_error(y_cost_test, cost_pred)
cost_rmse = np.sqrt(mean_squared_error(y_cost_test, cost_pred))
cost_r2 = r2_score(y_cost_test, cost_pred)

print(f"Cost Model - MAE: Rs{cost_mae:.2f}, RMSE: Rs{cost_rmse:.2f}, R2: {cost_r2:.4f}")

print("\nTraining Time Prediction Model...")
time_model = RandomForestRegressor(
    n_estimators=200,
    max_depth=20,
    min_samples_split=4,
    min_samples_leaf=2,
    random_state=42,
    n_jobs=-1
)
time_model.fit(X_train, y_time_train)

# Evaluate time model
time_pred = time_model.predict(X_test)
time_mae = mean_absolute_error(y_time_test, time_pred)
time_rmse = np.sqrt(mean_squared_error(y_time_test, time_pred))
time_r2 = r2_score(y_time_test, time_pred)

print(f"Time Model - MAE: {time_mae:.2f} days, RMSE: {time_rmse:.2f} days, R2: {time_r2:.4f}")

# Save models
joblib.dump(cost_model, os.path.join(BASE_DIR, "cost_model.pkl"))
joblib.dump(time_model, os.path.join(BASE_DIR, "time_model.pkl"))

print("\nModels saved successfully!")
print("   - cost_model.pkl")
print("   - time_model.pkl")
print("   - policy_reason_encoder.pkl")

print(f"\nFeature importance (Cost Model):")
feature_names = ["Material_Cost", "Labor_Cost", "Profit_Rate", "Discount_or_Markup", "Policy_Reason"]
for name, importance in sorted(zip(feature_names, cost_model.feature_importances_), 
                                key=lambda x: x[1], reverse=True):
    print(f"   {name}: {importance:.4f}")
