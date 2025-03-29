import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX
import pickle

# --------------------------
# 📤 2025 Data Forecast
# --------------------------
def load_2025_forecast_input(filepath):
    df = pd.read_csv(
        filepath,
        sep="\t",
        skiprows=2,
        encoding="latin1",
        engine="python",
        names=["Heures", "PrevisionJ-1", "PrevisionJ", "Consommation", "Extra1", "Extra2"]
    )
    df = df[df["PrevisionJ-1"].astype(str).str.isnumeric()]
    df = df[df["PrevisionJ"].astype(str).str.isnumeric()]
    df = df[df["Consommation"].astype(str).str.isnumeric()]
    df["PrevisionJ-1"] = df["PrevisionJ-1"].astype(float)
    df["PrevisionJ"] = df["PrevisionJ"].astype(float)
    df["Consommation"] = df["Consommation"].astype(float)
    df = df.head(96).reset_index(drop=True)
    return df

# get 2025 data
df_2025 = load_2025_forecast_input("conso_mix_RTE_2025.xls")
exog_2025 = df_2025[["PrevisionJ-1", "PrevisionJ"]]
real_consumption = df_2025["Consommation"]

# load model
with open("sarimax_model.pkl", "rb") as f:
    model_fit = pickle.load(f)

# forecast
forecast = model_fit.forecast(steps=96, exog=exog_2025)

# --------------------------
# 🧾 Forecast and Reality Comparison
# --------------------------
result = pd.DataFrame({
    "Forecast (SARIMAX)": forecast.values,
    "Real Consumption": real_consumption.values
})

print(result.head(10))  # Print first 10 lines
