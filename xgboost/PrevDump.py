"""
This script is used for dumping unused code snippets that are not in the main files. These previous versions are kept
for referencing.

"""

"""
Trainer.py Prev Versions

"""
# This Section is for training the model using Provision J-1 and J-2 data that gives accurate results

# import pandas as pd
# import xgboost as xgb
# import joblib


# df_train = pd.read_excel("final_conso_RTE_2023.xlsx")
# # df_train = df_train[df_train["datetime"].dt.month == 1]
# df_train = df_train[(df_train["datetime"] >= "2023-01-01") & (df_train["datetime"] < "2023-07-01")]

# features = ['provision_j_1', 'provision_j', 'hour_of_day', 'day_of_week']
# X_train = df_train[features]
# y_train = df_train['real_consumption']

# model = xgb.XGBRegressor(objective='reg:squarederror', n_estimators=100)
# model.fit(X_train, y_train)

# joblib.dump(model, "xgb_model_2023.pkl")
# print("Model saved as xgb_model_2023.pkl")
# print(f"Training on {len(df_train)} records from January 2023")

# This is an updated version with inclusion of Provision data

# import pandas as pd
# import xgboost as xgb
# import joblib
# from sklearn.model_selection import train_test_split
# from sklearn.metrics import mean_squared_error
# import numpy as np


# df_train = pd.read_excel("final_conso_RTE_2023.xlsx")


# df_train = df_train[(df_train["datetime"] >= "2023-01-01") & (df_train["datetime"] < "2023-04-01")]

# print(f"Loaded {len(df_train)} records from Jan–Jun 2023")


# features = ['provision_j_1', 'provision_j', 'hour_of_day', 'day_of_week']
# target = 'real_consumption'

# X = df_train[features]
# y = df_train[target]

# # Optional: train/val split to evaluate performance
# X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)


# model = xgb.XGBRegressor(
#     objective='reg:squarederror',
#     n_estimators=200,
#     max_depth=5,
#     learning_rate=0.1,
#     subsample=0.8,
#     colsample_bytree=0.8,
#     random_state=42
# )


# print("Training model...")
# model.fit(X_train, y_train)


# y_pred = model.predict(X_val)
# rmse = np.sqrt(mean_squared_error(y_val, y_pred))
# print(f"Training complete. RMSE on validation set: {rmse:.2f}")


# joblib.dump(model, "xgb_model_2023.pkl")
# print("Model saved as xgb_model_2023.pkl")

"""
predicter.py Prev Versions

"""
# Predicter with inclusion if Provision data

# import pandas as pd
# import joblib


# model = joblib.load("xgb_model_2023.pkl")
# df_2025 = pd.read_excel("final_conso_RTE_2025.xlsx")
# features = ['provision_j_1', 'provision_j', 'hour_of_day', 'day_of_week']
# X_2025 = df_2025[features]

# df_2025['predicted_consumption'] = model.predict(X_2025)

# df_2025.to_excel("forecast_2025_from_2023_model.xlsx", index=False)
# print("Forecast saved to forecast_2025_from_2023_model.xlsx")

"""
In this one, no recursive feedback, thus annealing cannot be done and after cutoff prediction is inaccurate

The following code is for the 2024 prediction that only considers the real consumption in 2023. It is not using provision J-1
and J data. We are using the trained model from the Trainer.py script. Lag functions are also deployed here with NaN values filled with
-1 instead of dropping them. This filling causes an outlier in the first day data. The other predictions are following the
desired pattern

"""

# import pandas as pd
# import joblib


# model = joblib.load("xgb_model_2023_2024.pkl")


# df_2025 = pd.read_excel("final_conso_RTE_2025_extended.xlsx")


# df_2025['hour_of_day'] = df_2025['datetime'].dt.hour + df_2025['datetime'].dt.minute / 60
# df_2025['day_of_week'] = df_2025['datetime'].dt.dayofweek
# df_2025['month'] = df_2025['datetime'].dt.month


# df_2025['lag_1'] = df_2025['real_consumption'].shift(1)
# df_2025['lag_4'] = df_2025['real_consumption'].shift(4)
# df_2025['lag_96'] = df_2025['real_consumption'].shift(96)
# df_2025['lag_672'] = df_2025['real_consumption'].shift(672)


# # df_2025 = df_2025.dropna(subset=['lag_1', 'lag_4', 'lag_96', 'lag_672'])


# df_2025[['lag_1', 'lag_4', 'lag_96', 'lag_672']] = df_2025[['lag_1', 'lag_4', 'lag_96', 'lag_672']].fillna(-1)



# features = ['hour_of_day', 'day_of_week', 'month', 'lag_1', 'lag_4', 'lag_96', 'lag_672']
# # 
# X_2025 = df_2025[features]


# df_2025['predicted_consumption'] = model.predict(X_2025)

# df_2025.to_excel("forecast_2025_with_2023_2024.xlsx", index=False)
# print("Forecast with lag features saved to forecast_2025_with_2023_2024.xlsx")

