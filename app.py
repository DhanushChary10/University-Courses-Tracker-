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

def graph_style(fig, title):
    fig.update_layout(
        title=dict(text=title, x=0.5, font=dict(size=18)),
        paper_bgcolor="#F4F6FA",
        plot_bgcolor="#FFFFFF",
        height=320,
        margin=dict(l=30, r=30, t=60, b=40),
    )
    return fig

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

        dcc.Interval(id="interval", interval=5000, n_intervals=0),

        # ---------- ADD COURSE ----------
        html.Div(
            style={
                "backgroundColor": "white",
                "padding": "15px",
                "borderRadius": "10px",
                "marginBottom": "25px",
            },
            children=[
                html.H3("Add New Course", style={"fontWeight": "bold"}),
                dcc.Input(id="code", placeholder="Course Code"),
                dcc.Input(id="name", placeholder="Course Name"),
                dcc.Input(id="inst", placeholder="Instructor"),
                dcc.Input(id="credits", placeholder="Credits", type="number"),
                html.Br(),
                html.Br(),
                html.Button("Add Course", id="add_btn"),
                html.Div(id="add_msg", style={"color": "green"}),
            ],
        ),

        # ---------- ROW 1 ----------
        html.Div(style={"display": "flex", "gap": "25px", "marginBottom": "25px"}, children=[
            dcc.Graph(id="bar_chart", style={"width": "50%"}),
            dcc.Graph(id="pie_chart", style={"width": "50%"}),
        ]),

        # ---------- ROW 2 ----------
        html.Div(style={"display": "flex", "gap": "25px", "marginBottom": "25px"}, children=[
            dcc.Graph(id="instructor_bar", style={"width": "50%"}),
            dcc.Graph(id="credit_hist", style={"width": "50%"}),
        ]),

        # ---------- ROW 3 ----------
        html.Div(style={"display": "flex", "gap": "25px", "marginBottom": "25px"}, children=[
            dcc.Graph(id="top_courses", style={"width": "50%"}),
            dcc.Graph(id="avg_inst", style={"width": "50%"}),
        ]),

        # ---------- TABLE ----------
        html.Div(
            style={
                "backgroundColor": "white",
                "padding": "15px",
                "borderRadius": "10px",
            },
            children=[
                html.H3("Course Details", style={"fontWeight": "bold"}),
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
    ],
)

# ---------- UPDATE DASHBOARD ----------
@app.callback(
    [
        Output("bar_chart", "figure"),
        Output("pie_chart", "figure"),
        Output("instructor_bar", "figure"),
        Output("credit_hist", "figure"),
        Output("top_courses", "figure"),
        Output("avg_inst", "figure"),
        Output("course_table", "data"),
        Output("course_table", "columns"),
    ],
    Input("interval", "n_intervals"),
)
def update_dashboard(n):
    df = get_data()
    if df.empty:
        return {}, {}, {}, {}, {}, {}, [], []

    bar = graph_style(
        px.bar(df, x="course_name", y="credits",
               color="credits", color_discrete_map=COLOR_MAP),
        "Credits per Course"
    )

    pie = graph_style(
        px.pie(df, names="credits",
               color="credits", color_discrete_map=COLOR_MAP),
        "Credit Distribution"
    )

    inst = df.groupby("instructor").size().reset_index(name="Courses")
    instructor_bar = graph_style(
        px.bar(inst, x="instructor", y="Courses", color="Courses"),
        "Courses per Instructor"
    )

    credit_hist = graph_style(
        px.histogram(df, x="credits", nbins=5),
        "Credits Frequency"
    )

    top = df.sort_values("credits", ascending=False).head(5)
    top_courses = graph_style(
        px.bar(top, x="course_name", y="credits", color="credits"),
        "Top 5 High Credit Courses"
    )

    avg = df.groupby("instructor")["credits"].mean().reset_index()
    avg_inst = graph_style(
        px.bar(avg, x="instructor", y="credits", color="credits"),
        "Average Credits per Instructor"
    )

    columns = [
        {"name": c, "id": c, "editable": c == "instructor"}
        for c in df.columns
    ]

    return (
        bar,
        pie,
        instructor_bar,
        credit_hist,
        top_courses,
        avg_inst,
        df.to_dict("records"),
        columns,
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

    for cid in prev_ids - current_ids:
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
