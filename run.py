from dash import Dash, html
from app.components.charts import get_consumption_chart

app = Dash(__name__)

app.layout = html.Div(children=[
    html.H1("Electricity Consumption Dashboard"),
    get_consumption_chart()
])

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=3000)
