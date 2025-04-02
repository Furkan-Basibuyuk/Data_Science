"""
The following code is for the 2025 prediction that only considers the real consumption in 2023 and 2024.
It does not use provision J-1 or J data. Lag functions are used. For missing future lags, predictions are generated
recursively by feeding previous predictions back into lag slots. Optional annealing logic is included but commented.
"""

import pandas as pd
import joblib

# Load trained model
model = joblib.load("xgb_model_2023_2024.pkl")

# Load extended 2025 dataset
df = pd.read_excel("final_conso_RTE_2025_extended.xlsx")

# Create month column (only for feature input, not saved)
df['month'] = df['datetime'].dt.month

# Initialize predicted_consumption column
# Copy real_consumption where available
if 'real_consumption' in df.columns:
    df['predicted_consumption'] = df['real_consumption']
else:
    df['predicted_consumption'] = pd.NA

# Determine last index where real consumption is known
cutoff_idx = df['predicted_consumption'].last_valid_index()

# Recursive forecasting from the next row to the end
for i in range(cutoff_idx + 1, len(df)):
    row = df.loc[i]

    def get_lag(idx):
        if idx < 0:
            return -1
        if idx <= cutoff_idx:
            return df.loc[idx, 'real_consumption']
        return df.loc[idx, 'predicted_consumption']

    lag_1   = get_lag(i - 1)
    lag_4   = get_lag(i - 4)
    lag_96  = get_lag(i - 96)
    lag_672 = get_lag(i - 672)

    input_features = [[
        row['hour_of_day'],
        row['day_of_week'],
        row['month'],
        lag_1 if pd.notna(lag_1) else -1,
        lag_4 if pd.notna(lag_4) else -1,
        lag_96 if pd.notna(lag_96) else -1,
        lag_672 if pd.notna(lag_672) else -1
    ]]

    prediction = model.predict(input_features)[0]

    # Optional: annealing (smooth prediction drift)
    prediction = 0.9 * prediction + 0.1 * df.loc[i - 96, 'predicted_consumption']

    df.at[i, 'predicted_consumption'] = prediction

# Save results
output_path = "forecast_2025_recursive_from_2023_2024.xlsx"
df.to_excel(output_path, index=False)
print(f"📈 Recursive forecast saved to {output_path}")
