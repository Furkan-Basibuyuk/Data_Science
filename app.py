from flask import Flask, render_template_string, request
import pandas as pd
import plotly.express as px

app = Flask(__name__)

# Config: available dataset files (label: path)
DATASETS = {
    "XGBOOST": "data/2023_translated_all.xlsx",
}

value_columns = ['Forecast_Day-1', 'Forecast_Day', 'Actual Consumption','Predicted Consumption']

def load_dataset(file_path):
    df = pd.read_excel(file_path)
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True)
    df = df.dropna(subset=['Time'])
    df['Datetime'] = pd.to_datetime(df['Date'].dt.strftime('%Y-%m-%d') + ' ' + df['Time'].astype(str))
    df['Formatted_Time'] = pd.to_datetime(df['Time'].astype(str)).dt.strftime('%H:%M')
    return df

@app.route("/", methods=["GET"])
def chart():
    # Get dataset
    selected_dataset = request.args.get("dataset", list(DATASETS.keys())[0])
    file_path = DATASETS.get(selected_dataset)
    if file_path is None:
        selected_dataset = list(DATASETS.keys())[0]
        file_path = DATASETS[selected_dataset]

    df = load_dataset(file_path)

    # View mode
    view_mode = request.args.get("view_mode", "daily").lower()

    # Dates available
    available_dates = sorted(df['Date'].dt.date.unique())

    # Selected date
    date_str = request.args.get("date")
    selected_date = pd.to_datetime(date_str).date() if date_str else available_dates[0]

    # Selected columns
    selected_columns = request.args.getlist("columns")
    if not selected_columns:
        selected_columns = value_columns

    # Daily data
    df_day = df[df['Date'].dt.date == selected_date].copy()
    df_day = df_day.sort_values(by='Datetime')

    # Apply view mode
    if view_mode == "daily":
        df_plot = df_day.copy()
        x = "Formatted_Time"
        date_label = selected_date.strftime("%Y-%m-%d")
    elif view_mode == "monthly":
        df_plot = df[df['Date'].dt.month == selected_date.month].copy()
        df_plot["Day"] = df_plot["Date"].dt.day
        df_plot = df_plot.groupby("Day")[selected_columns].mean().reset_index()
        x = "Day"
        date_label = selected_date.strftime("%m-%Y")
    elif view_mode == "yearly":
        df_plot = df[df['Date'].dt.year == selected_date.year].copy()
        df_plot["Month"] = df_plot["Date"].dt.strftime("%b")
        df_plot = df_plot.groupby("Month")[selected_columns].mean().reset_index()
        x = "Month"
        date_label = selected_date.strftime("%Y")
    else:
        df_plot = df_day.copy()
        x = "Formatted_Time"
        date_label = selected_date.strftime("%Y-%m-%d")

    # Create Plotly chart
    fig = px.line(df_plot, x=x, y=selected_columns,
                  title=f"Dataset {selected_dataset} — {view_mode.capitalize()} View — {date_label}",
                  labels={'value': 'Values', x: x})
    chart_html = fig.to_html(full_html=False)

    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
    <title>Forecast Dashboard</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #4f46e5;
            --accent: #10b981;
            --bg: #f0f4f8;
            --text: #1f2937;
            --card: #ffffff;
            --border: #e5e7eb;
        }
        body {
            font-family: 'Inter', sans-serif;
            background: linear-gradient(to right, #f9fafb, #eef2f7);
            margin: 0;
            padding: 0;
            color: var(--text);
        }
        .container {
            max-width: 1100px;
            margin: auto;
            padding: 40px 20px;
            text-align: center;
        }
        h1 {
            font-size: 2.5em;
            font-weight: 600;
            margin-bottom: 30px;
            background: linear-gradient(90deg, var(--primary), var(--accent));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .card {
            background: var(--card);
            box-shadow: 0 6px 16px rgba(0, 0, 0, 0.05);
            border-radius: 16px;
            padding: 30px 35px;
            display: flex;
            grid-template-columns: 1fr 1fr 1fr 1fr; /* force equal spacing */
            column-gap: 40px;
            row-gap: 20px;
            margin-bottom: 40px;
            border: 1px solid var(--border);
        }
        label {
            font-weight: 600;
            font-size: 14px;
            margin-bottom: 6px;
            display: block;
            color: var(--text);
        }
        select, input[type="date"] {
            padding: 10px 14px;
            border: 1px solid var(--border);
            border-radius: 8px;
            font-size: 14px;
            width: 100%;
            transition: border 0.2s ease;
        }
        select:hover, input[type="date"]:hover {
            border-color: var(--primary);
        }
        .checkboxes {
            margin-top: 6px;
        }
        .checkboxes label {
            display: flex;
            align-items: center;
            font-weight: 500;
            font-size: 14px;
            color: #374151;
            padding: 4px 0;
        }
        input[type="checkbox"] {
            accent-color: var(--primary);
            margin-right: 8px;
        }
        .checkboxes label:hover {
            color: var(--primary);
        }
        .checkboxes {
            margin-top: 6px;
            display: grid;
            grid-template-columns: 1fr 1fr; /* two columns */
            gap: 10px; /* spacing between items */
        }

        .checkboxes label {
            display: flex;
            align-items: center;
        }

        .form-section-model {
            min-width: 220px;
            flex: 1;
            text-align: left;
            display: flex;
            flex-direction: column;
            justify-content: flex-start;
        }
        .form-section-date {
            min-width: 220px;
            flex: 1;
            text-align: left;
            display: flex;
            flex-direction: column;
            justify-content: flex-start;
        }
        .form-section-view {
            min-width: 220px;
            flex: 1;
            text-align: left;
            margin-left: 30px;
            display: flex;
            flex-direction: column;
            justify-content: flex-start;
        }
        .form-section-checkbox {
            min-width: 220px;
            flex: 1;
            text-align: left;
            display: flex;
            flex-direction: column;
            justify-content: flex-start;
        }
                                  
                          
    </style>
    <script>
        function autoSubmit() {
            document.getElementById("control-form").submit();
        }
    </script>
</head>
<body>
    <div class="container">
        <h1>Forecast vs Consumption</h1>

        <form id="control-form" method="get">
            <div class="card">

                <div class="form-section-date">
                    <label for="date">Choose a date</label>
                    <input type="date" id="date" name="date" value="{{ selected_date }}" onchange="autoSubmit()">
                </div>

                <div class="form-section-view">
                    <label for="view_mode">View Mode</label>
                    <select name="view_mode" id="view_mode" onchange="autoSubmit()">
                        <option value="daily" {% if view_mode == 'daily' %}selected{% endif %}>Daily</option>
                        <option value="monthly" {% if view_mode == 'monthly' %}selected{% endif %}>Monthly</option>
                        <option value="yearly" {% if view_mode == 'yearly' %}selected{% endif %}>Yearly</option>
                    </select>
                </div>

                <div class="form-section-checkbox">
                    <label>Select columns</label>
                    <div class="checkboxes">
                        {% for col in value_columns %}
                            <label>
                                <input type="checkbox" name="columns" value="{{ col }}"
                                    {% if not request.args or col in selected_columns %}checked{% endif %}
                                    onchange="autoSubmit()">
                                {{ col }}
                            </label>
                        {% endfor %}
                    </div>
                </div>

            </div>
        </form>

        <div>
            {{ chart | safe }}
        </div>
    </div>
</body>
</html>
""",
    chart=chart_html,
    datasets=DATASETS.keys(),
    selected_dataset=selected_dataset,
    selected_date=selected_date.strftime("%Y-%m-%d"),
    value_columns=value_columns,
    selected_columns=selected_columns,
    view_mode=view_mode
)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
