"""
This script trains the XGBoost with only the real consumption data. No provision data is used. Lags are introduced to 
dynamically predict the consumption and prevent cyclic repeating patterns. Unless it is used, the prediction takes account of
days and weeks while disregarding monthly or seasonal fluctuations.
"""

import pandas as pd
import xgboost as xgb
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import numpy as np


df_2023 = pd.read_excel("final_conso_RTE_2023.xlsx")
df_2024 = pd.read_excel("final_conso_RTE_2024.xlsx")

# Combine them
df_all = pd.concat([df_2023, df_2024]).sort_values("datetime")

# Save to one file
df_all.to_excel("final_conso_RTE_2023_2024_combined.xlsx", index=False)

df_train = pd.read_excel("final_conso_RTE_2023_2024_combined.xlsx")

df_train = df_train[(df_train["datetime"] >= "2023-01-01") ]
# & (df_train["datetime"] < "2023-07-01")


df_train['hour_of_day'] = df_train['datetime'].dt.hour + df_train['datetime'].dt.minute / 60
df_train['day_of_week'] = df_train['datetime'].dt.dayofweek
df_train['month'] = df_train['datetime'].dt.month


lags = [1, 4, 96, 672]  # 1 step, 1 hour, 1 day, 1 week
for lag in lags:
    df_train[f'lag_{lag}'] = df_train['real_consumption'].shift(lag)


# df_train = df_train.dropna(subset=['real_consumption'] + [f'lag_{l}' for l in lags])

# Fill missing lag values with placeholder
df_train[[f'lag_{l}' for l in lags]] = df_train[[f'lag_{l}' for l in lags]].fillna(-1)

# Optionally still drop rows where target is missing (just in case)
df_train = df_train.dropna(subset=['real_consumption'])



# Define features and target
features = ['hour_of_day', 'day_of_week', 'month'] + [f'lag_{l}' for l in lags]
X = df_train[features]
y = df_train['real_consumption']

# Optional: split for evaluation
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

# --------------------------
# ⚙️ XGBoost Configuration
# --------------------------
model = xgb.XGBRegressor(
    objective='reg:squarederror',
    n_estimators=200,
    max_depth=5,
    learning_rate=0.1,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42
)

# --------------------------
# 🏋️ Train Model
# --------------------------
print("Training model...")
model.fit(X_train, y_train)

# --------------------------
# 📉 Evaluate
# --------------------------
y_pred = model.predict(X_val)
rmse = np.sqrt(mean_squared_error(y_val, y_pred))
print(f"✅ Training complete. RMSE on validation set: {rmse:.2f}")

# --------------------------
# 💾 Save Model
# --------------------------
joblib.dump(model, "xgb_model_2023_2024.pkl")
print("✅ Model saved as xgb_model_2023_2024.pkl")


