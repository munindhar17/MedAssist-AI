HIGH_RISK_SYMPTOMS=[

"chest_pain",
"breathlessness",
"fast_heart_rate",
"loss_of_balance",
"loss_of_consciousness",
"slurred_speech",
"unconsciousness",
"blood_in_sputum",
"receiving_unsterile_injections"

]

def check_emergency(symptoms):

    detected=[]

    for symptom in symptoms:

        if symptom in HIGH_RISK_SYMPTOMS:

            detected.append(
                symptom
            )

    if len(detected)>=2:

        return{

            "emergency":True,

            "message":
            "Seek immediate medical attention.",

            "symptoms":
            detected

        }

    return{

        "emergency":False,

        "message":
        "No emergency symptoms detected.",

        "symptoms":
        []

    }
