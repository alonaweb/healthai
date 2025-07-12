# 🩺 Med AI – Personal Health & Wellness Assistant

Welcome to **Med AI**, a web-based health assistant designed to help users **track symptoms**, **get health information**, and **receive wellness suggestions** in a chat-style interface.

---

## 📌 Features

- 🔐 **User Authentication** (Login & Registration)
- 📝 **Symptom Tracking** with timestamp
- 📖 **Health Information** on symptoms:
  - Definition
  - Causes
  - Symptoms
  - Remedies
  - Common Medicines
- 🌿 **Wellness Suggestions** based on each symptom
- 💬 **Interactive Chat Interface**
- 📊 **Pie Chart Visualization** of weekly symptom trends
- 🧠 **History Sidebar** for recent interactions

---

## 🧰 Technologies Used

- **Python** – Flask Web Framework  
- **HTML/CSS** – Bootstrap for responsive UI  
- **JavaScript** – Chart.js for charts  
- **SQLite** – Lightweight persistent database  
- **Session Management** – Flask session system  
- **Password Security** – SHA-256 hashing

---

## 🗃️ Project Structure

```
healthai/
├── static/
│   └── doctor.png
├── templates/
│   ├── chat.html
│   ├── login.html
│   ├── register.html
│   ├── history.html
├── health_analysis.py
├── health.db
└── README.md
```

---

## ⚙️ Setup Instructions

```bash
# Clone the repo
git clone https://github.com/alonaweb/healthai.git
cd healthai

# Create virtual environment (optional)
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install flask flask_cors

# Run the app
python health_analysis.py
```

Open your browser and go to:  
👉 `http://127.0.0.1:5002`

---

## 📈 Future Enhancements

- 🧠 Symptom prediction using ML
- 🗂 Export symptom history to PDF/CSV
- 🔔 Health alerts & reminders
- 📱 PWA/mobile version
- 🛡️ Two-factor authentication

---

## 🧑‍💻 Developed By

**Alona Jijo**  
*B.Tech Student*  
*Amal Jyothi College of Engineering, Kanjirappally*

---

## 📄 License

This project is for educational/demo purposes only.  
Consult a real doctor for professional medical advice.
