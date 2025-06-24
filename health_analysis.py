from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_cors import CORS
import sqlite3
import datetime
import random
import hashlib

app = Flask(__name__)
CORS(app)
app.secret_key = 'your_secret_key_here'

# Initialize DB
def init_db():
    conn = sqlite3.connect("health.db")
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS symptoms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            symptom TEXT,
            timestamp TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)
    conn.commit()
    conn.close()

init_db()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def normalize_symptom(symptom):
    mapping = {
        "chest pain": "back pain", "tiredness": "fatigue", "runny nose": "cold",
        "difficulty sleeping": "insomnia", "lightheadedness": "dizziness", "heartburn": "acidity",
        "throat pain": "sore throat", "rash": "skin rash", "stomach pain": "vomiting",
        "body ache": "fever", "irritability": "anxiety"
    }
    return mapping.get(symptom.lower(), symptom.lower())

# 15+ Symptom Definitions and Suggestions
defined_info = {
    "fever": {
        "definition": "Temporary rise in body temperature.",
        "causes": "Infection, inflammation, or heat stroke.",
        "symptoms": "High temp, chills, headache, sweating.",
        "remedies": "Stay hydrated, wear light clothes.",
        "medicines": "Paracetamol, ibuprofen.",
        "wellness": ["Rest well", "Drink fluids", "Light clothing"]
    },
    "cough": {
        "definition": "Reflex to clear the throat or lungs.",
        "causes": "Colds, allergies, infection.",
        "symptoms": "Dry or wet cough, sore throat.",
        "remedies": "Honey, steam, warm liquids.",
        "medicines": "Cough syrup, lozenges.",
        "wellness": ["Warm fluids", "Avoid cold foods", "Gargle salt water"]
    },
    "cold": {
        "definition": "Viral infection of nose/throat.",
        "causes": "Rhinoviruses.",
        "symptoms": "Sneezing, congestion, sore throat.",
        "remedies": "Rest, steam, fluids.",
        "medicines": "Decongestants, antihistamines.",
        "wellness": ["Stay warm", "Steam", "Herbal tea"]
    },
    "headache": {
        "definition": "Pain in head or neck area.",
        "causes": "Stress, dehydration, eyestrain.",
        "symptoms": "Throbbing or sharp pain.",
        "remedies": "Rest, compress, fluids.",
        "medicines": "Paracetamol, ibuprofen.",
        "wellness": ["Dark room", "Massage", "Cold pack"]
    },
    "fatigue": {
        "definition": "Persistent tiredness.",
        "causes": "Lack of sleep, anemia, stress.",
        "symptoms": "Exhaustion, low focus.",
        "remedies": "Sleep, light activity.",
        "medicines": "Treat cause, multivitamins.",
        "wellness": ["Short nap", "Fruit snack", "Gentle walk"]
    },
    "anxiety": {
        "definition": "Excessive worry or fear.",
        "causes": "Stress, mental health disorder.",
        "symptoms": "Palpitations, restlessness.",
        "remedies": "Relaxation, therapy.",
        "medicines": "SSRIs, benzodiazepines.",
        "wellness": ["Deep breathing", "Meditation", "Journaling"]
    },
    "diarrhea": {
        "definition": "Frequent loose stools.",
        "causes": "Food poisoning, infection.",
        "symptoms": "Loose stool, cramps.",
        "remedies": "ORS, rice, bananas.",
        "medicines": "ORS, loperamide.",
        "wellness": ["Eat BRAT diet", "Hydrate", "Rest"]
    },
    "constipation": {
        "definition": "Difficulty passing stools.",
        "causes": "Low fiber, dehydration.",
        "symptoms": "Bloating, hard stool.",
        "remedies": "Fiber foods, water, walk.",
        "medicines": "Laxatives short-term.",
        "wellness": ["Warm water", "Walk", "Fruits"]
    },
    "sore throat": {
        "definition": "Throat irritation and pain.",
        "causes": "Infection, dry air.",
        "symptoms": "Painful swallowing.",
        "remedies": "Salt water gargle.",
        "medicines": "Lozenges, analgesics.",
        "wellness": ["Warm tea", "Honey", "Rest voice"]
    },
    "vomiting": {
        "definition": "Expulsion of stomach contents.",
        "causes": "Foodborne illness, motion sickness.",
        "symptoms": "Nausea, stomach pain.",
        "remedies": "Clear liquids, ginger.",
        "medicines": "Ondansetron, domperidone.",
        "wellness": ["Rest", "Sips of water", "Avoid solids"]
    },
    "back pain": {
        "definition": "Discomfort in lower/upper back.",
        "causes": "Posture, injury, strain.",
        "symptoms": "Stiffness, ache.",
        "remedies": "Stretch, compress.",
        "medicines": "Painkillers, muscle relaxants.",
        "wellness": ["Gentle stretching", "Good posture", "Short walks"]
    },
    "acidity": {
        "definition": "Excess stomach acid.",
        "causes": "Spicy food, stress.",
        "symptoms": "Heartburn, reflux.",
        "remedies": "Cold milk, small meals.",
        "medicines": "Antacids, PPIs.",
        "wellness": ["Avoid late meals", "No fried foods", "Stay upright after eating"]
    },
    "skin rash": {
        "definition": "Skin inflammation or irritation.",
        "causes": "Allergies, infection.",
        "symptoms": "Redness, itching.",
        "remedies": "Cool compress, lotion.",
        "medicines": "Antihistamines, cream.",
        "wellness": ["Loose clothes", "Cool baths", "Mild soap"]
    },
    "insomnia": {
        "definition": "Difficulty sleeping.",
        "causes": "Anxiety, blue light, caffeine.",
        "symptoms": "Lack of sleep, fatigue.",
        "remedies": "Sleep hygiene, relax.",
        "medicines": "Melatonin, sleeping pills (prescribed).",
        "wellness": ["No screens", "Bedtime routine", "Warm milk"]
    },
    "dizziness": {
        "definition": "Feeling faint or unsteady.",
        "causes": "Dehydration, low BP.",
        "symptoms": "Spinning, lightheadedness.",
        "remedies": "Lie down, hydrate.",
        "medicines": "Meclizine, fluids.",
        "wellness": ["Rest", "Avoid sudden moves", "Hydrate"]
    },
    "default": {
        "definition": "No information available.",
        "causes": "-",
        "symptoms": "-",
        "remedies": "-",
        "medicines": "-",
        "wellness": ["Drink water", "Rest", "Consult a doctor"]
    }
}

# ROUTES
@app.route("/")
def home():
    return redirect(url_for('login'))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = hash_password(request.form['password'])
        conn = sqlite3.connect("health.db")
        cur = conn.cursor()
        cur.execute("SELECT id FROM users WHERE username = ? AND password = ?", (username, password))
        user = cur.fetchone()
        conn.close()
        if user:
            session['user_id'] = user[0]
            session['username'] = username
            return redirect(url_for('chat'))
        return render_template("login.html", error="Invalid credentials")
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form['username']
        password = hash_password(request.form['password'])
        try:
            conn = sqlite3.connect("health.db")
            cur = conn.cursor()
            cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
        except:
            return render_template("register.html", error="Username already exists")
    return render_template("register.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route("/chat")
def chat():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template("chat.html", username=session['username'])

@app.route("/chat_api", methods=["POST"])
def chat_api():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    data = request.json
    raw_input = data.get("message", "")
    symptom = normalize_symptom(raw_input)
    timestamp = datetime.datetime.now().isoformat()

    conn = sqlite3.connect("health.db")
    cur = conn.cursor()
    cur.execute("INSERT INTO symptoms (user_id, symptom, timestamp) VALUES (?, ?, ?)",
                (session['user_id'], symptom, timestamp))
    conn.commit()
    conn.close()

    entry = defined_info.get(symptom, defined_info["default"])
    suggestion = random.choice(entry["wellness"])
    reply = f"""✅ Symptom '{symptom}' recorded.

📖 Definition: {entry['definition']}
❓ Causes: {entry['causes']}
🩺 Symptoms: {entry['symptoms']}
💡 Remedies: {entry['remedies']}
💊 Medicines: {entry['medicines']}
🌿 Suggestion: {suggestion}
"""
    return jsonify({"response": reply})

@app.route("/symptom_trend")
def symptom_trend():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    conn = sqlite3.connect("health.db")
    cur = conn.cursor()
    cur.execute("""
        SELECT DATE(timestamp), COUNT(*) FROM symptoms
        WHERE user_id = ?
        GROUP BY DATE(timestamp)
        ORDER BY DATE(timestamp) DESC
        LIMIT 7
    """, (session['user_id'],))
    rows = cur.fetchall()
    conn.close()
    return jsonify([{"date": r[0], "count": r[1]} for r in reversed(rows)])

@app.route("/symptom_summary")
def symptom_summary():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    conn = sqlite3.connect("health.db")
    cur = conn.cursor()
    cur.execute("""
        SELECT symptom, COUNT(*) FROM symptoms
        WHERE user_id = ? AND DATE(timestamp) >= DATE('now', '-7 day')
        GROUP BY symptom
    """, (session['user_id'],))
    rows = cur.fetchall()
    conn.close()
    return jsonify([{"symptom": r[0], "count": r[1]} for r in rows])

@app.route("/symptom_times")
def symptom_times():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    conn = sqlite3.connect("health.db")
    cur = conn.cursor()
    cur.execute("SELECT strftime('%H', timestamp) FROM symptoms WHERE user_id = ?", (session['user_id'],))
    hours = cur.fetchall()
    conn.close()
    bins = {'Morning': 0, 'Afternoon': 0, 'Evening': 0, 'Night': 0}
    for (hour,) in hours:
        hour = int(hour)
        if 5 <= hour < 12: bins['Morning'] += 1
        elif 12 <= hour < 17: bins['Afternoon'] += 1
        elif 17 <= hour < 21: bins['Evening'] += 1
        else: bins['Night'] += 1
    return jsonify(bins)
@app.route("/history")
def history():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = sqlite3.connect("health.db")
    cur = conn.cursor()
    cur.execute("""
        SELECT symptom, timestamp FROM symptoms
        WHERE user_id = ?
        ORDER BY timestamp DESC
        LIMIT 20
    """, (session['user_id'],))
    rows = cur.fetchall()
    conn.close()

    return render_template("history.html", history=rows, username=session.get('username'))
if __name__ == '__main__':
    print("✅ Running Health Assistant at http://127.0.0.1:5002")
    app.run(debug=True, port=5002)
