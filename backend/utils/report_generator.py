from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)

from reportlab.lib import styles


def generate_report(data):

    doc = SimpleDocTemplate(
        "medical_report.pdf"
    )

    style = styles.getSampleStyleSheet()

    content=[]

    disease = data.get(
        "disease",
        "No prediction generated"
    )

    confidence = data.get(
        "confidence",
        "N/A"
    )

    risk = data.get(
        "risk",
        "N/A"
    )

    doctor = data.get(
        "doctor",
        "N/A"
    )

    emergency = data.get(
        "emergency",
        "N/A"
    )

    prediction_explanation = data.get(
        "prediction_explanation",
        {}
    )

    matched_symptoms = prediction_explanation.get(
        "matched_symptoms",
        []
    )

    explanation_reason = prediction_explanation.get(
        "reason",
        ""
    )

    content.append(

        Paragraph(

            "MedAssist AI Health Report",

            style["Title"]

        )

    )

    content.append(
        Spacer(1,20)
    )

    content.append(

        Paragraph(

            f"Disease: {disease}",

            style["BodyText"]

        )

    )

    content.append(

        Paragraph(

            f"Confidence: {confidence}",

            style["BodyText"]

        )

    )

    content.append(

        Paragraph(

            f"Risk Level: {risk}",

            style["BodyText"]

        )

    )

    if matched_symptoms:
        content.append(
            Spacer(1, 10)
        )
        content.append(
            Paragraph(
                "Matched symptoms:",
                style["BodyText"]
            )
        )
        content.append(
            Paragraph(
                ", ".join(matched_symptoms),
                style["BodyText"]
            )
        )

    if explanation_reason:
        content.append(
            Spacer(1, 10)
        )
        content.append(
            Paragraph(
                f"Reason: {explanation_reason}",
                style["BodyText"]
            )
        )

    content.append(

        Paragraph(

            f"Doctor: {doctor}",

            style["BodyText"]

        )

    )

    content.append(

        Paragraph(

            f"Emergency: {emergency}",

            style["BodyText"]

        )

    )

    content.append(
        Spacer(1, 18)
    )

    content.append(

        Paragraph(

            "Disclaimer: This application is for educational purposes only and does not provide medical diagnosis, treatment, or emergency care recommendations.",

            style["BodyText"]

        )

    )

    doc.build(content)

    return "medical_report.pdf"
