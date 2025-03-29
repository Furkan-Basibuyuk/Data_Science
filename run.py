import dash
from dash import html

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Hello, Dash!"),
    html.P("This is a minimal Dash app.")
])

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=3000)
