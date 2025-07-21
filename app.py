from flask import Flask, render_template, request, jsonify, send_file
import sqlite3, pandas as pd, io
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Questions list
questions = [
    {
        "question": "Feedback & Evaluation Triggers",
        "options": [
            "Receiving feedback in public",
            "No feedback for long periods",
            "Feedback that feels personal, not professional",
            "Being evaluated unfairly or inaccurately",
            "Lack of follow-up after feedback is given"
        ]
    },
    {
        "question": "Autonomy & Control Triggers",
        "options": [
            "Tasks being reassigned without explanation",
            "Not being trusted to make decisions",
            "Strict rules with no flexibility",
            "Constant check-ins or surveillance",
            "Workload imposed without consultation"
        ]
    }
]

@app.route("/")
def index():
    return render_template("drag_and_drop.html", username="User1", questions=questions)

@app.route("/submit", methods=["POST"])
def submit():
    data = request.get_json()
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS responses (
        username TEXT,
        question_id INTEGER,
        answer TEXT,
        submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")
    for qid, ans_list in data["answers"].items():
        qid_int = int(qid)
        for ans in ans_list:
            cursor.execute("INSERT INTO responses (username, question_id, answer) VALUES (?, ?, ?)",
                           (data["username"], qid_int, ans))
    conn.commit()
    conn.close()
    return jsonify({"status": "success"})

@app.route("/download")
def download():
    conn = sqlite3.connect("data.db")
    df = pd.read_sql_query("SELECT * FROM responses", conn)
    conn.close()
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name="Responses")
    output.seek(0)
    return send_file(output, download_name="quiz_responses.xlsx", as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
