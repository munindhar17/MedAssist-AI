doctor_map = {

    "heart attack":"Cardiologist",
    "hypertension":"Cardiologist",
    "bronchial asthma":"Pulmonologist",
    "pneumonia":"Pulmonologist",
    "tuberculosis":"Pulmonologist",

    "gerd":"Gastroenterologist",
    "peptic ulcer diseae":"Gastroenterologist",
    "gastroenteritis":"Gastroenterologist",
    "alcoholic hepatitis":"Gastroenterologist",
    "chronic cholestasis":"Gastroenterologist",
    "hepatitis a":"Gastroenterologist",
    "hepatitis b":"Gastroenterologist",
    "hepatitis c":"Gastroenterologist",
    "hepatitis d":"Gastroenterologist",
    "hepatitis e":"Gastroenterologist",
    "jaundice":"Gastroenterologist",
    "typhoid":"Gastroenterologist",

    "diabetes":"Endocrinologist",
    "hypothyroidism":"Endocrinologist",
    "hyperthyroidism":"Endocrinologist",
    "hypoglycemia":"Endocrinologist",
    "hormonal imbalance":"Endocrinologist",

    "migraine":"Neurologist",
    "paralysis (brain hemorrhage)":"Neurologist",
    "(vertigo) paroymsal  positional vertigo":"Neurologist",

    "fungal infection":"Dermatologist",
    "acne":"Dermatologist",
    "psoriasis":"Dermatologist",
    "impetigo":"Dermatologist",
    "chicken pox":"Dermatologist",
    "drug reaction":"Dermatologist",

    "allergy":"Allergist",

    "arthritis":"Orthopedic",
    "osteoarthristis":"Orthopedic",
    "osteoarthritis":"Orthopedic",
    "cervical spondylosis":"Orthopedic",
    "varicose veins":"Vascular Specialist",

    "urinary tract infection":"Urologist",
    "uti":"Urologist",
    "pcos":"Gynecologist",
    "polycystic ovary syndrome":"Gynecologist"

}

def get_doctor(disease):

    disease = disease.strip().lower()

    return doctor_map.get(

        disease,

        "General Physician"

    )
