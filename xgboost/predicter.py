"""
The following code is for the 2025 prediction that only considers the real consumption in 2023 and 2024.
It does not use provision J-1 or J data. Lag functions are used. For missing future lags, predictions are generated
recursively by feeding previous predictions back into lag slots. Optional annealing logic is included but commented.
"""

import pandas as pd
import joblib


model = joblib.load("xgb_model_2023_2024.pkl")


df = pd.read_excel("final_conso_RTE_2025.xlsx")


df['month'] = df['datetime'].dt.month


# Copy real_consumption where available
if 'real_consumption' in df.columns:
    # df['predicted_consumption'] = df['real_consumption']
    df['predicted_consumption'] = pd.NA
else:
    df['predicted_consumption'] = pd.NA

# Determine last index where real consumption is known
# cutoff_idx = df['predicted_consumption'].last_valid_index()
cutoff_idx = df['real_consumption'].last_valid_index()


for i in range( len(df)):
# cutoff_idx + 1,
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

    
    # prediction = 0.9 * prediction + 0.1 * df.loc[i - 96, 'predicted_consumption']
    try:
        prediction = 0.9 * prediction + 0.1 * df.loc[i - 96, 'predicted_consumption']
    except KeyError:
        pass

    df.at[i, 'predicted_consumption'] = prediction


output_path = "forecast_2025_recursive_from_2023_2024.xlsx"
df.to_excel(output_path, index=False)
print(f"📈 Recursive forecast saved to {output_path}")

