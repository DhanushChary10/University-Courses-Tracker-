from dash import Dash, dcc, html, dash_table
from dash.dependencies import Input, Output, State
import plotly.express as px
import pandas as pd
import requests

API_URL = "http://127.0.0.1:8000/courses/"

COLOR_MAP = {
    1: "#636EFA",
    2: "#00CC96",
    3: "#AB63FA",
    4: "#FFA15A",
    5: "#EF553B",
}

# ---------- API HELPERS ----------
def get_data():
    r = requests.get(API_URL)
    if r.status_code == 200:
        return pd.DataFrame(r.json())
    return pd.DataFrame()

def add_course(course_code, course_name, instructor, credits):
    requests.post(API_URL, json={
        "course_code": course_code,
        "course_name": course_name,
        "instructor": instructor,
        "credits": credits
    })

def update_instructor(course_id, instructor):
    requests.put(f"{API_URL}{course_id}", json={"instructor": instructor})

def delete_course(course_id):
    requests.delete(f"{API_URL}{course_id}")

# ---------- DASH APP ----------
app = Dash(__name__)

app.layout = html.Div(
    style={
        "backgroundColor": "#ECEFF1",
        "padding": "20px",
        "height": "100vh",
        "overflowY": "auto",
    },
    children=[

        html.H1(
            "University Courses Dashboard",
            style={"textAlign": "center", "fontWeight": "bold"},
        ),

        # -------- KPI CARDS --------
        html.Div(
            style={"display": "flex", "gap": "20px", "marginBottom": "20px"},
            children=[

                html.Div(
                    style={
                        "backgroundColor": "#4CAF50",
                        "color": "white",
                        "padding": "20px",
                        "borderRadius": "12px",
                        "width": "33%",
                        "textAlign": "center",
                    },
                    children=[
                        html.H4("Total Courses"),
                        html.H2(id="kpi_courses"),
                    ],
                ),

                html.Div(
                    style={
                        "backgroundColor": "#2196F3",
                        "color": "white",
                        "padding": "20px",
                        "borderRadius": "12px",
                        "width": "33%",
                        "textAlign": "center",
                    },
                    children=[
                        html.H4("Total Instructors"),
                        html.H2(id="kpi_instructors"),
                    ],
                ),

                html.Div(
                    style={
                        "backgroundColor": "#FF9800",
                        "color": "white",
                        "padding": "20px",
                        "borderRadius": "12px",
                        "width": "33%",
                        "textAlign": "center",
                    },
                    children=[
                        html.H4("Average Credits"),
                        html.H2(id="kpi_avg"),
                    ],
                ),
            ],
        ),

        dcc.Interval(id="interval", interval=5000, n_intervals=0),

        # -------- ADD COURSE --------
        html.Div(
            style={
                "backgroundColor": "white",
                "padding": "15px",
                "borderRadius": "10px",
                "marginBottom": "15px",
            },
            children=[
                html.H3("Add New Course"),
                dcc.Input(id="code", placeholder="Course Code"),
                dcc.Input(id="name", placeholder="Course Name"),
                dcc.Input(id="inst", placeholder="Instructor"),
                dcc.Input(id="credits", placeholder="Credits", type="number"),
                html.Br(),
                html.Button("Add Course", id="add_btn"),
                html.Div(id="add_msg", style={"color": "green"}),
            ],
        ),

        # -------- CHARTS --------
        html.Div(
            style={"display": "flex", "gap": "15px"},
            children=[
                dcc.Graph(id="bar_chart", style={"width": "50%", "height": "350px"}),
                dcc.Graph(id="pie_chart", style={"width": "50%", "height": "350px"}),
            ],
        ),

        # -------- EXTRA GRAPH --------
        html.Div(
            style={
                "backgroundColor": "white",
                "padding": "20px",
                "borderRadius": "12px",
                "marginTop": "20px",
            },
            children=[
                html.H3("Courses per Instructor"),
                dcc.Graph(id="instructor_bar"),
            ],
        ),

        html.Br(),

        # -------- TABLES --------
        html.Div(
            style={"display": "flex", "gap": "20px"},
            children=[

                html.Div(
                    style={"width": "60%", "backgroundColor": "white", "padding": "15px", "borderRadius": "10px"},
                    children=[
                        html.H3("Course Details"),
                        dash_table.DataTable(
                            id="course_table",
                            editable=True,
                            row_deletable=True,
                            page_size=8,
                            style_table={"height": "300px", "overflowY": "auto"},
                            style_header={"fontWeight": "bold"},
                            style_cell={"padding": "8px"},
                        ),
                    ],
                ),

                html.Div(
                    style={"width": "40%", "backgroundColor": "white", "padding": "15px", "borderRadius": "10px"},
                    children=[
                        html.H3("Instructor Summary"),
                        dash_table.DataTable(
                            id="instructor_table",
                            page_size=8,
                            style_table={"height": "300px", "overflowY": "auto"},
                            style_header={"fontWeight": "bold"},
                            style_cell={"padding": "8px"},
                        ),
                    ],
                ),
            ],
        ),
    ],
)

# ---------- UPDATE DASHBOARD ----------
@app.callback(
    [
        Output("bar_chart", "figure"),
        Output("pie_chart", "figure"),
        Output("course_table", "data"),
        Output("course_table", "columns"),
        Output("instructor_table", "data"),
        Output("instructor_table", "columns"),
        Output("kpi_courses", "children"),
        Output("kpi_instructors", "children"),
        Output("kpi_avg", "children"),
        Output("instructor_bar", "figure"),
    ],
    Input("interval", "n_intervals"),
)
def update_dashboard(n):
    df = get_data()

    if df.empty:
        return {}, {}, [], [], [], [], 0, 0, 0, {}

    bar = px.bar(
        df, x="course_name", y="credits",
        color="credits", color_discrete_map=COLOR_MAP
    )

    pie = px.pie(
        df, names="credits",
        color="credits", color_discrete_map=COLOR_MAP
    )

    course_columns = [
        {"name": c, "id": c, "editable": c == "instructor"}
        for c in df.columns
    ]

    summary = df.groupby("instructor").size().reset_index(name="No of Courses")
    summary.insert(0, "S.No", range(1, len(summary) + 1))

    instructor_columns = [
        {"name": "S.No", "id": "S.No"},
        {"name": "Instructor Name", "id": "instructor"},
        {"name": "No of Courses", "id": "No of Courses"},
    ]

    total_courses = len(df)
    total_instructors = df["instructor"].nunique()
    avg_credits = round(df["credits"].mean(), 2)

    inst_bar = px.bar(
        summary,
        x="instructor",
        y="No of Courses",
        color="No of Courses",
        color_continuous_scale="Viridis",
    )

    return (
        bar,
        pie,
        df.to_dict("records"),
        course_columns,
        summary.to_dict("records"),
        instructor_columns,
        total_courses,
        total_instructors,
        avg_credits,
        inst_bar,
    )

# ---------- HANDLE EDIT & DELETE ----------
@app.callback(
    Output("interval", "n_intervals"),
    Input("course_table", "data_timestamp"),
    State("course_table", "data"),
    State("course_table", "data_previous"),
)
def handle_table_changes(ts, rows, prev_rows):
    if ts is None or prev_rows is None:
        return 0

    current_ids = {r["id"] for r in rows}
    prev_ids = {r["id"] for r in prev_rows}

    deleted = prev_ids - current_ids
    for cid in deleted:
        delete_course(cid)

    for r in rows:
        update_instructor(r["id"], r["instructor"])

    return 0

# ---------- ADD COURSE ----------
@app.callback(
    Output("add_msg", "children"),
    Input("add_btn", "n_clicks"),
    State("code", "value"),
    State("name", "value"),
    State("inst", "value"),
    State("credits", "value"),
)
def add_course_ui(n, code, name, inst, credits):
    if n and all([code, name, inst, credits]):
        add_course(code, name, inst, credits)
        return "Course added successfully!"
    return ""

# ---------- RUN ----------
if __name__ == "__main__":
    app.run(debug=True, port=8050)
