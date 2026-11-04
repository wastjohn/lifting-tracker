"""
File: tracker.py

Primary module for extracting data from my lifting spreadsheet.

Author: Will St. John
Date: Fall 2026
"""

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pandas import DataFrame
# from streamlit_gsheets import GSheetsConnection


class Tracker:
    def __init__(self, spreadsheet_url):
        # conn = st.connection("gsheets", type=GSheetsConnection)
        # data = conn.read(spreadsheet=spreadsheet_url)

         # Convert standard sharing link to a direct backend CSV export endpoint
        if "/edit" in spreadsheet_url:
            csv_url = spreadsheet_url.split("/edit")[0] + "/export?format=csv"
        else:
            csv_url = spreadsheet_url
            
        # Download straight into memory without needing Streamlit connections
        self.data = pd.read_csv(csv_url)
        self.fig = None
        self.gs = None
        self.table = None


    def format_data(self):
        self.data["Date"] = pd.to_datetime(self.data['Date'])


    def get_fig(self):
        return self.fig


    def create_fig(self, figsize, nrow, ncol):
        self.fig = plt.figure(figsize=figsize)
        self.gs = self.fig.add_gridspec(nrow, ncol, hspace=0.7, wspace=0.3)
        
    
    def get_data_between(self, start_date, end_date):
        data = self.data
        mask = data["Date"].between(start_date, end_date)
        return data[mask]


    def add_weekly_steps_plot(self):
        today = pd.Timestamp.today().strftime('%Y-%m-%d')
        week_ago = (pd.Timestamp.today() - pd.Timedelta(days=6)).strftime('%Y-%m-%d')
        data = self.get_data_between(week_ago, today)
        fig = self.fig
        gs = self.gs
        
        x = mdates.date2num(data["Date"])
        y = data["Yesterday's Steps"]

        mask = ~np.isnan(x) & ~np.isnan(y)
        coeffs = np.polyfit(x[mask], y[mask], 1)
        trendline_fn = np.poly1d(coeffs)

        ax = fig.add_subplot(gs[:2, :])
        ax.scatter(data["Date"], data["Yesterday's Steps"], color="tab:green")
        ax.plot(x, trendline_fn(x), linestyle="--", color="tab:green")
        ax.set_ylabel("Previous Day Steps")
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))



    def add_weekly_weight_plot(self):
        today = pd.Timestamp.today().strftime('%Y-%m-%d')
        week_ago = (pd.Timestamp.today() - pd.Timedelta(days=6)).strftime('%Y-%m-%d')
        data = self.get_data_between(week_ago, today)
        fig = self.fig
        gs = self.gs
        
        x = mdates.date2num(data["Date"])
        y = data["Weight"]

        mask = ~np.isnan(x) & ~np.isnan(y)
        coeffs = np.polyfit(x[mask], y[mask], 1)
        trendline_fn = np.poly1d(coeffs)

        ax = fig.add_subplot(gs[2:4, :])
        ax.scatter(data["Date"], data["Weight"], color="tab:orange")
        ax.plot(x, trendline_fn(x), linestyle="--", color="tab:orange")
        ax.set_ylabel("Weight (lbs)")
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))


    def add_weekly_sleep_plot(self):
        today = pd.Timestamp.today().strftime('%Y-%m-%d')
        week_ago = (pd.Timestamp.today() - pd.Timedelta(days=6)).strftime('%Y-%m-%d')
        data = self.get_data_between(week_ago, today)[["Last Night's Sleep Energy Score", 
                        "Sleep Time (min)", "Actual Sleep Time (min)", "Deep Sleep (min)", 
                        "REM Sleep (min)", "Awake (min)", "Sleep Latency (min)", "Date"]]
        fig = self.fig
        gs = self.gs
        
        sleep_data = data[["Sleep Time (min)", "Actual Sleep Time (min)", "Deep Sleep (min)", 
                        "REM Sleep (min)", "Awake (min)", "Sleep Latency (min)"]]

        
        ax1 = fig.add_subplot(gs[4:6, 0])
        ax2 = fig.add_subplot(gs[4:6, 1:])

        ax1.scatter(data["Date"], data["Last Night's Sleep Energy Score"])
        ax1.plot(data["Date"], data["Last Night's Sleep Energy Score"])
        ax1.set_ylabel("Previous Night Sleep Score")
        ax1.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
        ax1.tick_params(axis="x", rotation=25) 


        sleep_data.boxplot(ax=ax2, grid=False)
        ax2.set_ylabel("Time (min)")
        manual_labels = ["Sleep Time", "Actual", "Deep", "REM", "Awake", "Latency"]
        ax2.set_xticklabels(manual_labels, fontsize=10) 


    def add_weight_plot(self):
        # if hasattr(self, 'fig') and self.fig is not None:
        #     plt.close(self.fig)

        data = self.data
        fig = self.fig
        gs = self.gs
        x = mdates.date2num(data["Date"])
        y = data["Weight"]

        today = pd.Timestamp.today().strftime('%Y-%m-%d')
        week_ago = (pd.Timestamp.today() - pd.Timedelta(days=6)).strftime('%Y-%m-%d')
        last_weeks_data = self.get_data_between(week_ago, today)

        mask = ~np.isnan(x) & ~np.isnan(y)
        coeffs = np.polyfit(x[mask], y[mask], 1)
        trendline_fn = np.poly1d(coeffs)

        ax = fig.add_subplot(gs[-2:, :])
        ax.scatter(data["Date"], data["Weight"], s=2)
        ax.scatter(last_weeks_data["Date"], last_weeks_data["Weight"], s=2, color="tab:orange")
        ax.plot(x, trendline_fn(x), label=f"y={coeffs[0]:.2f}x+{coeffs[1]:.2f}")
        ax.set_ylabel("Weight (lbs)")
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
        ax.legend()


    def get_PRs(self):
        return

    
    def get_weekly_PRs(self):
        today = pd.Timestamp.today().strftime('%Y-%m-%d')
        week_ago = (pd.Timestamp.today() - pd.Timedelta(days=6)).strftime('%Y-%m-%d')
        data = self.get_data_between(week_ago, today)

        exclude_cols = [
        'Submission ID', 'Submission time', 'Date', 'Weight', "Yesterday's Steps", 
        "Last Night's Sleep Energy Score", 'Sleep Time (min)', 'Actual Sleep Time (min)', 
        'Deep Sleep (min)', 'REM Sleep (min)', 'Awake (min)', 'Sleep Latency (min)', 
        'Lifting phase', 'Lifting day', 'Notes', 'Enjoyment Rating', 
        'Challenge Rating', 'Tiredness Rating'
        ]

        exercise_cols = [col for col in data.columns if col not in exclude_cols]

        exercise_data = data[exercise_cols].replace('Reps, Weight', np.nan)


        days_dict = {}
        max_rows = 0

        # 2. Iterate through each submission row in order (Chronological Days)
        for idx, row in data.iterrows():
            # Convert the date string into a beautiful "%b %d" format (e.g., Oct 29)
            date_obj = pd.to_datetime(row['Date'])
            date_str = date_obj.strftime('%b %d')
            
            day_list = []

            # --- Insert Phase and Lifting Day as the top rows ---
            phase_val = str(row.get('Lifting phase', '')).strip()
            day_val = str(row.get('Lifting day', '')).strip()
            
            # If the values exist and aren't null string representations
            if phase_val and phase_val.lower() != 'nan':
                day_list.append(f"<span class='meta-tag phase-tag'>{phase_val}</span>")
            else:
                day_list.append("<span class='meta-tag empty-tag'>-</span>")
                
            if day_val and day_val.lower() != 'nan':
                day_list.append(f"<span class='meta-tag day-tag'>{day_val}</span>")
            else:
                day_list.append("<span class='meta-tag empty-tag'>-</span>")
            
            # 3. Iterate through exercises in the exact sequence of your column index
            for exercise in exercise_cols:
                details = exercise_data.loc[idx, exercise]
                
                # If the cell has real tracking text (numbers/reps) left over
                if pd.notna(details) and str(details).strip() != '':
                    clean_details = str(details).replace("Reps, Weight\n", "").strip()
                    formatted_details = clean_details.replace("\n", "<br>")
                    
                    cell_html = f"<strong>{exercise}</strong><br><span class='sets'>{formatted_details}</span>"
                    day_list.append(cell_html)
                    
            # If no exercise data was recorded on this date, flag it explicitly as a rest day
            if not day_list:
                day_list.append("<em style='color:#a0a0a0; font-style: italic;'>Rest Day</em>")
                
            days_dict[date_str] = day_list
            max_rows = max(max_rows, len(day_list))

        # 4. Uniformly pad shorter columns so they match the longest workout day
        for date_str in days_dict:
            while len(days_dict[date_str]) < max_rows:
                days_dict[date_str].append("")

        # 5. Build the final structured HTML document
        html_df = pd.DataFrame(days_dict)
        html_table = html_df.to_html(index=False, escape=False, classes="workout-table")

        return html_table


    

if __name__ == "__main__":
    url = "https://docs.google.com/spreadsheets/d/1NcRIHGLn1MBLxQE1dgbk55GUWr_ospFCtNKTkVQaZbo/edit?usp=sharing"
    t = Tracker(url)
    t.format_data()
    t.create_fig((12, 10), 8, 3)
    t.add_weekly_steps_plot()
    t.add_weekly_weight_plot()
    t.add_weekly_sleep_plot()
    t.add_weight_plot()
    fig = t.get_fig()
    # fig.savefig("weight_trend_test.png", bbox_inches="tight")
    data = t.get_weekly_PRs()
    plt.close()

