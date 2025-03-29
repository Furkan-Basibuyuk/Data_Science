import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX
import pickle
import contextlib
import sys


# --------------------------
# 📥 Training Data Load
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
    df = df[["Heures", "PrevisionJ-1", "PrevisionJ", "Consommation"]]
    df = df.dropna()
    df = df[df["Consommation"].astype(str).str.isnumeric()]
    df["PrevisionJ-1"] = df["PrevisionJ-1"].astype(float)
    df["PrevisionJ"] = df["PrevisionJ"].astype(float)
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

    return df[["PrevisionJ-1", "PrevisionJ", "Consommation"]]

# Load training files
df_2023 = load_rte_file("conso_mix_RTE_2023.xls", 2023)
df_2024 = load_rte_file("conso_mix_RTE_2024.xls", 2024)
df_all = pd.concat([df_2023, df_2024]).sort_index()
df_all = df_all["2023-01-01":"2023-01-31"]

# --------------------------
# 🎯 Model Training
# --------------------------
y = df_all["Consommation"]
X = df_all[["PrevisionJ-1", "PrevisionJ"]]

# >>>>> Before Training - Data Check
print("🎯 Y (target - consommation):")
print(y)

print("\n🧾 X (outer veriables - PrevisionJ-1, PrevisionJ):")
print(X)

print("📊 Data size:", y.shape[0])
print("🕒 Start:", y.index.min())
print("🕒 End:", y.index.max())


model = SARIMAX(
    endog=y,
    exog=X,
    order=(1, 1, 1),
    seasonal_order=(1, 1, 1, 96),
    enforce_stationarity=False,
    enforce_invertibility=False
)
print("✅ Training is started.")

with contextlib.redirect_stdout(sys.stdout):
    model_fit = model.fit(disp=True)

try:   
    with open("sarimax_model.pkl", "wb") as f:
        pickle.dump(model_fit, f)
except Exception as e:
    print("My Pickle file exception: ", e)
    
# Eğitim tamamlandı
print("✅ SARIMAX has been successfully trained.")

