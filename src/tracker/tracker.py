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
from streamlit_gsheets import GSheetsConnection


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
        self.weight_fig = None


    def format_data(self):
        self.data["Date"] = pd.to_datetime(self.data['Date'])

    
    def get_weight_plot(self):
        if hasattr(self, 'weight_fig') and self.weight_fig is not None:
            plt.close(self.weight_fig)

        data = self.data
        x = mdates.date2num(data["Date"])
        y = data["Weight"]

        mask = ~np.isnan(x) & ~np.isnan(y)
        coeffs = np.polyfit(x[mask], y[mask], 1)
        trendline_fn = np.poly1d(coeffs)

        fig, ax = plt.subplots(figsize=(6, 4))
        ax.scatter(data["Date"], data["Weight"], s=1)
        ax.plot(x, trendline_fn(x))
        ax.set_xlabel("Date")
        ax.set_ylabel("Weight (lbs)")
        fig.autofmt_xdate()

        self.weight_fig = fig
        return fig

    

if __name__ == "__main__":
    url = "https://docs.google.com/spreadsheets/d/1NcRIHGLn1MBLxQE1dgbk55GUWr_ospFCtNKTkVQaZbo/edit?usp=sharing"
    t = Tracker(url)
    t.format_data()
    fig = t.get_weight_plot()
    fig.savefig("weight_trend_test.png", bbox_inches="tight")

