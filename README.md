# 🩺 MedAssist AI

### AI-Powered Symptom Analysis & Health Insights

MedAssist AI is a full-stack machine learning web application that analyzes user symptoms and predicts possible diseases along with confidence scores, risk levels, severity estimation, specialist recommendations, nearby doctors, and downloadable health reports.

---

## 🌐 Live Demo

**Frontend:**
https://med-assist-ai-fawn.vercel.app/

**Backend API:**
https://medassist-ai-4.onrender.com

**API Documentation (Swagger):**
https://medassist-ai-4.onrender.com/docs

---

## ✨ Features

* AI-based disease prediction
* Voice symptom input
* Smart symptom search
* Health profile management
* Confidence score calculation
* Risk and severity estimation
* Recommended specialist suggestion
* Nearby doctor finder
* PDF report generation
* Health analytics dashboard
* Responsive modern interface

---

## 🖼️ Application Preview

### Home Screen

* Symptom search
* Voice input
* Health profile

### Prediction Results

* Predicted disease
* Confidence percentage
* Risk level
* Severity score
* Doctor recommendation

### Additional Insights

* Disease description
* Causes
* Symptoms
* Foods to avoid
* Exercise suggestions
* Similar conditions
* Suggested missing symptoms

### Analytics Dashboard

* Prediction history
* Risk distribution
* Severity trends

---

## 🛠️ Tech Stack

### Frontend

* React
* Vite
* Axios
* Chart.js

### Backend

* Python
* FastAPI
* Scikit-learn
* XGBoost
* Pandas
* NumPy

### Deployment

* Vercel
* Render

---

## 📂 Project Structure

```text
MedAssist-AI/
│
├── frontend/
│   ├── src/
│   ├── public/
│   └── package.json
│
├── backend/
│   ├── main.py
│   ├── ml/
│   ├── models/
│   ├── utils/
│   └── requirements.txt
│
├── datasets/
├── tests/
└── README.md
```

---

## 🚀 Local Setup

### Clone Repository

```bash
git clone https://github.com/munindhar17/MedAssist-AI.git
cd MedAssist-AI
```

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

Backend runs on:

```
http://127.0.0.1:8000
```

Swagger API:

```
http://127.0.0.1:8000/docs
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on:

```
http://localhost:5173
```

---

## 📡 API Endpoints

| Method | Endpoint           | Description                |
| ------ | ------------------ | -------------------------- |
| GET    | `/symptoms`        | Get all available symptoms |
| POST   | `/predict`         | Predict disease            |
| GET    | `/nearby-doctors`  | Get nearby doctors         |
| POST   | `/generate-report` | Generate PDF report        |

---

## 📊 Example Prediction

### Input Symptoms

* Chest Pain
* Breathlessness
* Sweating

### Output

```
Disease           : Heart Attack
Confidence Score  : 76.5%
Risk Level        : High
Severity Score    : 28
Recommended Doctor: Cardiologist
```

---

## 🔮 Future Improvements

* User authentication
* Appointment booking
* Real hospital API integration
* Patient history management
* Multi-language support
* Mobile application
* Cloud database integration

---

## ⚠️ Disclaimer

This project is developed for educational and demonstration purposes only.

It is not intended to replace professional medical advice, diagnosis, or treatment. Always consult a qualified healthcare professional for medical concerns.

---

## 👨‍💻 Author

**Munindhar Chandanagiri**

GitHub:
https://github.com/munindhar17

---

## ⭐ Support

If you found this project useful, please consider giving it a ⭐ on GitHub.
