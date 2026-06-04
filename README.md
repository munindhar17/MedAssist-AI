MedAssist AI

AI-powered symptom analysis and health insights.

MedAssist AI is a full-stack healthcare assistant that analyzes user symptoms using a machine learning model and provides:

Disease prediction
Confidence score
Risk assessment
Severity calculation
Recommended specialist
Nearby doctors
Health analytics dashboard
Voice symptom input
PDF report generation

Live Demo:

🌐 https://med-assist-ai-fawn.vercel.app/

Features
AI symptom-based disease prediction
Voice-to-text symptom input
Health profile management
Prediction confidence visualization
Disease descriptions and precautions
Suggested additional symptoms
Nearby doctor recommendations
PDF report download
Health analytics dashboard
Responsive modern UI
Tech Stack
Frontend
React
Vite
Axios
Chart.js
Backend
FastAPI
Python
Scikit-learn
XGBoost
Pandas
NumPy
Deployment
Frontend: Vercel
Backend: Render
Project Structure
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
Running Locally
Clone repository
git clone https://github.com/munindhar17/MedAssist-AI.git

cd MedAssist-AI
Backend
cd backend

pip install -r requirements.txt

uvicorn main:app --reload

Backend runs at:

http://127.0.0.1:8000

Swagger API:

http://127.0.0.1:8000/docs
Frontend
cd frontend

npm install

npm run dev

Frontend runs at:

http://localhost:5173
API Endpoints
Method	Endpoint	Description
GET	/symptoms	Get available symptoms
POST	/predict	Predict disease
GET	/nearby-doctors	Find nearby doctors
POST	/generate-report	Download PDF report
Sample Prediction
Input Symptoms
chest pain
breathlessness
sweating
Output
Disease: Heart Attack

Confidence: 76.5%

Risk: High

Severity: 28

Recommended Doctor:
Cardiologist
Deployment
Frontend

Vercel:

https://med-assist-ai-fawn.vercel.app/
Backend

Render:

https://medassist-ai-4.onrender.com

API Documentation:

https://medassist-ai-4.onrender.com/docs
Disclaimer

This application is intended for educational and demonstration purposes only.

It is not a substitute for professional medical advice, diagnosis, or treatment. Users should always consult qualified healthcare professionals for medical concerns.

Author

Munindhar Chandanagiri

GitHub:
https://github.com/munindhar17

I would also add a Demo section near the top, because recruiters immediately look for it:

## Live Demo

🌐 Frontend:
https://med-assist-ai-fawn.vercel.app/

⚡ API Docs:
https://medassist-ai-4.onrender.com/docs
