
from flask import Flask, render_template, request, session
import json, os
from datetime import date, timedelta, datetime
from question_bank import generate_question, generate_sats_paper, choose_topic
from curriculum import WORLDS, LESSONS

try:
    from openai import OpenAI
except Exception:
    OpenAI = None

app = Flask(__name__)
app.secret_key = "year4-maths-secret"

PROGRESS_FILE = "progress.json"

def load_progress():
    if not os.path.exists(PROGRESS_FILE):
        return {
            "xp": 0, "level": 1, "world": 1, "streak": 0, "last_played": "",
            "total": 0, "correct": 0, "badges": [],
            "topics": {
                "place_value": {"correct": 0, "total": 0},
                "addition": {"correct": 0, "total": 0},
                "subtraction": {"correct": 0, "total": 0},
                "multiplication": {"correct": 0, "total": 0},
                "division": {"correct": 0, "total": 0},
                "fractions": {"correct": 0, "total": 0},
                "measurement": {"correct": 0, "total": 0},
                "geometry": {"correct": 0, "total": 0},
                "statistics": {"correct": 0, "total": 0}
            }
        }
    with open(PROGRESS_FILE) as f:
        return json.load(f)

def save_progress(data):
    with open(PROGRESS_FILE, "w") as f:
        json.dump(data, f, indent=2)

def compute_accuracy(data):
    if data["total"] == 0:
        return 0
    return int((data["correct"] / data["total"]) * 100)

def maybe_update_streak(data):
    today = date.today()
    last = data.get("last_played", "")
    if not last:
        data["streak"] = 1
        data["last_played"] = str(today)
        return
    last_date = datetime.strptime(last, "%Y-%m-%d").date()
    if last_date == today:
        return
    if last_date == today - timedelta(days=1):
        data["streak"] += 1
    else:
        data["streak"] = 1
    data["last_played"] = str(today)

def update_badges(data):
    badges = set(data.get("badges", []))
    if data["correct"] >= 10:
        badges.add("10 Correct")
    if data["correct"] >= 50:
        badges.add("50 Correct")
    if data["streak"] >= 3:
        badges.add("3-Day Streak")
    if data["streak"] >= 7:
        badges.add("7-Day Streak")
    if data["world"] >= 5:
        badges.add("Explorer")
    if data["world"] >= 10:
        badges.add("SATs Summit Reached")
    for topic, stats in data["topics"].items():
        if stats["total"] >= 10 and stats["correct"] / max(1, stats["total"]) >= 0.8:
            badges.add(f"{topic.replace('_',' ').title()} Star")
    data["badges"] = sorted(list(badges))

def ai_explain(question, correct_answer, user_answer):
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key or OpenAI is None:
        return "Try it step by step. Look carefully at the numbers, then solve one part at a time."
    try:
        client = OpenAI(api_key=api_key)
        prompt = (
            "Explain to a 9-year-old how to solve this Year 4 maths problem in short simple steps. "
            f"Question: {question} "
            f"Student answer: {user_answer}. Correct answer: {correct_answer}. "
            "Keep it friendly and concise."
        )
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return "Try it step by step. Look carefully at the numbers, then solve one part at a time."

@app.route("/", methods=["GET", "POST"])
def home():
    data = load_progress()
    maybe_update_streak(data)

    question = None
    result = None
    explanation = None
    lesson = None

    current_world = data.get("world", 1)
    if current_world > 10:
        current_world = 10

    if request.method == "POST":
        action = request.form.get("action")

        if action == "lesson":
            world_topic = WORLDS[current_world-1]["topic"]
            if world_topic == "mixed":
                world_topic = choose_topic(data, current_world)
            lesson = LESSONS.get(world_topic, LESSONS["addition"])

        elif action == "new":
            topic = choose_topic(data, current_world)
            question_text, answer, built_in_explanation = generate_question(topic, data["level"])
            session["question"] = question_text
            session["answer"] = answer
            session["topic"] = topic
            session["built_in_explanation"] = built_in_explanation
            question = question_text

        elif action == "submit":
            user_answer = request.form.get("answer", "").strip()
            correct = str(session.get("answer", "")).strip()
            question = session.get("question")
            topic = session.get("topic", "addition")
            built_in_explanation = session.get("built_in_explanation", "")

            data["total"] += 1
            data["topics"][topic]["total"] += 1

            if user_answer.lower() == correct.lower():
                result = "Correct! 🎉"
                data["correct"] += 1
                data["topics"][topic]["correct"] += 1
                data["xp"] += 10
                if data["xp"] >= data["level"] * 100:
                    data["level"] += 1
                if data["level"] > data["world"] * 5 and data["world"] < 10:
                    data["world"] += 1
            else:
                result = f"Not quite. Correct answer: {correct}"
                explanation = ai_explain(question, correct, user_answer)
                if explanation.startswith("Try it step by step") and built_in_explanation:
                    explanation = built_in_explanation

            update_badges(data)

        save_progress(data)

    accuracy = compute_accuracy(data)
    worlds = WORLDS
    current_world_info = worlds[current_world-1]

    return render_template(
        "index.html",
        progress=data,
        accuracy=accuracy,
        worlds=worlds,
        current_world=current_world,
        current_world_info=current_world_info,
        question=question,
        result=result,
        explanation=explanation,
        lesson=lesson
    )

@app.route("/test")
def test():
    paper = generate_sats_paper()
    return render_template("test.html", paper=paper)

@app.route("/parent")
def parent():
    data = load_progress()
    accuracy = compute_accuracy(data)

    topic_rows = []
    for topic, stats in data["topics"].items():
        topic_accuracy = 0
        if stats["total"] > 0:
            topic_accuracy = int((stats["correct"] / stats["total"]) * 100)
        topic_rows.append({
            "topic": topic.replace("_", " ").title(),
            "correct": stats["correct"],
            "total": stats["total"],
            "accuracy": topic_accuracy
        })

    weakest = sorted(topic_rows, key=lambda x: x["accuracy"] if x["total"] > 0 else 999)
    return render_template(
        "parent.html",
        progress=data,
        accuracy=accuracy,
        topic_rows=topic_rows,
        weakest=weakest[:3]
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
