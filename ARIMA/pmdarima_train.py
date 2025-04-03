import pandas as pd
from pmdarima import auto_arima
import joblib

# --------------------------
# 📥 Eğitim Verisini Yükle
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

# 🔹 Verileri yükle
y_2023 = load_rte_file("conso_mix_RTE_2023.xls", 2023)
y_2024 = load_rte_file("conso_mix_RTE_2024.xls", 2024)
y_all = pd.concat([y_2023, y_2024]).sort_index()
y_train = y_all

# Bilgi yaz
print("📊 Veri boyutu:", len(y_train))
print("🕒 Başlangıç:", y_train.index.min())
print("🕒 Bitiş:", y_train.index.max())

# --------------------------
# 🎯 Model Eğitimi
# --------------------------
print("⏳ PMDARIMA modeli eğitiliyor...")
model = auto_arima(
    y_train,
    seasonal=False,
    m=96,
    stepwise=True,
    suppress_warnings=True,
    trace=True
)
print("✅ Eğitim tamamlandı.")

# --------------------------
# 💾 Modeli Kaydet
# --------------------------
joblib.dump(model, "pmdarima_model.pkl")
print("✅ Model kaydedildi: pmdarima_model.pkl")
