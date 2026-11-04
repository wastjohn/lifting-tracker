"""
File: weekly_email_update.py

This file generates a weekly summary of swimming and lifting stats.

Brainstorm:
- What important stats do I want to see each week?
    Training volume, max weight, my weight trend, any improvements to lifts --> weekly summary statistics
- List of PRs?
    Make note of how far off I was from my PR?
- Strength, Swimming, Mobility Benchmarks
    Strength: Vertical, Weighted Pullup SWR
    Swimming: TODO
    Mobility: TODO
- Sleep Statistics
- Walking Statistics

Format:
Subject: Weekly Progress Update
Body:
- Show past 7 days
    For each day, display phase and workouts completed (rows, cols = workouts, (reps, weight); add * if it was an improvement from last week add ** if it was a new PR)
    Also include total volume for that day at bottom
- Weight Trend
- Sleep Statistics
- Walking Statistics
- List of PRs


Author: Will St. John
Fall 2026
"""


import os
import io
import smtplib
from email.message import EmailMessage
from email.utils import make_msgid
from tracker import Tracker



def get_html_week(tracker):
    html_table = tracker.get_weekly_PRs()
    return html_table


def get_html_progress_plot(tracker):
    tracker.create_fig((12, 10), 8, 3)
    tracker.add_weekly_steps_plot()
    tracker.add_weekly_weight_plot()
    tracker.add_weekly_sleep_plot()
    tracker.add_weight_plot()
    fig = tracker.get_fig()
    img_buf = io.BytesIO()
    fig.savefig(img_buf, format="png", bbox_inches='tight', dpi=150)
    img_buf.seek(0)
    return img_buf.read()


def get_html_PRs():
    return


def send_weekly_email():
    SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
    SENDER_PASSWORD = os.environ.get("SENDER_PASSWORD")
    RECEIVER_EMAIL = os.environ.get("RECEIVER_EMAIL")

    msg = EmailMessage()
    msg["Subject"] = "Your Weekly Progress Update"
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECEIVER_EMAIL

    url = "https://docs.google.com/spreadsheets/d/1NcRIHGLn1MBLxQE1dgbk55GUWr_ospFCtNKTkVQaZbo/edit?usp=sharing"
    tracker = Tracker(url)
    tracker.format_data()
    html_table = get_html_week(tracker)

    chart_cid = make_msgid()

    html_content = f"""
    <!DOCTYPE html>
    <html>
        <body>
            <h2 style="color: #306998;">
                Weekly Performance Report
            </h2>

            <p>
                Hello! Here is the automated trend visualization
                for this week:
            </p>

            <div style="margin: 20px 0;">
                <img
                    src="cid:{chart_cid[1:-1]}"
                    alt="Weekly Trend Chart"
                    style="max-width: 100%; height: auto;"
                >
            </div>

            <!-- Injected Exercise Table Section -->
            <div style="margin: 20px 0; overflow-x: auto;">
                {html_table}
            </div>

            <hr>

            <p style="font-size: 12px; color: gray;">
                Automated via GitHub Actions Cron Job.
            </p>
        </body>
    </html>
    """

    msg.add_alternative(html_content, subtype="html")

    image_data = get_html_progress_plot(tracker)

    html_part = msg.get_payload()[-1]

    html_part.add_related(
        image_data,
        maintype="image",
        subtype="png",
        cid=chart_cid
    )
    try:
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=30) as server:
            server.starttls()

            server.login(
                SENDER_EMAIL,
                SENDER_PASSWORD
            )

            refused = server.send_message(msg)

            if refused:
                print(f"Recipients refused: {refused}")
            else:
                print("Gmail accepted the message.")

    except Exception as e:
        print(f"Failed to send email: {e}")
        raise

if __name__ == "__main__":
    send_weekly_email()