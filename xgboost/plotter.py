import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_excel("forecast_2025_recursive_from_2023_2024.xlsx")
if 'datetime'  in df.columns:
    df['datetime'] = pd.to_datetime(df['datetime'])
else:
    df['datetime'] = pd.date_range(start="2025-01-01", periods=len(df), freq="15min")

# df = df[df['datetime'].dt.date == df['datetime'].dt.date.min()]

plt.figure(figsize=(14, 6))
plt.plot(df['datetime'], df['predicted_consumption'], label='Predicted Consumption', color='blue')

if 'real_consumption' in df.columns:
    plt.plot(df['datetime'], df['real_consumption'], label='Actual Consumption', color='orange', alpha=0.6)

plt.title("Electricity Consumption Forecast - 2025")
plt.xlabel("Time")
plt.ylabel("MW")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
