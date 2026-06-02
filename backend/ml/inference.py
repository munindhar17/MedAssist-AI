import joblib
import os
import pandas as pd
from pathlib import Path
from rapidfuzz import fuzz

from backend.data.disease_details import get_disease_details
from backend.data.symptom_aliases import symptom_aliases


base_dir = Path(__file__).resolve().parent.parent.parent


model = joblib.load(
    base_dir / "models" / "disease_model.pkl"
)

encoder = joblib.load(
    base_dir / "models" / "disease_encoder.pkl"
)

symptom_columns = joblib.load(
    base_dir / "models" / "symptom_columns.pkl"
)


DEBUG_PREDICTIONS = os.getenv("DEBUG_PREDICTIONS", "True").lower() == "true"

CONFIDENCE_THRESHOLD = 0.25
MAX_PREDICTIONS = 3
PREDICTION_VERSION = "v3"

FEMALE_ONLY_SYMPTOMS = {
    "abnormal_menstruation",
    "irregular_periods"
}

FEMALE_RELEVANT_DISEASES = {
    "pcos",
    "polycystic ovary syndrome",
    "hypothyroidism",
    "hyperthyroidism",
    "hormonal imbalance"
}

DISEASE_RISK_LEVELS = {
    "heart attack": 3,
    "paralysis (brain hemorrhage)": 3,
    "pneumonia": 3,
    "tuberculosis": 3,
    "hepatitis a": 2,
    "hepatitis b": 2,
    "hepatitis c": 2,
    "hepatitis d": 2,
    "hepatitis e": 2,
    "jaundice": 2,
    "malaria": 2,
    "dengue": 2,
    "typhoid": 2,
    "urinary tract infection": 2,
    "diabetes": 2,
    "hypoglycemia": 2,
    "hyperthyroidism": 2,
    "hypothyroidism": 2,
}

DISEASE_RISK_DATABASE = {
    "heart attack": "high",
    "stroke": "high",
    "paralysis (brain hemorrhage)": "high",
    "pneumonia": "high",
    "tuberculosis": "high",
    "urinary tract infection": "medium",
    "uti": "medium",
    "diabetes": "medium",
    "hypothyroidism": "medium",
    "hyperthyroidism": "medium",
    "acne": "low",
    "osteoarthristis": "low",
    "osteoarthritis": "low",
    "arthritis": "low",
}


def clean_text(value):
    return (
        str(value)
        .lower()
        .replace("_", " ")
        .replace("-", " ")
        .strip()
    )


def canonical_disease_name(disease):
    disease_key = clean_text(disease)
    if disease_key == "osteoarthristis":
        return "Osteoarthritis"
    if disease_key == "urinary tract infection":
        return "UTI"
    return str(disease).strip()


def normalize_symptom(value):
    symptom = clean_text(value)
    symptom = symptom_aliases.get(symptom, symptom)

    return clean_text(symptom).replace(" ", "_")

SYMPTOM_CATEGORIES = {
    "cardiology": {
        "chest pain",
        "breathlessness",
        "fast heart rate",
        "sweating",
        "palpitations",
        "chest discomfort"
    },
    "endocrine": {
        "mood swings",
        "abnormal menstruation",
        "increased appetite",
        "excessive hunger",
        "fatigue",
        "weight gain",
        "weight loss",
        "anxiety",
        "irregular periods",
        "cold intolerance",
        "enlarged thyroid",
        "brittle nails",
        "lethargy",
        "irritability",
        "restlessness",
        "depression",
        "cold hands and feets",
        "puffy face and eyes",
        "swollen extremeties"
    },
    "gynecology": {
        "abnormal menstruation",
        "irregular periods",
        "mood swings"
    },
    "gastro": {
        "stomach pain",
        "abdominal pain",
        "acidity",
        "vomiting",
        "indigestion",
        "bloating",
        "heartburn",
        "nausea",
        "diarrhea",
        "diarrhoea",
        "dark urine",
        "jaundice",
        "yellow skin"
    },
    "urology": {
        "burning micturition",
        "continuous feel of urine",
        "bladder discomfort",
        "foul smell of urine",
        "foul smell of urine",
        "urinary urgency",
        "cloudy urine",
        "painful urination",
        "polyuria"
    },
    "respiratory": {
        "cough",
        "congestion",
        "breathlessness",
        "phlegm",
        "wheezing",
        "shortness of breath",
        "sore throat",
        "high fever"
    },
    "dermatology": {
        "blackheads",
        "pimples",
        "skin rash",
        "pus filled pimples",
        "blister",
        "itching",
        "red bumps",
        "dry skin",
        "scurring",
        "nodal skin eruptions",
        "dischromic patches",
        "red sores",
        "flaking",
        "crusting"
    },
    "neurology": {
        "headache",
        "dizziness",
        "loss of balance",
        "altered sensorium",
        "confusion",
        "blurred vision",
        "blurred and distorted vision",
        "weakness of one body side",
        "difficulty speaking",
        "unsteady movement",
        "spinning sensation"
    },
    "orthopedic": {
        "joint pain",
        "hip joint pain",
        "knee pain",
        "neck pain",
        "back pain",
        "stiffness",
        "swelling joints",
        "swelling",
        "painful walking",
        "muscle weakness"
    }
}

NORMALIZED_SYMPTOM_CATEGORIES = {
    category: {normalize_symptom(symptom) for symptom in symptoms}
    for category, symptoms in SYMPTOM_CATEGORIES.items()
}

SYMPTOM_CATEGORY_MAP = {
    normalize_symptom(symptom): category.lower()
    for category, symptoms in SYMPTOM_CATEGORIES.items()
    for symptom in symptoms
}

DISEASE_CATEGORIES = {
    "(vertigo) paroymsal  positional vertigo": "neurology",
    "aids": "endocrine",
    "acne": "dermatology",
    "alcoholic hepatitis": "gastro",
    "allergy": "respiratory",
    "arthritis": "orthopedic",
    "bronchial asthma": "respiratory",
    "cervical spondylosis": "orthopedic",
    "chicken pox": "dermatology",
    "chronic cholestasis": "gastro",
    "common cold": "respiratory",
    "dengue": "gastro",
    "diabetes": "endocrine",
    "dimorphic hemmorhoids(piles)": "gastro",
    "drug reaction": "dermatology",
    "fungal infection": "dermatology",
    "gastroenteritis": "gastro",
    "gerd": "gastro",
    "heart attack": "cardiology",
    "hepatitis a": "gastro",
    "hepatitis b": "gastro",
    "hepatitis c": "gastro",
    "hepatitis d": "gastro",
    "hepatitis e": "gastro",
    "hypertension": "cardiology",
    "hyperthyroidism": "endocrine",
    "hypoglycemia": "endocrine",
    "hypothyroidism": "endocrine",
    "impetigo": "dermatology",
    "jaundice": "gastro",
    "malaria": "gastro",
    "migraine": "neurology",
    "osteoarthristis": "orthopedic",
    "osteoarthritis": "orthopedic",
    "paralysis (brain hemorrhage)": "neurology",
    "peptic ulcer diseae": "gastro",
    "pneumonia": "respiratory",
    "psoriasis": "dermatology",
    "tuberculosis": "respiratory",
    "typhoid": "gastro",
    "urinary tract infection": "urology",
    "varicose veins": "cardiology",
    "pcos": "gynecology",
    "polycystic ovary syndrome": "gynecology",
}

RULE_BASED_DISEASE_SYMPTOMS = {
    "PCOS": {
        "abnormal_menstruation",
        "irregular_periods",
        "mood_swings",
        "weight_gain",
        "fatigue",
        "excessive_hunger"
    }
}

CRITICAL_SYMPTOMS = {
    "chest_pain",
    "breathlessness",
    "fast_heart_rate",
    "sweating",
    "altered_sensorium",
    "weakness_of_one_body_side",
    "loss_of_balance",
    "high_fever",
    "blood_in_sputum",
}

DISEASE_CRITICAL_SYMPTOMS = {
    "heart attack": {
        "chest_pain",
        "breathlessness",
        "sweating",
        "fast_heart_rate"
    },
    "pneumonia": {
        "cough",
        "high_fever",
        "breathlessness",
        "phlegm"
    },
    "tuberculosis": {
        "cough",
        "blood_in_sputum",
        "night_sweats",
        "weight_loss"
    },
    "urinary tract infection": {
        "burning_micturition",
        "bladder_discomfort"
    }
}


def load_dataset_disease_symptoms():
    dataset_path = base_dir / "datasets" / "symptom_dataset" / "dataset.csv"
    disease_symptoms = {}

    if not dataset_path.exists():
        return disease_symptoms

    dataset = pd.read_csv(dataset_path)
    symptom_columns_from_dataset = [
        column for column in dataset.columns
        if column.lower() != "disease"
    ]

    for _, row in dataset.iterrows():
        disease = str(row.get("Disease", "")).strip()
        if not disease:
            continue

        key = clean_text(disease)
        disease_symptoms.setdefault(key, set())

        for column in symptom_columns_from_dataset:
            value = row.get(column)
            if pd.isna(value):
                continue

            symptom = str(value).strip()
            if symptom:
                disease_symptoms[key].add(normalize_symptom(symptom))

    return disease_symptoms


DATASET_DISEASE_SYMPTOMS = load_dataset_disease_symptoms()


def get_symptom_category(symptom):
    normalized = normalize_symptom(symptom)
    return SYMPTOM_CATEGORY_MAP.get(normalized)


def get_symptom_categories(symptoms):
    if not symptoms:
        return set()

    categories = set()
    for symptom in symptoms:
        normalized = normalize_symptom(symptom)
        for category, category_symptoms in NORMALIZED_SYMPTOM_CATEGORIES.items():
            if normalized in category_symptoms:
                categories.add(category)

        category = SYMPTOM_CATEGORY_MAP.get(normalized)
        if category and category not in categories:
            categories.add(category)

    return categories


def is_same_category(symptom, disease_symptom):
    category_a = get_symptom_category(symptom)
    category_b = get_symptom_category(disease_symptom)
    return category_a is None or category_b is None or category_a == category_b


def is_related_symptom(symptom, disease_symptom):
    current = normalize_symptom(symptom)
    target = normalize_symptom(disease_symptom)

    if current == target:
        return True

    if not is_same_category(current, target):
        return False

    if current in target or target in current:
        return True

    score = max(
        fuzz.ratio(current, target),
        fuzz.partial_ratio(current, target),
        fuzz.token_sort_ratio(current, target)
    )

    return score >= 78


def get_disease_symptoms(disease):
    details = get_disease_details(disease)
    symptoms = details.get("symptoms", [])

    normalized = set(DATASET_DISEASE_SYMPTOMS.get(clean_text(disease), set()))

    for symptom in symptoms:
        if not isinstance(symptom, str):
            continue

        normalized.add(normalize_symptom(symptom))

    return sorted(set(normalized))


def match_symptoms(user_symptoms, disease_symptoms, strong=False):
    matched = []
    matcher = is_related_symptom

    if strong:
        def strong_match(symptom, disease_symptom):
            current = normalize_symptom(symptom)
            target = normalize_symptom(disease_symptom)

            if current == target:
                return True

            if not is_same_category(current, target):
                return False

            score = max(
                fuzz.ratio(current, target),
                fuzz.partial_ratio(current, target),
                fuzz.token_sort_ratio(current, target)
            )

            return score >= 85

        matcher = strong_match

    for symptom in user_symptoms:
        for disease_symptom in disease_symptoms:
            if matcher(symptom, disease_symptom):
                matched.append(symptom)
                break

    return sorted(set(matched))


def audit_symptom_utilization(user_symptoms, disease_symptoms):
    audit = []

    for symptom in user_symptoms:
        normalized = normalize_symptom(symptom)
        exact_match = normalized in disease_symptoms
        partial_match = False

        if not exact_match:
            partial_match = any(
                is_related_symptom(normalized, disease_symptom)
                for disease_symptom in disease_symptoms
            )

        if exact_match:
            status = "matched"
        elif partial_match:
            status = "partially matched"
        else:
            status = "ignored"

        audit.append({
            "symptom": normalized,
            "status": status
        })

    return audit


def get_disease_category(disease, disease_symptoms):
    disease_key = clean_text(disease)
    if disease_key in DISEASE_CATEGORIES:
        return DISEASE_CATEGORIES[disease_key]

    symptom_categories = get_symptom_categories(disease_symptoms)
    if symptom_categories:
        return max(symptom_categories, key=lambda item: len([
            symptom for symptom in disease_symptoms
            if get_symptom_category(symptom) == item
        ]))

    return None


def calculate_symptom_match_score(user_symptoms, matched_symptoms, strong_matched_symptoms):
    if not user_symptoms:
        return 0.0

    user_count = len(set(user_symptoms))
    strong_ratio = len(strong_matched_symptoms) / user_count
    matched_ratio = len(matched_symptoms) / user_count

    return min(1.0, strong_ratio * 0.8 + matched_ratio * 0.2)


def calculate_category_consistency(user_categories, disease_category):
    if not user_categories or not disease_category:
        return 0.0

    return 1.0 if disease_category in user_categories else 0.0


def is_female_relevant_disease(disease, disease_category):
    disease_key = clean_text(disease)
    return (
        disease_key in FEMALE_RELEVANT_DISEASES or
        disease_category in {"gynecology", "endocrine"}
    )


def get_risk_level_weight(disease):
    risk = DISEASE_RISK_DATABASE.get(clean_text(disease))
    if risk == "high":
        return 3
    if risk == "medium":
        return 2
    return DISEASE_RISK_LEVELS.get(clean_text(disease), 1)


def get_disease_risk(disease):
    return DISEASE_RISK_DATABASE.get(clean_text(disease), "low")


def calculate_clinical_priority(disease, cleaned_symptoms, disease_category):
    disease_key = clean_text(disease)
    symptom_set = set(cleaned_symptoms)
    priority = 0.0

    if disease_key == "heart attack" and {"chest_pain", "breathlessness"} <= symptom_set:
        priority += 0.3

    if disease_category == "cardiology" and "chest_pain" in symptom_set:
        priority += 0.1

    if disease_key == "urinary tract infection" and {
        "burning_micturition",
        "bladder_discomfort"
    } <= symptom_set:
        priority += 0.2

    if disease_key == "osteoarthristis" and {"hip_joint_pain", "knee_pain"} <= symptom_set:
        priority += 0.2

    return priority


def has_all_critical_symptoms(disease, cleaned_symptoms):
    critical_symptoms = DISEASE_CRITICAL_SYMPTOMS.get(clean_text(disease), set())
    if not critical_symptoms:
        return False

    return critical_symptoms <= set(cleaned_symptoms)


def confidence_label_for(confidence):
    if confidence < 40:
        return "Low confidence prediction"
    if confidence < 70:
        return "Moderate confidence prediction"
    return "High confidence prediction"


def calibrate_confidence(candidate, rank_index):
    confidence = (
        28.0 +
        candidate["symptom_match_score"] * 38.0 +
        candidate["category_consistency"] * 10.0 +
        min(candidate["ml_probability"], 0.25) * 12.0 +
        min(candidate["clinical_priority"], 0.3) * 12.0
    )

    if candidate["symptom_match_score"] >= 0.95:
        confidence = max(confidence, 70.0)
    elif candidate["symptom_match_score"] >= 0.55:
        confidence = max(confidence, 50.0)
    else:
        confidence = max(confidence, 30.0)

    confidence *= 0.92 ** rank_index

    if candidate["all_critical_symptoms_present"]:
        confidence = min(confidence, 98.0)
    else:
        confidence = min(confidence, 88.0)

    if rank_index > 0:
        confidence = min(confidence, 54.0)
    if rank_index > 1:
        confidence = min(confidence, 31.0)

    return round(max(0.0, confidence), 1)


def predict_disease(user_symptoms, invalid_count=0, gender=None):
    input_data = dict.fromkeys(symptom_columns, 0)

    cleaned_symptoms = []
    for symptom in user_symptoms:
        symptom_text = str(symptom).strip()
        if not symptom_text:
            continue

        cleaned_symptoms.append(normalize_symptom(symptom_text))

    cleaned_symptoms = list(dict.fromkeys(cleaned_symptoms))

    gender_value = clean_text(gender or "")
    if gender_value == "male":
        cleaned_symptoms = [
            symptom for symptom in cleaned_symptoms
            if symptom not in FEMALE_ONLY_SYMPTOMS
        ]

    for symptom in cleaned_symptoms:
        if symptom in input_data:
            input_data[symptom] = 1

    active = [key for key, value in input_data.items() if value == 1]

    if DEBUG_PREDICTIONS:
        print("Received:", cleaned_symptoms)
        print("Matched:", active)

    input_df = pd.DataFrame([input_data])
    probabilities = model.predict_proba(input_df)[0]
    classes = model.classes_

    candidates = []

    for index, probability in enumerate(probabilities):
        disease_label = classes[index]
        disease = encoder.inverse_transform([disease_label])[0]
        disease = str(disease).strip()

        disease_symptoms = get_disease_symptoms(disease)
        matched_symptoms = match_symptoms(cleaned_symptoms, disease_symptoms)
        strong_matched_symptoms = match_symptoms(cleaned_symptoms, disease_symptoms, strong=True)

        if len(strong_matched_symptoms) == 0 and len(matched_symptoms) == 0:
            continue

        symptom_match_score = calculate_symptom_match_score(
            cleaned_symptoms,
            matched_symptoms,
            strong_matched_symptoms
        )

        user_categories = get_symptom_categories(cleaned_symptoms)
        disease_category = get_disease_category(disease, disease_symptoms)
        category_consistency = calculate_category_consistency(
            user_categories,
            disease_category
        )
        clinical_priority = calculate_clinical_priority(
            disease,
            cleaned_symptoms,
            disease_category
        )

        ml_probability = float(probability)
        final_score = (
            ml_probability * 0.10 +
            symptom_match_score * 0.70 +
            category_consistency * 0.20
        )

        exact_match_bonus = len(strong_matched_symptoms) * 0.15
        final_score += exact_match_bonus

        if (
            gender_value == "female" and
            user_categories & {"gynecology", "endocrine"} and
            is_female_relevant_disease(disease, disease_category)
        ):
            final_score += 0.12

        if category_consistency > 0:
            final_score *= 1.7

        if user_categories and disease_category and disease_category not in user_categories:
            final_score *= 0.35

        if len(matched_symptoms) == 1 and len(cleaned_symptoms) >= 3:
            final_score *= 0.7

        contradiction_penalty = 0.25 if len(user_categories) >= 4 else 0.0
        penalty = min(0.18, invalid_count * 0.06) if invalid_count > 0 else 0.0
        final_score = min(1.0, max(0.0, final_score - penalty - contradiction_penalty))
        confidence = round(final_score * 100, 1)

        if confidence < 40:
            confidence_label = "Low confidence prediction"
        elif confidence < 70:
            confidence_label = "Moderate confidence prediction"
        else:
            confidence_label = "High confidence prediction"

        if DEBUG_PREDICTIONS:
            print(
                "Prediction debug:",
                {
                    "Disease": disease,
                    "ML Probability": round(ml_probability, 4),
                    "Matched Symptoms": matched_symptoms,
                    "Strong Matches": strong_matched_symptoms,
                    "Category Score": round(category_consistency, 4),
                    "Final Score": round(final_score, 4),
                    "Raw Score Percent": confidence
                }
            )

        candidates.append({
            "disease": canonical_disease_name(disease),
            "model_disease": disease,
            "ml_probability": ml_probability,
            "symptom_match_score": symptom_match_score,
            "category_consistency": category_consistency,
            "category_consistency_score": category_consistency,
            "disease_category": disease_category,
            "final_score": final_score,
            "exact_match_bonus": exact_match_bonus,
            "clinical_priority": clinical_priority,
            "invalid_symptom_penalty": penalty,
            "contradiction_penalty": contradiction_penalty,
            "matched_symptoms": strong_matched_symptoms,
            "all_matched_symptoms": matched_symptoms,
            "symptom_utilization": audit_symptom_utilization(
                cleaned_symptoms,
                disease_symptoms
            ),
            "disease_symptom_count": len(disease_symptoms),
            "risk_level_weight": get_risk_level_weight(disease),
            "disease_risk": get_disease_risk(disease),
            "matched_critical_symptoms": sorted(
                set(strong_matched_symptoms) & CRITICAL_SYMPTOMS
            ),
            "all_critical_symptoms_present": has_all_critical_symptoms(
                disease,
                cleaned_symptoms
            ),
            "confidence_score": confidence,
            "confidence": f"{confidence}%",
            "confidence_label": confidence_label
        })

    if gender_value != "male":
        pcos_symptoms = RULE_BASED_DISEASE_SYMPTOMS["PCOS"]
        pcos_matches = sorted(set(cleaned_symptoms) & pcos_symptoms)
        if len(pcos_matches) >= 2 and any(
            symptom in pcos_matches
            for symptom in FEMALE_ONLY_SYMPTOMS
        ):
            symptom_match_score = len(pcos_matches) / max(1, len(cleaned_symptoms))
            category_consistency = 1.0
            final_score = min(
                1.0,
                symptom_match_score * 0.70 +
                category_consistency * 0.20 +
                len(pcos_matches) * 0.15 +
                0.12
            )

            candidates.append({
                "disease": "PCOS",
                "model_disease": "PCOS",
                "ml_probability": 0.0,
                "symptom_match_score": symptom_match_score,
                "category_consistency": category_consistency,
                "category_consistency_score": category_consistency,
                "disease_category": "gynecology",
                "final_score": final_score,
                "exact_match_bonus": len(pcos_matches) * 0.15,
                "clinical_priority": 0.12,
                "invalid_symptom_penalty": 0.0,
                "contradiction_penalty": 0.0,
                "matched_symptoms": pcos_matches,
                "all_matched_symptoms": pcos_matches,
                "symptom_utilization": audit_symptom_utilization(
                    cleaned_symptoms,
                    pcos_symptoms
                ),
                "disease_symptom_count": len(pcos_symptoms),
                "risk_level_weight": 2,
                "disease_risk": "medium",
                "matched_critical_symptoms": [],
                "all_critical_symptoms_present": False,
                "confidence_score": 0.0,
                "confidence": "0.0%",
                "confidence_label": "Low confidence prediction"
            })

    ranked = [
        item for item in sorted(
            candidates,
            key=lambda item: (
                item["final_score"],
                item["clinical_priority"],
                item["ml_probability"]
            ),
            reverse=True
        )
        if item["final_score"] >= CONFIDENCE_THRESHOLD
    ]

    filtered = ranked[:MAX_PREDICTIONS]

    for rank_index, item in enumerate(filtered):
        confidence = calibrate_confidence(item, rank_index)
        item["confidence_score"] = confidence
        item["confidence"] = f"{confidence}%"
        item["confidence_label"] = confidence_label_for(confidence)

        if DEBUG_PREDICTIONS:
            print(
                "Calibrated prediction:",
                {
                    "Disease": item["disease"],
                    "ML Probability": round(item["ml_probability"], 4),
                    "Matched Symptoms": item["all_matched_symptoms"],
                    "Strong Matches": item["matched_symptoms"],
                    "Category Score": round(item["category_consistency"], 4),
                    "Final Score": round(item["final_score"], 4),
                    "Confidence": confidence
                }
            )

    return filtered
