import pandas as pd
import os
import glob


BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

DATASET_DIR = os.path.join(
    BASE_DIR,
    "datasets",
    "symptom_dataset"
)

DISEASE_ALIASES = {
    "osteoarthritis": "osteoarthristis",
    "uti": "urinary tract infection"
}


def find_file(keyword):

    files = glob.glob(
        os.path.join(
            DATASET_DIR,
            "*.csv"
        )
    )

    for file in files:

        filename = os.path.basename(
            file
        ).lower()

        if keyword.lower() in filename:

            return file

    raise FileNotFoundError(
        f"{keyword} file not found"
    )


description_file = find_file(
    "description"
)

precaution_file = find_file(
    "precaution"
)

severity_file = find_file(
    "severity"
)


description_df = pd.read_csv(
    description_file
)

precaution_df = pd.read_csv(
    precaution_file
)

severity_df = pd.read_csv(
    severity_file
)


severity_dict={}

for _,row in severity_df.iterrows():

    symptom = str(
        row["Symptom"]
    ).strip()

    weight = int(
        row["weight"]
    )

    severity_dict[
        symptom
    ] = weight



def get_description(disease):

    disease = str(
        disease
    ).strip().lower()
    disease = DISEASE_ALIASES.get(disease, disease)

    for _,row in description_df.iterrows():

        current = str(
            row["Disease"]
        ).strip().lower()

        if current == disease:

            return row[
                "Description"
            ]

    return "No description available"



def get_precautions(disease):

    disease = str(
        disease
    ).strip().lower()
    disease = DISEASE_ALIASES.get(disease, disease)

    for _,row in precaution_df.iterrows():

        current = str(
            row["Disease"]
        ).strip().lower()

        if current == disease:

            precautions=[]

            for i in range(1,5):

                value = row[
                    f"Precaution_{i}"
                ]

                if pd.notna(value):

                    precautions.append(
                        str(value)
                    )

            return precautions

    return [

        "Consult doctor",
        "Monitor symptoms"

    ]



def calculate_risk(symptoms):

    total = 0

    for symptom in symptoms:

        total += severity_dict.get(
            symptom,
            0
        )

    if total >= 20:

        risk = "High"

    elif total >= 10:

        risk = "Medium"

    else:

        risk = "Low"

    return total,risk
