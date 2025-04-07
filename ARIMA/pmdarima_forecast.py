import pandas as pd
import joblib
import matplotlib.pyplot as plt

import warnings
warnings.filterwarnings("ignore")

# --------------------------
# 📥 2025 Data Load
# --------------------------
def load_rte_file(filepath, year):
    df = pd.read_csv(
        filepath,
        sep="\t",
        encoding="latin1",
        names=["Heures", "PrevisionJ-1", "PrevisionJ", "Consommation", "Extra1", "Extra2"],
        skiprows=2,
        engine="python"
    )
    df = df[["Heures", "Consommation"]]
    df = df.dropna()
    df = df[df["Consommation"].astype(str).str.isnumeric()]
    df["Consommation"] = df["Consommation"].astype(float)

    n_rows_per_day = 96
    n_days = len(df) // n_rows_per_day
    dates = pd.date_range(start=f"{year}-01-01", periods=n_days, freq="D")
    full_datetimes = []

    for date in dates:
        for time_str in df["Heures"].unique():
            dt = pd.to_datetime(f"{date.date()} {time_str}")
            full_datetimes.append(dt)

    df = df.iloc[:len(full_datetimes)]
    df["Datetime"] = full_datetimes
    df.set_index("Datetime", inplace=True)

    return df["Consommation"]

# 🔹 Load data
y_2025 = load_rte_file("conso_mix_RTE_2025.xls", 2025)
y_2025 = y_2025["2025-01-01":"2025-01-02"]

# --------------------------
# 🎯 Upload Model
# --------------------------
model = joblib.load("pmdarima_model.pkl")

# --------------------------
# 🔁 Recursive Forecast
# --------------------------
preds = []
history = []

for i, value in enumerate(y_2025):
    pred = model.predict(n_periods=1).item()
    preds.append(pred)
    model.update(value)
    history.append(value)
    print(f"{i+1}/{len(y_2025)} completed")



# --------------------------
# 💾 Excel Output
# --------------------------
output_df = pd.DataFrame({
    "DateTime": list(y_2025.index)[:len(preds)],  # adjust index number to forecast
    "Real Consumption": list(y_2025.values)[:len(preds)],
    "Forecast (PMDARIMA)": preds
})


output_df["DateTime"] = output_df["DateTime"].dt.strftime("%Y-%m-%d %H:%M")
output_df.to_excel("PMDARIMA_2025_Forecast_Report.xlsx", index=False)
print("✅ Forecast Exported to Excel: PMDARIMA_2025_Forecast_Report.xlsx")

# --------------------------
# 📊 Draw the Graph
# --------------------------
plt.figure(figsize=(12, 5))
plt.plot(y_2025.index, y_2025.values, label="Real", alpha=0.8)
plt.plot(y_2025.index, preds, label="Forecast", alpha=0.8)
plt.title("2025 - Real vs Forecast (PMDARIMA)")
plt.xlabel("Time")
plt.ylabel("Consumption")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("pmdarima_forecast_graph.png")
plt.show()


