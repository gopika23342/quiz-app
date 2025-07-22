from flask import Flask, render_template, request, redirect, url_for, send_file, jsonify
import pandas as pd
from datetime import datetime
import os
import random

app = Flask(__name__)

EXCEL_FILE = "responses.xlsx"

# Sample questions
questions = [
    {
        "question": "What situations make you feel stressed at work?",
        "options": ["Tight deadlines", "Conflicts", "Lack of support", "Unclear tasks", "Multitasking"]
    },
    {
        "question": "Which behaviors affect your focus?",
        "options": ["Noise", "Interruptions", "Micromanagement", "Meetings", "Notifications"]
    }
]

# Ensure Excel file exists
if not os.path.exists(EXCEL_FILE):
    df = pd.DataFrame(columns=["Name", "Question", "Answer", "Timestamp"])
    df.to_excel(EXCEL_FILE, index=False)

@app.route("/")
def quiz():
    # Generate anonymous user ID (can be improved to track sessions later)
    random_id = f"Anonymous-{random.randint(1000,9999)}"
    return render_template("drag_and_drop.html", questions=questions, username=random_id)

@app.route("/submit", methods=["POST"])
def submit():
    data = request.get_json()
    username = data.get("username")
    responses = data.get("responses")

    if not username or not responses:
        return jsonify({"message": "Missing data"}), 400

    rows = []
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for question, answers in responses.items():
        rows.append({
            "Name": username,
            "Question": question,
            "Answer": ", ".join(answers),
            "Timestamp": timestamp
        })

    df_new = pd.DataFrame(rows)

    try:
        if os.path.exists(EXCEL_FILE):
            df_existing = pd.read_excel(EXCEL_FILE)
            df_combined = pd.concat([df_existing, df_new], ignore_index=True)
        else:
            df_combined = df_new

        df_combined.to_excel(EXCEL_FILE, index=False)
    except Exception as e:
        print(f"Error writing to Excel: {e}")
        return jsonify({"message": "Error saving data"}), 500

    return jsonify({"message": "Submitted successfully!"})

@app.route("/thankyou")
def thankyou():
    return render_template("thankyou.html")

@app.route("/admin")
def admin():
    try:
        if os.path.exists(EXCEL_FILE):
            df = pd.read_excel(EXCEL_FILE)
            table_html = df.to_html(classes="table table-striped", index=False)
        else:
            table_html = "<p>No responses yet.</p>"
    except Exception as e:
        table_html = f"<p>Error loading responses: {e}</p>"

    return render_template("admin.html", table=table_html)

@app.route("/download")
def download():
    if os.path.exists(EXCEL_FILE):
        return send_file(EXCEL_FILE, as_attachment=True)
    return "No data available yet."

if __name__ == "__main__":
    app.run(debug=True)
