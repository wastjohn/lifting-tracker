# goal: make an app that displays past information on lifts, highliting strengths and weaknesses associated with swims and overall lifts
# 
# The user should be able to see:
# - How my weight changes over time
# - How my times change over time
# - How my lifts change over time
# - How my exercises/lifts/weight correlate with my swims
#
# TODO: 


import streamlit as st
from streamlit_gsheets import GSheetsConnection
import plotly.express as px
import pandas as pd
import numpy as np

st.set_page_config(layout="wide")

# access data from google sheet
url = "https://docs.google.com/spreadsheets/d/1NcRIHGLn1MBLxQE1dgbk55GUWr_ospFCtNKTkVQaZbo/edit?usp=sharing"
conn = st.connection("gsheets", type=GSheetsConnection)
data = conn.read(spreadsheet=url)

# organize and clean data
time = data["Date"]
weight = data["Weight"]
data["Date"] = pd.to_datetime(data['Date'])


def get_lift_df(colname:str, idx:int):
    """
    Get a dataframe with reps and weight for a given lift. Returns empty df if no data provided.
    """
    if pd.isna(data[colname][idx]):
        return pd.DataFrame()
    rows = data[colname][idx].split("\n")
    r_list = []
    w_list = []
    for row in rows[1:]:
        r, w = row.split(", ")
        r_list.append(r)
        w_list.append(w)

    combined = pd.DataFrame({"Reps": r_list, "Weight": w_list})

    combined["Weight"] = combined["Weight"].replace('', "0").astype(float)
    combined["Reps"] = combined["Reps"].astype(float)
    combined["Volume"] = combined["Weight"] * combined["Reps"]
    return combined


def get_lift_stats(df):
    if df.empty:
        return pd.DataFrame({"Total Volume": [0], "Max Volume": [0], "Max Weight": [0], "Reps at Max Weight": [0], "Max Reps": [0]})
    max_volume = df["Volume"].max()
    total_volume = df["Volume"].sum()
    max_weight = df["Weight"].max()
    reps_at_max = df.loc[df["Weight"] == max_weight, "Reps"].values[0]
    max_reps = df["Reps"].max()
    return pd.DataFrame({"Total Volume": [total_volume], "Max Volume": [max_volume], "Max Weight": [max_weight], "Reps at Max Weight": [reps_at_max], "Max Reps": max_reps})


def get_all_lift_stats(colname:str):
    df = pd.DataFrame()
    for idx in range(len(data)):
        lift_df = get_lift_df(colname, idx)
        lift_stats = get_lift_stats(lift_df)
        df = pd.concat([df, lift_stats], ignore_index=True)
        df["Date"] = data["Date"]
        df["Lift"] = data["Lifting day?"]
        df["Weight"] = data["Weight"]
    df = df[df["Max Reps"] != 0]
    return df


def get_delta(colname:str):
    return np.round(data[colname].iloc[-1] - data[colname].iloc[-2], 2)


def get_most_recent(colname:str):
    return data[colname].iloc[-1]


st.title("Strength Performance")  # create title

# calculate PRs and maxes
all_lifts = data.columns.tolist()[5:]
all_PRs = pd.DataFrame()

for l in all_lifts:
    stats = get_all_lift_stats(l)
    stats["Exercise"] = l
    all_PRs = pd.concat([all_PRs, stats], ignore_index=True)


maxes = all_PRs.sort_values("Max Weight", ascending=False).drop_duplicates("Exercise")
maxes["E1RM (Epley)"] = maxes["Max Weight"] * (1 + maxes["Reps at Max Weight"] / 30)
maxes["E1RM (Brzycki)"] = maxes["Max Weight"] / (1.0278 - 0.0278 * maxes["Reps at Max Weight"])
maxes["SWR (Epley)"] = maxes["E1RM (Epley)"] / maxes["Weight"]
maxes["SWR (Brzycki)"] = maxes["E1RM (Brzycki)"] / maxes["Weight"]
previous_maxes = maxes[maxes["Date"] != maxes["Date"].max()]

current_SWR = np.round(maxes[["SWR (Epley)", "SWR (Brzycki)"]].mean().mean(), 2)
previous_SWR = previous_maxes[["SWR (Epley)", "SWR (Brzycki)"]].mean().mean()
d_SWR = np.round(current_SWR - previous_SWR, 2)


# page layout columns
col1, col2, col3, col4 = st.columns(4)  # metrics
lift_col, weight_col = st.columns(2)  # lift and weight plots
pr_container = st.container(border=True)  # PR df


# metrics
col1.metric("Total Volume", f"{all_PRs["Total Volume"].sum()} lbs", f"{all_PRs["Total Volume"].sum() - all_PRs["Total Volume"][:-1].sum()} lbs", border=True)
col2.metric("Weight", f"{get_most_recent("Weight")} lbs", f"{get_delta("Weight")} lbs", delta_color="inverse", border=True)
col3.metric("Strongest Lift", maxes["Max Weight"].max(), maxes["Max Weight"].max() - previous_maxes["Max Weight"].max(), border=True)
col4.metric("Avg. SWR", current_SWR, d_SWR, border=True)


# lift plot
lift_container = lift_col.container(border=True)
lifttype = lift_container.selectbox("Select an exercise to see your history", all_lifts)

lift = all_PRs[all_PRs["Exercise"] == f"{lifttype}"].dropna(axis=1)
y = lift_container.selectbox("Select a parameter to explore", lift.columns.tolist()[:5])
lift_plot = px.scatter(lift, x="Date", y = y, trendline="ols")
lift_container.plotly_chart(lift_plot)








# weight plot
weight_fig = px.scatter(data, x="Date", y="Weight", color="Lifting day?" , trendline="ols", trendline_scope="overall")
weight_container = weight_col.container(border=True)
weight_container.plotly_chart(weight_fig)


# list table of exercises at bottom with columes of exercise name, lifting day, max weight, SWR
pr_container.subheader("Personal Records")
pr_container.text("Ranked by Max Weight")
maxes = maxes.sort_values("Max Weight")
pr_container.dataframe(maxes[["Exercise", "Lift", "Max Weight", "Reps at Max Weight", "E1RM (Epley)", "E1RM (Brzycki)", "SWR (Epley)", "SWR (Brzycki)"]], hide_index=True)


