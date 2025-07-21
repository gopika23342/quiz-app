from flask import Flask, render_template, request, send_file
from flask_cors import CORS
import pandas as pd
import io

app = Flask(__name__)
CORS(app)

questions = [
    {
        "question": "What triggers discomfort in communication for you?",
        "options": [
            "Being interrupted while speaking",
            "Getting vague or unclear feedback",
            "Emails or messages being ignored",
            "Being talked over in meetings",
            "Sarcasm or passive-aggressive tone"
        ]
    },
    {
        "question": "What triggers frustration around leadership and authority?",
        "options": [
            "Being micromanaged",
            "Not being recognized for my contributions",
            "Having no say in decisions that affect me",
            "Inconsistent expectations from leadership",
            "Receiving only criticism, no praise"
        ]
    },
    {
        "question": "What team dynamics tend to trigger you?",
        "options": [
            "Team members not meeting commitments",
            "Feeling excluded from team activities",
            "Dominating voices in group settings",
            "Blame games after failures",
            "Lack of team collaboration"
        ]
    },
    {
        "question": "What feedback and evaluation practices do you find triggering?",
        "options": [
            "Receiving feedback in public",
            "No feedback for long periods",
            "Feedback that feels personal, not professional",
            "Being evaluated unfairly or inaccurately",
            "Lack of follow-up after feedback is given"
        ]
    },
    {
        "question": "What triggers discomfort in autonomy and control at work?",
        "options": [
            "Tasks being reassigned without explanation",
            "Not being trusted to make decisions",
            "Strict rules with no flexibility",
            "Constant check-ins or surveillance",
            "Workload imposed without consultation"
        ]
    },
    {
        "question": "What situations around recognition and appreciation trigger you?",
        "options": [
            "Credit being given to someone else",
            "Being overlooked for opportunities",
            "No acknowledgment for extra effort",
            "Praise given only to “favorites”",
            "Recognition only after complaints"
        ]
    },
    {
        "question": "What fairness or equity issues do you find triggering?",
        "options": [
            "Unequal distribution of workload",
            "Promotions without transparency",
            "Double standards for different people",
            "Being paid less than peers",
            "Rules applied inconsistently"
        ]
    },
    {
        "question": "What identity and inclusion-related experiences do you find triggering?",
        "options": [
            "Assumptions made based on my background",
            "Jokes or comments about identity",
            "Being the only one of my kind in the room",
            "Having to “code switch” to fit in",
            "Feeling like I can’t speak freely"
        ]
    }
]

# Store all responses in memory (or extend to DB later)
responses = []

@app.route('/')
def index():
    return render_template("drag_and_drop.html", questions=questions)

@app.route('/submit', methods=['POST'])
def submit():
    data = request.form.to_dict(flat=False)
    formatted = {}
    for qid, answers in data.items():
        formatted[qid] = answers  # list of selected answers
    responses.append(formatted)
    return "Submitted! <br><a href='/'>Back to quiz</a><br><a href='/download_excel'>Download Excel</a>"

@app.route('/download_excel')
def download_excel():
    flat_data = []
    for i, entry in enumerate(responses, start=1):
        row = {'User': f'User {i}'}
        for qidx, answers in entry.items():
            row[f'Q{qidx}'] = ", ".join(answers)
        flat_data.append(row)

    df = pd.DataFrame(flat_data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Responses')
    output.seek(0)
    return send_file(output, as_attachment=True, download_name='quiz_responses.xlsx', mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

if __name__ == '__main__':
    app.run(debug=True)
