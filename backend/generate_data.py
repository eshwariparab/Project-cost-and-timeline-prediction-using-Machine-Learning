import pandas as pd
import numpy as np

# Generate more realistic training data for software/construction projects
np.random.seed(42)

num_samples = 300  # Increased for better accuracy

# Project types: 0 = Software, 1 = Construction, 2 = Hybrid
project_types = ['software', 'construction', 'hybrid']
data = {
    'project_type': np.random.choice([0, 1, 2], num_samples),  # 0=software, 1=construction, 2=hybrid
    'project_size': np.random.uniform(50, 300, num_samples),
    'team_size': np.random.randint(2, 12, num_samples),
    'experience': np.random.uniform(1, 10, num_samples),
    'complexity': np.random.choice([1, 2, 3], num_samples),
    'risk_factor': np.random.uniform(0.1, 0.8, num_samples),
    'estimated_budget': np.random.uniform(50000, 250000, num_samples)
}

df = pd.DataFrame(data)

# Generate realistic actual_cost based on features and project type
# Software projects typically cost less per unit size
# Construction projects have higher material costs
def calculate_cost(row):
    base_cost = row['estimated_budget']
    type_multiplier = {
        0: 0.9,  # Software - typically more predictable
        1: 1.3,  # Construction - higher material/permits costs
        2: 1.1   # Hybrid - moderate
    }
    
    multiplier = type_multiplier[row['project_type']]
    cost = base_cost * multiplier * (
        1 + 
        row['risk_factor'] * 0.5 + 
        row['complexity'] * 0.15 + 
        (1 - row['experience'] / 10) * 0.3 +
        (row['project_size'] / 200) * 0.2
    )
    return cost + np.random.normal(0, base_cost * 0.1)

# Generate realistic actual_duration based on features and project type
# Software projects might have faster iteration cycles
# Construction projects have more sequential dependencies
def calculate_duration(row):
    base_duration = (row['project_size'] / row['team_size']) * (row['complexity'] / max(row['experience'], 1))
    
    type_multiplier = {
        0: 0.8,  # Software - agile methodologies
        1: 1.4,  # Construction - weather, permits delays
        2: 1.1   # Hybrid
    }
    
    multiplier = type_multiplier[row['project_type']]
    duration = base_duration * multiplier * (1 + row['risk_factor'] * 0.5) * (1 + row['estimated_budget'] / 200000 * 0.5)
    return duration + np.random.normal(0, 10)

df['actual_cost'] = df.apply(calculate_cost, axis=1)
df['actual_duration'] = df.apply(calculate_duration, axis=1)

# Ensure positive values
df['actual_cost'] = np.maximum(df['actual_cost'], df['estimated_budget'] * 0.9)
df['actual_duration'] = np.maximum(df['actual_duration'], 30)

# Round to reasonable precision
df['actual_cost'] = df['actual_cost'].round(0)
df['actual_duration'] = df['actual_duration'].round(0)

# Convert project_type back to string for readability (keep numeric for ML)
df['project_type_name'] = df['project_type'].map({0: 'software', 1: 'construction', 2: 'hybrid'})

# Reorder columns
df = df[['project_type', 'project_size', 'team_size', 'experience', 'complexity', 
         'risk_factor', 'estimated_budget', 'actual_cost', 'actual_duration']]

df.to_csv('project_data.csv', index=False)
print(f"Generated {num_samples} samples and saved to project_data.csv")
print(f"Data shape: {df.shape}")
print(f"\nSample data:")
print(df.head(10))
print(f"\nProject type distribution:")
print(f"Software (0): {(df['project_type'] == 0).sum()}")
print(f"Construction (1): {(df['project_type'] == 1).sum()}")
print(f"Hybrid (2): {(df['project_type'] == 2).sum()}")
