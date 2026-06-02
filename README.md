# MedAssist AI

AI-assisted symptom triage with disease ranking, confidence calibration, triage levels, doctor recommendations, analytics, PDF reports, and contextual Ask MedAssist support.

This tool is informational only and is not a substitute for professional medical care.

## Local Setup

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

If running from the repository root:

```bash
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Default local URLs:

- Backend: `http://127.0.0.1:8000`
- Frontend: `http://localhost:5173`

## Environment Variables

Create `.env` files for deployment-specific values.

Backend `.env` example:

```bash
ENV=production
DEBUG_PREDICTIONS=False
ALLOWED_ORIGINS=https://your-vercel-app.vercel.app
```

Frontend `.env` example:

```bash
VITE_API_URL=https://your-render-backend.onrender.com
```

## Deployment

### Backend on Render

1. Create a new Render Web Service.
2. Connect this repository.
3. Set the root directory to the repository root.
4. Use a Python runtime.
5. Build command:

```bash
pip install -r backend/requirements.txt
```

6. Start command:

```bash
uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

7. Add environment variables from the backend `.env` example.

### Frontend on Vercel

1. Import the repository into Vercel.
2. Set the project root to `frontend`.
3. Build command:

```bash
npm run build
```

4. Output directory:

```bash
dist
```

5. Add `VITE_API_URL` pointing to the Render backend URL.

## Prediction Versioning

Current prediction engine version: `v3`.

Analytics and history only use latest-version predictions so older scoring behavior does not pollute severity trends or disease counts.

## Production Notes

- Keep `DEBUG_PREDICTIONS=False` in production.
- Review CORS origins before deployment.
- The model is only one input. Final ranking prioritizes symptom overlap, category consistency, calibrated confidence, triage level, and red-flag safety rules.
