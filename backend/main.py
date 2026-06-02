
from backend.data.disease_details import get_disease_details
from backend.data.symptom_aliases import symptom_aliases
from pydantic import BaseModel
from fastapi import FastAPI
from typing import Optional
import os
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from rapidfuzz import fuzz, process


from backend.ml.inference import (
    predict_disease,
    symptom_columns,
    get_disease_symptoms,
    PREDICTION_VERSION
)

from backend.utils.data_loader import (
    get_description,
    get_precautions,
    calculate_risk
)

from backend.utils.db import (
    save_prediction,
    get_history,
    get_all_history
)

from backend.utils.doctor_recommendation import (
    get_doctor
)

from backend.utils.report_generator import (
    generate_report
)

from backend.utils.emergency_checker import (
    check_emergency
)

app = FastAPI()

SYMPTOM_CATEGORIES = {
    "CARDIAC": {
        "chest_pain",
        "breathlessness",
        "fast_heart_rate",
        "sweating",
        "palpitations",
        "chest_discomfort"
    },
    "HORMONAL": {
        "mood_swings",
        "abnormal_menstruation",
        "increased_appetite",
        "fatigue",
        "weight_gain",
        "anxiety",
        "irregular_periods",
        "cold_intolerance"
    },
    "DIGESTIVE": {
        "stomach_pain",
        "acidity",
        "vomiting",
        "indigestion",
        "bloating",
        "heartburn",
        "nausea",
        "diarrhea"
    },
    "URINARY": {
        "burning_micturition",
        "continuous_feel_of_urine",
        "bladder_discomfort",
        "foul_smell_of_urine",
        "urinary_urgency",
        "cloudy_urine",
        "painful_urination"
    },
    "RESPIRATORY": {
        "cough",
        "congestion",
        "breathlessness",
        "phlegm",
        "wheezing",
        "shortness_of_breath",
        "sore_throat",
        "high_fever"
    },
    "SKIN": {
        "blackheads",
        "pimples",
        "skin_rash",
        "pus_filled_pimples",
        "blister",
        "itching",
        "red_bumps",
        "dry_skin"
    },
    "NEUROLOGICAL": {
        "headache",
        "dizziness",
        "loss_of_balance",
        "altered_sensorium",
        "confusion",
        "blurred_and_distorted_vision",
        "weakness_of_one_body_side",
        "numbness"
    }
}

FEMALE_ONLY_SYMPTOMS = {
    "abnormal_menstruation",
    "irregular_periods"
}

latest_report_data = {}

RED_FLAG_SYMPTOMS = {
    "chest_pain",
    "breathlessness",
    "loss_of_consciousness",
    "slurred_speech",
    "blood_in_sputum"
}

DISEASE_RISK_LEVELS = {
    "heart attack": "high",
    "stroke": "high",
    "paralysis (brain hemorrhage)": "high",
    "urinary tract infection": "medium",
    "uti": "medium",
    "acne": "low",
    "osteoarthristis": "low",
    "osteoarthritis": "low",
    "hypothyroidism": "medium",
    "hyperthyroidism": "medium",
    "pcos": "medium",
}

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://med-assist-ai-fawn.vercel.app"
]

extra_origins = [
    origin.strip()
    for origin in os.getenv("ALLOWED_ORIGINS", "").split(",")
    if origin.strip()
]

origins.extend(extra_origins)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):

    question:str

class Profile(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    conditions: Optional[list[str]] = None
    allergies: Optional[list[str]] = None

class SymptomInput(BaseModel):
    symptoms: list[str]
    profile: Optional[Profile] = None


DISEASE_SYMPTOM_HINTS = {
    "heart attack": ["chest pain", "breathlessness", "sweating", "fast heart rate"],
    "hypertension": ["chest pain", "headache", "dizziness"],
    "acne": ["blackheads", "pimples", "skin rash", "pus filled pimples", "oily skin"],
    "osteoarthristis": ["hip joint pain", "knee pain", "joint pain", "swelling joints", "painful walking"],
    "osteoarthritis": ["hip joint pain", "knee pain", "joint pain", "swelling joints", "painful walking"],
    "arthritis": ["joint pain", "stiffness", "swelling joints", "painful walking"],
    "urinary tract infection": [
        "burning micturition",
        "continuous feel of urine",
        "bladder discomfort",
        "foul smell of urine"
    ],
    "uti": [
        "burning micturition",
        "continuous feel of urine",
        "bladder discomfort",
        "foul smell of urine"
    ],
    "diabetes": ["polyuria", "increased appetite", "fatigue", "weight loss"],
    "gerd": ["stomach pain", "acidity", "chest pain"],
    "peptic ulcer diseae": ["stomach pain", "indigestion", "vomiting"],
    "migraine": ["headache", "nausea", "blurred and distorted vision"],
    "bronchial asthma": ["breathlessness", "cough", "wheezing"],
    "pneumonia": ["cough", "breathlessness", "high fever", "phlegm"],
    "hypothyroidism": ["abnormal menstruation", "mood swings", "weight gain", "fatigue", "cold intolerance"],
    "hyperthyroidism": ["abnormal menstruation", "mood swings", "weight loss", "fast heart rate", "sweating"],
}

DISEASE_SUGGESTION_PRIORITIES = {
    "acne": ["pimples", "oily skin", "pus filled pimples", "skin rash"],
    "heart attack": ["breathlessness", "sweating", "fast heart rate", "chest pain"],
    "hypertension": ["headache", "dizziness", "chest pain"],
    "urinary tract infection": ["burning micturition", "bladder discomfort", "urinary urgency"],
    "uti": ["burning micturition", "bladder discomfort", "urinary urgency"],
    "osteoarthristis": ["hip_joint_pain", "knee_pain", "joint_pain", "swelling_joints", "painful_walking"],
    "osteoarthritis": ["hip_joint_pain", "knee_pain", "joint_pain", "swelling_joints", "painful_walking"],
    "diabetes": ["polyuria", "fatigue", "increased appetite"],
    "migraine": ["headache", "nausea", "light sensitivity"],
    "hypothyroidism": ["fatigue", "weight_gain", "cold_intolerance", "lethargy", "brittle_nails"],
    "hyperthyroidism": ["fast_heart_rate", "weight_loss", "sweating", "restlessness", "muscle_weakness"],
}

DANGEROUS_SYMPTOMS = {
    "chest pain",
    "breathlessness",
    "fast heart rate",
    "sweating",
    "loss of balance",
    "weakness of one body side",
    "altered sensorium",
    "high fever"
}

PROFILE_RISK_CONDITIONS = {
    "diabetes",
    "hypertension",
    "heart disease",
    "asthma",
    "kidney disease",
    "stroke"
}


def clean_text(value):

    return (
        str(value)
        .lower()
        .replace("_", " ")
        .replace("-", " ")
        .strip()
    )


def normalize_symptom(value):

    symptom = clean_text(value)

    symptom = symptom_aliases.get(
        symptom,
        symptom
    )

    return clean_text(symptom).replace(" ", "_")


def is_related_symptom(symptom, disease_symptom):

    current = normalize_symptom(symptom)
    target = normalize_symptom(disease_symptom)

    if current == target:
        return True

    if current in target or target in current:
        return True

    score = max(
        fuzz.ratio(current, target),
        fuzz.partial_ratio(current, target),
        fuzz.token_sort_ratio(current, target)
    )

    return score >= 72


def get_symptom_categories(symptoms):
    categories = set()
    for symptom in symptoms:
        normalized = normalize_symptom(symptom)
        for category, category_symptoms in SYMPTOM_CATEGORIES.items():
            if normalized in category_symptoms:
                categories.add(category)
                break
    return categories


def get_symptom_category(symptom):
    normalized = normalize_symptom(symptom)
    for category, category_symptoms in SYMPTOM_CATEGORIES.items():
        if normalized in category_symptoms:
            return category
    return None


def get_disease_category(symptoms):
    categories = [get_symptom_category(symptom) for symptom in symptoms]
    categories = [category for category in categories if category]
    if not categories:
        return None
    return max(set(categories), key=categories.count)


CATEGORY_SUGGESTIONS = {
    "CARDIAC": ["fatigue", "sweating", "palpitations", "chest_discomfort"],
    "HORMONAL": ["fatigue", "weight_gain", "anxiety", "irregular_periods"],
    "DIGESTIVE": ["nausea", "bloating", "heartburn", "indigestion"],
    "RESPIRATORY": ["cough", "wheezing", "phlegm", "sore_throat"],
    "URINARY": ["burning_micturition", "urinary_urgency", "cloudy_urine", "bladder_discomfort"],
    "SKIN": ["itching", "red_bumps", "dry_skin", "blister"],
    "NEUROLOGICAL": ["dizziness", "confusion", "blurred_and_distorted_vision", "loss_of_balance"]
}


def suggest_symptoms_for_disease(disease, current_symptoms, matched_symptoms):
    disease_symptoms = list(get_disease_symptoms(disease))

    disease_symptoms.extend(
        normalize_symptom(s)
        for s in DISEASE_SYMPTOM_HINTS.get(clean_text(disease), [])
        if isinstance(s, str)
    )

    disease_priority = DISEASE_SUGGESTION_PRIORITIES.get(clean_text(disease), [])
    candidates = []

    if disease_priority:
        candidates.extend([normalize_symptom(item) for item in disease_priority])

    candidates.extend(disease_symptoms)

    suggestions = []
    for item in candidates:
        normalized_item = normalize_symptom(item)
        if (
            normalized_item not in current_symptoms and
            normalized_item not in matched_symptoms and
            normalized_item not in suggestions and
            normalized_item
        ):
            suggestions.append(normalized_item)
        if len(suggestions) >= 5:
            break

    return suggestions


def get_disease_risk_level(disease):
    return DISEASE_RISK_LEVELS.get(clean_text(disease), "low")


def get_triage_level(disease, symptoms, severity_score):
    disease_key = clean_text(disease)
    symptom_set = set(symptoms)

    if disease_key in {"heart attack", "stroke", "paralysis (brain hemorrhage)"}:
        return "Emergency"

    if symptom_set & RED_FLAG_SYMPTOMS:
        return "Emergency" if {"chest_pain", "breathlessness"} <= symptom_set else "Urgent"

    if severity_score >= 26:
        return "Urgent"

    if disease_key in {"urinary tract infection", "uti"}:
        return "Routine"

    if disease_key == "acne":
        return "Monitor"

    if severity_score >= 11:
        return "Routine"

    return "Monitor"


def get_ignored_symptoms(symptom_utilization):
    return [
        item["symptom"]
        for item in symptom_utilization
        if item.get("status") == "ignored"
    ]


def build_prediction_reason(matched_symptoms, ignored_symptoms, suggested_symptoms):
    parts = []

    if matched_symptoms:
        parts.append(
            "Matched symptoms: " +
            ", ".join(matched_symptoms)
        )

    if ignored_symptoms:
        parts.append(
            "Ignored symptoms: " +
            ", ".join(ignored_symptoms)
        )

    if suggested_symptoms:
        parts.append(
            "Common missing symptoms: " +
            ", ".join(suggested_symptoms[:3])
        )
        parts.append(
            "Confidence reduced because some major symptoms are absent."
        )

    if not parts:
        return "No strong symptom overlap was found."

    return " ".join(parts)


def calculate_new_severity(symptoms, top_prediction, profile_risk_factor=0):
    if not top_prediction:
        return 5, "Low"

    symptom_count = len(symptoms)
    disease_risk_level = int(top_prediction.get("risk_level_weight", 1))
    critical_count = len(top_prediction.get("matched_critical_symptoms", []))
    matched_count = len(top_prediction.get("matched_symptoms", []))

    severity_score = (
        symptom_count * 2 +
        matched_count * 1 +
        disease_risk_level * 4 +
        critical_count * 4 +
        profile_risk_factor * 2
    )

    severity_score = min(40, max(0, int(severity_score)))

    if severity_score <= 10:
        risk_level = "Low"
    elif severity_score <= 25:
        risk_level = "Medium"
    else:
        risk_level = "High"

    return severity_score, risk_level


def calculate_symptom_overlap_score(user_symptoms, disease_symptoms):
    normalized_user = [normalize_symptom(s) for s in user_symptoms]
    normalized_disease = [normalize_symptom(s) for s in disease_symptoms]

    score = 0.0
    for user_symptom in normalized_user:
        for disease_symptom in normalized_disease:
            if user_symptom == disease_symptom:
                score += 1.0
            elif user_symptom in disease_symptom or disease_symptom in user_symptom:
                score += 0.7
            else:
                user_cat = get_symptom_categories([user_symptom])
                disease_cat = get_symptom_categories([disease_symptom])
                if user_cat & disease_cat:
                    score += 0.4

    return score


def check_inconsistent_symptoms(symptoms):
    categories = get_symptom_categories(symptoms)
    return len(categories) >= 4


@app.get("/")
def home():

    return {
        "message":"MedAssist AI running"
    }


@app.get("/symptoms")
def symptoms():

    cleaned=[]

    for symptom in symptom_columns:

        symptom=(

            symptom
            .replace(" _","_")
            .replace("_ ","_")
            .replace(" ","_")
            .strip()

        )

        cleaned.append(
            symptom
        )

    return{

        "symptoms":

        sorted(

            list(
                set(cleaned)
            )

        )

    }


@app.post("/predict")
def predict(data: SymptomInput):

    global latest_report_data

    normalized_symptoms = []

    for symptom in data.symptoms:

        normalized_symptoms.append(
            normalize_symptom(symptom)
        )

    normalized_symptoms = list(
        dict.fromkeys(normalized_symptoms)
    )

    invalid_symptoms = []
    valid_symptoms = []

    for symptom in normalized_symptoms:
        if (
            data.profile and
            data.profile.gender and
            str(data.profile.gender).strip().lower() == "male" and
            symptom in FEMALE_ONLY_SYMPTOMS
        ):
            invalid_symptoms.append(symptom)
        else:
            valid_symptoms.append(symptom)

    normalized_symptoms = list(dict.fromkeys(valid_symptoms))
    suggested_symptoms = []

    profile_applied = False
    health_profile = {}
    age = 0
    conditions = []
    allergies = []

    if data.profile:
        profile_applied = True
        age = data.profile.age or 0
        conditions = data.profile.conditions or []
        allergies = data.profile.allergies or []
        health_profile = {
            "name": data.profile.name,
            "age": age,
            "gender": data.profile.gender,
            "height": data.profile.height,
            "weight": data.profile.weight,
            "conditions": conditions,
            "allergies": allergies
        }

    if check_inconsistent_symptoms(normalized_symptoms):
        has_prediction = False
        prediction_status = "Inconsistent symptoms"
        top_disease = "Insufficient information"
        confidence = 0.0
        predictions = []
        top_prediction = None
        matched_symptoms = []
        matched_count = 0
        severity_score = 5
        risk_level = "Low"
        final_severity_score = severity_score
        final_risk_level = risk_level
        description = "Symptoms belong to too many unrelated body systems. Please review and provide consistent symptoms."
        precautions = ["Review symptom selection", "Consult a healthcare provider for accurate diagnosis"]
        recommended_doctor = "General Physician"
        doctor = recommended_doctor
        details = {}
        prediction_explanation = {
            "matched_symptoms": [],
            "ignored_symptoms": normalized_symptoms,
            "suggested_symptoms": [],
            "symptom_utilization": [
                {"symptom": symptom, "status": "ignored"}
                for symptom in normalized_symptoms
            ],
            "reason": description,
            "invalid_symptoms": invalid_symptoms
        }
    else:
        predictions = predict_disease(
            normalized_symptoms,
            invalid_count=len(invalid_symptoms),
            gender=data.profile.gender if data.profile else None
        )

        if predictions:
            top_prediction = predictions[0]
            top_disease = top_prediction["disease"]
            confidence = float(
                top_prediction.get("confidence_score", 0.0)
            )
        else:
            top_prediction = None
            top_disease = "Insufficient information"
            confidence = 0.0

        details = get_disease_details(top_disease)

        disease_key = clean_text(top_disease)

        disease_symptoms = [
            normalize_symptom(s)
            for s in details.get("symptoms", [])
            if isinstance(s, str)
        ]

        disease_symptoms.extend(
            normalize_symptom(s)
            for s in DISEASE_SYMPTOM_HINTS.get(disease_key, [])
            if isinstance(s, str)
        )

        matched_symptoms = top_prediction["matched_symptoms"] if top_prediction else []
        matched_count = len(matched_symptoms)
        symptom_utilization = (
            top_prediction.get("symptom_utilization", [])
            if top_prediction
            else []
        )
        ignored_symptoms = get_ignored_symptoms(symptom_utilization)

        condition_names = [
            clean_text(condition)
            for condition in conditions
            if condition
        ]

        profile_risk_factor = sum(
            1
            for condition in condition_names
            if any(
                risk_condition in condition
                for risk_condition in PROFILE_RISK_CONDITIONS
            )
        )

        if confidence < 25 or matched_count == 0:
            has_prediction = False
            severity_score = 5
            risk_level = "Low"
        else:
            has_prediction = True
            severity_score, risk_level = calculate_new_severity(
                normalized_symptoms,
                top_prediction,
                profile_risk_factor
            )

        suggested_symptoms = []
        if has_prediction and top_disease != "Insufficient information":
            suggested_symptoms = suggest_symptoms_for_disease(
                top_disease,
                normalized_symptoms,
                matched_symptoms
            )

        prediction_reason = build_prediction_reason(
            matched_symptoms,
            ignored_symptoms,
            suggested_symptoms
        )

        if invalid_symptoms:
            prediction_reason = (
                prediction_reason +
                f" {len(invalid_symptoms)} symptom was excluded because it may not apply to the selected profile."
            )

        final_severity_score = severity_score
        final_risk_level = risk_level

        prediction_explanation = {
            "matched_symptoms": matched_symptoms,
            "ignored_symptoms": ignored_symptoms,
            "suggested_symptoms": suggested_symptoms,
            "symptom_utilization": symptom_utilization,
            "reason": prediction_reason,
            "invalid_symptoms": invalid_symptoms
        }

        if len(data.symptoms) < 2 and confidence < 70:

            prediction_status = (
                "Need more symptoms"
            )

            top_disease = (
                "Insufficient information"
            )

            description = (
                "Please provide at least 2 symptoms "
                "for a more reliable prediction."
            )

            precautions = [

                "Add more symptoms",
                "Observe symptoms",
                "Consult doctor if symptoms worsen"

            ]

            has_prediction = False

        else:

            if confidence >= 70:

                prediction_status = "High confidence prediction"

            elif confidence >= 40:

                prediction_status = "Moderate confidence prediction"

            else:

                if matched_count >= 2:

                    prediction_status = (
                        "Low confidence prediction"
                    )

                else:

                    prediction_status = (
                        "Insufficient information"
                    )

            if matched_count == 0 and confidence < 40:

                description = (
                    "Not enough symptom information. "
                    "Please add more symptoms."
                )

                recommended_doctor = (
                    "General Physician"
                )

            else:

                description = get_description(
                    top_disease
                )
                recommended_doctor = get_doctor(
                    top_disease
                )

            precautions = get_precautions(
                top_disease
            )

        if 'recommended_doctor' not in locals():
            doctor = get_doctor(
                top_disease
            )
        else:
            doctor = recommended_doctor

    emergency_data = check_emergency(
        normalized_symptoms
    )

    red_flag_symptoms = [
        symptom
        for symptom in normalized_symptoms
        if symptom in RED_FLAG_SYMPTOMS
    ]

    triage_level = get_triage_level(
        top_disease,
        normalized_symptoms,
        final_severity_score
    )

    red_flag_warning = (
        "Urgent medical evaluation recommended."
        if red_flag_symptoms
        else ""
    )

    if emergency_data["emergency"]:

        emergency_message = (
            emergency_data["message"]
        )

    elif red_flag_warning:

        emergency_message = red_flag_warning

    elif final_risk_level == "High":

        emergency_message = (
            "Seek immediate medical attention."
        )

    elif final_risk_level == "Medium":

        emergency_message = (
            "Consult doctor if symptoms persist."
        )

    else:

        emergency_message = (
            "Continue monitoring symptoms."
        )


    latest_report_data = {

        "disease": top_disease,

        "confidence": (
            top_prediction["confidence"]
            if top_prediction
            else "0.0%"
        ),

        "risk": final_risk_level,

        "severity": final_severity_score,

        "triage_level": triage_level,

        "matched_symptoms": matched_symptoms,

        "ignored_symptoms": (
            prediction_explanation.get("ignored_symptoms", [])
            if prediction_explanation
            else []
        ),

        "doctor": doctor,

        "emergency":
        emergency_message,

        "prediction_explanation": prediction_explanation
    }

    if has_prediction and confidence >= 25 and matched_count >= 1:
        save_prediction(
            normalized_symptoms,
            top_disease,
            top_prediction["confidence"] if top_prediction else "0.0%",
            final_severity_score,
            final_risk_level,
            PREDICTION_VERSION
        )

    response_body = {

        "prediction_status":
        prediction_status,

        "has_prediction":
        has_prediction,

        "predictions":
        predictions if has_prediction else [],

        "severity_score":
        final_severity_score,

        "risk_level":
        final_risk_level,

        "risk":
        final_risk_level,

        "triage_level":
        triage_level,

        "red_flag_symptoms":
        red_flag_symptoms,

        "red_flag_warning":
        red_flag_warning,

        "description":
        description,

        "precautions":
        precautions,

        "recommended_doctor":
        doctor if has_prediction else "General Physician",

        "doctor_type":
        doctor if has_prediction else "General Physician",

        "emergency_message":
        emergency_message,

        "emergency":
        emergency_data,

        "health_profile_applied":
        profile_applied,

        "health_profile":
        health_profile,

        "prediction_explanation":
        prediction_explanation,

        "suggested_symptoms":
        suggested_symptoms,

        "prediction":
        top_disease,

        "confidence":
        top_prediction["confidence"] if top_prediction else "0.0%",

        "severity":
        final_severity_score,

        "matched_symptoms":
        matched_symptoms,

        "ignored_symptoms":
        prediction_explanation.get("ignored_symptoms", []),

        "disease_details":
        details if has_prediction else {}

    }

    return response_body




@app.get("/history")
def history():

    data = get_history()

    records = []

    for row in data:

        records.append({

"id": row[0],
"symptoms": row[1],
"disease": row[2],
"confidence": row[3],
"severity": row[4],
"risk": row[5],
"time": row[6]

})

    return {

        "history": records

    }


@app.get("/analytics")
def analytics():

    history = get_all_history()

    valid_predictions = [
        row for row in history
        if row[2] != "Insufficient information"
    ]

    total = len(valid_predictions)

    if total == 0:

        return {

            "total_predictions": 0,

            "most_common_disease": "N/A",

            "risk_distribution": {

                "Low": 0,
                "Medium": 0,
                "High": 0

            },

            "severity_trend": []

        }

    diseases = []

    risks = {

        "Low": 0,
        "Medium": 0,
        "High": 0

    }

    for row in valid_predictions:

        disease = row[2]
        risk = row[5]

        diseases.append(
            disease
        )

        if risk in risks:

            risks[risk] += 1

    severity_trend = [
        {
            "time": row[6],
            "severity": row[4]
        }
        for row in reversed(valid_predictions[:10])
    ]

    most_common = max(
        set(diseases),
        key=diseases.count
    )

    return {

        "total_predictions":
        total,

        "most_common_disease":
        most_common,

        "risk_distribution":
        risks,

        "severity_trend":
        severity_trend

    }


@app.get("/download-report")
def download_report():

    global latest_report_data

    if not latest_report_data:

        latest_report_data = {

            "disease":
            "No prediction generated",

            "confidence":
            "N/A",

            "risk":
            "N/A",

            "doctor":
            "N/A",

            "emergency":
            "Generate prediction first"

        }

    pdf = generate_report(
        latest_report_data
    )

    return FileResponse(

        path=pdf,

        filename="medical_report.pdf",

        media_type="application/pdf"

    )


@app.get("/nearby-doctors")
def nearby_doctors(latitude: float, longitude: float, specialty: str):

    doctor_data = {
        "Cardiologist": [
            {
                "name": "Apollo Hospital",
                "specialty": "Cardiologist",
                "distance": "2.1 km"
            },
            {
                "name": "Yashoda Hospital",
                "specialty": "Cardiologist",
                "distance": "3.5 km"
            }
        ],
        "Dermatologist": [
            {
                "name": "Care Hospital",
                "specialty": "Dermatologist",
                "distance": "1.8 km"
            }
        ],
        "Neurologist": [
            {
                "name": "AIG Hospital",
                "specialty": "Neurologist",
                "distance": "4.2 km"
            }
        ],
        "Gastroenterologist": [
            {
                "name": "Asian Institute of Gastroenterology",
                "specialty": "Gastroenterologist",
                "distance": "2.3 km"
            },
            {
                "name": "Gastro Care Clinic",
                "specialty": "Gastroenterologist",
                "distance": "4.1 km"
            }
        ],
        "Pulmonologist": [
            {
                "name": "Lung Care Center",
                "specialty": "Pulmonologist",
                "distance": "3.2 km"
            }
        ],
        "Endocrinologist": [
            {
                "name": "Diabetes Care Hospital",
                "specialty": "Endocrinologist",
                "distance": "2.8 km"
            }
        ],
        "Urologist": [
            {
                "name": "Care Urology Center",
                "specialty": "Urologist",
                "distance": "2.5 km"
            },
            {
                "name": "Apollo Urology Clinic",
                "specialty": "Urologist",
                "distance": "4.0 km"
            }
        ],
        "General Physician": [
            {
                "name": "Sunrise Clinic",
                "specialty": "General Physician",
                "distance": "1.2 km"
            },
            {
                "name": "City Medical Center",
                "specialty": "General Physician",
                "distance": "2.4 km"
            }
        ]
    }

    return doctor_data.get(
        specialty,
        doctor_data["General Physician"]
    )


@app.post("/chat")
async def chat(data: ChatRequest):

    question = data.question.lower()
    disease = latest_report_data.get("disease", "")
    confidence = latest_report_data.get("confidence", "0.0%")
    risk = latest_report_data.get("risk", "N/A")
    doctor = latest_report_data.get("doctor", "a healthcare provider")
    severity = latest_report_data.get("severity", "N/A")
    triage_level = latest_report_data.get("triage_level", "Monitor")
    matched_symptoms = latest_report_data.get("matched_symptoms", [])
    ignored_symptoms = latest_report_data.get("ignored_symptoms", [])
    explanation = latest_report_data.get("prediction_explanation", {})

    def context_reply(intent):
        if not disease or disease == "Insufficient information":
            return {
                "reply": (
                    "I do not have enough information to answer that. "
                    "Please run a prediction and provide your symptoms."
                )
            }

        confidence_value = 0.0
        try:
            confidence_value = float(str(confidence).rstrip("%"))
        except ValueError:
            confidence_value = 0.0

        if confidence_value >= 70:
            confidence_text = "moderate-to-high confidence"
        elif confidence_value >= 40:
            confidence_text = "moderate confidence"
        else:
            confidence_text = "limited confidence"

        matched_text = (
            ", ".join(matched_symptoms)
            if matched_symptoms
            else "the selected symptoms"
        )

        ignored_text = ""
        if ignored_symptoms:
            ignored_text = (
                " Some symptoms were not used strongly in this prediction: " +
                ", ".join(ignored_symptoms) + "."
            )

        caution = (
            "Because cardiac or neurological warning symptoms can become serious quickly, "
            "seek urgent medical care if symptoms worsen, spread to the arm or jaw, "
            "or are accompanied by sweating, dizziness, fainting, or slurred speech."
            if triage_level in {"Emergency", "Urgent"}
            else f"A {doctor} is the right next step if symptoms persist, worsen, or keep returning."
        )

        return {
            "reply": (
                f"Your symptoms match {disease} with {confidence_text}. "
                f"Matched symptoms include {matched_text}. "
                f"Triage level: {triage_level}. Severity score: {severity}. "
                f"Risk level: {risk}.{ignored_text} "
                f"{caution} This tool is informational only."
            )
        }

    if any(phrase in question for phrase in ["should i worry", "worry", "concern", "be worried"]):
        return context_reply("worry")

    if "confidence" in question:
        return context_reply("confidence")

    if "what should i do" in question or "what do i do" in question:
        return context_reply("action")

    if "risk" in question or "danger" in question:
        return context_reply("risk")

    if "doctor" in question or "specialist" in question or "clinic" in question:
        return context_reply("doctor")

    responses = {
        "hypertension":
        "Hypertension can usually be controlled through exercise, reducing salt intake, weight management and medications.",

        "headache":
        "Headaches may improve with hydration, sleep, stress reduction and identifying the cause. Persistent headaches should be checked by a doctor.",

        "dizziness":
        "Dizziness may happen due to dehydration, low blood pressure, stress or other medical conditions.",

        "chest pain":
        "Chest pain can have many causes including muscle strain, acidity or heart-related conditions. Seek immediate care if severe.",

        "heart attack":
        "Heart attacks occur when blood flow to the heart becomes blocked. Immediate medical care is critical. Call emergency services.",

        "fever":
        "Fever usually happens due to infections or inflammation. Rest and hydration are often helpful. Seek medical attention if fever persists.",

        "diabetes":
        "Diabetes is managed through healthy eating, exercise, medications and regular monitoring."
    }

    words = question.split()

    bestMatch=None
    highestScore=0

    for word in words:
        match = process.extractOne(
            word,
            responses.keys()
        )

        if match:
            matchedWord,score,_=match
            if score>highestScore:
                highestScore=score
                bestMatch=matchedWord

    if highestScore>=75:
        return{
            "reply": responses[bestMatch]
        }

    return{
        "reply": "I do not have enough information for that question."
    }
