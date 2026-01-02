from fpdf import FPDF
from datetime import datetime

def generate_report(history):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(0, 10, "Medical Translation Report", ln=True)
    pdf.cell(0, 10, str(datetime.now()), ln=True)

    for h in history:
        pdf.multi_cell(
            0, 8,
            f"{h['mode']}:\n{h['source']}\n\nTranslated:\n{h['translated']}\n"
        )

    path = "medical_report.pdf"
    pdf.output(path)
    return path
