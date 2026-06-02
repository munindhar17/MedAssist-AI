from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)

from reportlab.lib import styles
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from datetime import datetime


def generate_report(data):

    doc = SimpleDocTemplate(
        "medical_report.pdf"
    )

    style = styles.getSampleStyleSheet()

    content = []

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

    severity = data.get(
        "severity",
        "N/A"
    )

    triage_level = data.get(
        "triage_level",
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

    ignored_symptoms = prediction_explanation.get(
        "ignored_symptoms",
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

    content.append(Spacer(1, 12))

    content.append(
        Paragraph(
            f"Generated: {datetime.now().strftime('%d-%b-%Y %I:%M %p')}",
            style["Normal"]
        )
    )

    content.append(Spacer(1, 20))

    content.append(
        Paragraph(
            "Prediction Results",
            style["Heading2"]
        )
    )

    content.append(Spacer(1, 8))

    data_table = [
        ["Disease", disease],
        ["Confidence", confidence],
        ["Severity Score", str(severity)],
        ["Risk Level", risk],
        ["Triage Level", triage_level],
        ["Recommended Doctor", doctor]
    ]

    table = Table(data_table, colWidths=[2*inch, 4*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), HexColor('#e8f4f8')),
        ('TEXTCOLOR', (0, 0), (-1, -1), HexColor('#333333')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#cccccc')),
    ]))

    content.append(table)

    content.append(Spacer(1, 20))

    if matched_symptoms:
        content.append(
            Paragraph(
                "Matched Symptoms",
                style["Heading2"]
            )
        )
        content.append(Spacer(1, 8))
        matched_text = ", ".join(matched_symptoms)
        content.append(
            Paragraph(
                matched_text,
                style["BodyText"]
            )
        )
        content.append(Spacer(1, 12))

    if ignored_symptoms:
        content.append(
            Paragraph(
                "Additional Symptoms Noted",
                style["Heading2"]
            )
        )
        content.append(Spacer(1, 8))
        ignored_text = ", ".join(ignored_symptoms)
        content.append(
            Paragraph(
                ignored_text,
                style["BodyText"]
            )
        )
        content.append(Spacer(1, 12))

    if explanation_reason:
        content.append(
            Paragraph(
                "Prediction Analysis",
                style["Heading2"]
            )
        )
        content.append(Spacer(1, 8))
        content.append(
            Paragraph(
                explanation_reason,
                style["BodyText"]
            )
        )
        content.append(Spacer(1, 20))

    content.append(
        Paragraph(
            "Next Steps",
            style["Heading2"]
        )
    )
    content.append(Spacer(1, 8))
    content.append(
        Paragraph(
            f"Please consult with a {doctor} for proper evaluation and treatment. This report is for informational purposes only.",
            style["BodyText"]
        )
    )

    content.append(Spacer(1, 20))

    content.append(
        Paragraph(
            "Disclaimer",
            style["Heading2"]
        )
    )
    content.append(Spacer(1, 8))
    content.append(
        Paragraph(
            "This application is for educational purposes only and does not provide medical diagnosis, treatment, or emergency care recommendations. Always consult with qualified healthcare professionals for medical advice.",
            style["BodyText"]
        )
    )

    doc.build(content)

    return "medical_report.pdf"
