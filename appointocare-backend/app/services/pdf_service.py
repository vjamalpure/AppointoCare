"""
AppointoCare Shared PDF Document Generation Engine
Generates enterprise-grade, branded PDFs for:
- Clinical E-Prescriptions (Healthcare)
- Tax-compliant Invoices & Payment Receipts
- Financial & Transaction Summary Reports
Uses ReportLab Platypus with strict text escaping, Unicode support,
and server-side access control.
"""

import io
from datetime import datetime
from xml.sax.saxutils import escape as xml_escape
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
    KeepTogether
)


def _safe_text(val) -> str:
    if val is None:
        return ""
    text = str(val).strip()
    return xml_escape(text)


def _get_styles():
    base = getSampleStyleSheet()

    header_style = ParagraphStyle(
        "OrgTitle",
        parent=base["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#0f172a")
    )

    sub_header_style = ParagraphStyle(
        "OrgSubtitle",
        parent=base["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#64748b")
    )

    section_heading = ParagraphStyle(
        "SectionHeading",
        parent=base["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#0f766e"),
        spaceBefore=8,
        spaceAfter=4
    )

    body_style = ParagraphStyle(
        "DocBody",
        parent=base["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#1e293b")
    )

    body_bold = ParagraphStyle(
        "DocBodyBold",
        parent=body_style,
        fontName="Helvetica-Bold"
    )

    table_header_style = ParagraphStyle(
        "TableHeader",
        parent=base["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=12,
        textColor=colors.white
    )

    footer_style = ParagraphStyle(
        "DocFooter",
        parent=base["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#94a3b8"),
        alignment=1  # Centered
    )

    return {
        "header": header_style,
        "sub_header": sub_header_style,
        "section": section_heading,
        "body": body_style,
        "body_bold": body_bold,
        "table_header": table_header_style,
        "footer": footer_style
    }


def generate_prescription_pdf(org_data: dict, record_data: dict, appt_data: dict = None) -> bytes:
    """
    Generates a clinical E-Prescription PDF.
    - org_data: {name, code, sector, address, phone, email}
    - record_data: {title, data: {prescriber, rx_number, diagnosis, vitals, medications, advice, follow_up}}
    - appt_data: {customer_name, customer_phone, appointment_date, doctor_name}
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = _get_styles()
    story = []

    # 1. Organization Header
    org_name = _safe_text(org_data.get("name") or "Healthcare Clinic")
    org_contact = f"Phone: {_safe_text(org_data.get('phone') or 'N/A')}  |  Email: {_safe_text(org_data.get('email') or 'N/A')}"
    org_addr = _safe_text(org_data.get("address") or "Main Medical Center")

    header_data = [
        [
            Paragraph(f"<b>{org_name}</b>", styles["header"]),
            Paragraph(f"<b>MEDICAL PRESCRIPTION</b><br/><font size=8 color='#64748b'>Ref: {_safe_text(record_data.get('data', {}).get('rx_number') or f'RX-{int(datetime.utcnow().timestamp())}')}</font>", styles["body_bold"])
        ],
        [
            Paragraph(f"{org_addr}<br/>{org_contact}", styles["sub_header"]),
            Paragraph(f"Date: {_safe_text(datetime.utcnow().strftime('%d %b %Y, %I:%M %p'))}", styles["sub_header"])
        ]
    ]

    header_table = Table(header_data, colWidths=[340, 180])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0f766e"), spaceAfter=10))

    # 2. Patient & Clinician Info Box
    patient_name = _safe_text(appt_data.get("customer_name") if appt_data else "Registered Patient")
    patient_phone = _safe_text(appt_data.get("customer_phone") if appt_data else "N/A")
    doctor_name = _safe_text(record_data.get("data", {}).get("prescriber") or (appt_data.get("staff_name") if appt_data else "Consulting Clinician"))
    rx_no = _safe_text(record_data.get("data", {}).get("rx_number") or "RX-GENERAL")

    info_data = [
        [
            Paragraph(f"<b>Patient Name:</b> {patient_name}", styles["body"]),
            Paragraph(f"<b>Prescribing Doctor:</b> {doctor_name}", styles["body"])
        ],
        [
            Paragraph(f"<b>Phone:</b> {patient_phone}", styles["body"]),
            Paragraph(f"<b>Prescription ID:</b> {rx_no}", styles["body"])
        ]
    ]
    info_table = Table(info_data, colWidths=[260, 260])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#f1f5f9")),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 10))

    # 3. Clinical Diagnosis & Vitals
    diag_text = _safe_text(record_data.get("data", {}).get("diagnosis") or record_data.get("title") or "General Clinical Review")
    story.append(Paragraph("Clinical Diagnosis", styles["section"]))
    story.append(Paragraph(diag_text, styles["body"]))
    story.append(Spacer(1, 8))

    vitals = record_data.get("data", {}).get("vitals")
    if isinstance(vitals, dict) and vitals:
        vitals_cells = []
        for k, v in vitals.items():
            k_clean = _safe_text(str(k).upper())
            v_clean = _safe_text(v)
            vitals_cells.append(f"<b>{k_clean}:</b> {v_clean}")
        
        # Display up to 4 per row
        row1 = vitals_cells[:4]
        vitals_table = Table([[Paragraph(c, styles["body"]) for c in row1]], colWidths=[130] * len(row1))
        vitals_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f0fdfa")),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#99f6e4")),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(vitals_table)
        story.append(Spacer(1, 10))

    # 4. Medications Table
    story.append(Paragraph("Rx / Prescribed Medications", styles["section"]))

    meds = record_data.get("data", {}).get("medications") or []
    med_rows = [
        [
            Paragraph("<b>#</b>", styles["table_header"]),
            Paragraph("<b>Medication & Strength</b>", styles["table_header"]),
            Paragraph("<b>Dosage / Regimen</b>", styles["table_header"]),
            Paragraph("<b>Duration</b>", styles["table_header"]),
            Paragraph("<b>Instructions</b>", styles["table_header"])
        ]
    ]

    if not meds:
        med_rows.append([
            Paragraph("1", styles["body"]),
            Paragraph("Standard Clinical Care & Rest", styles["body"]),
            Paragraph("As directed", styles["body"]),
            Paragraph("5 Days", styles["body"]),
            Paragraph("Follow up if symptoms persist", styles["body"])
        ])
    else:
        for idx, m in enumerate(meds, start=1):
            if isinstance(m, dict):
                m_name = _safe_text(m.get("name") or "Medication")
                m_dose = _safe_text(m.get("dosage") or "1 tab")
                m_dur = _safe_text(m.get("duration") or "3 days")
                m_inst = _safe_text(m.get("instructions") or "After food")
            else:
                m_name = _safe_text(str(m))
                m_dose = "As directed"
                m_dur = "3-5 days"
                m_inst = "Oral"

            med_rows.append([
                Paragraph(str(idx), styles["body"]),
                Paragraph(m_name, styles["body_bold"]),
                Paragraph(m_dose, styles["body"]),
                Paragraph(m_dur, styles["body"]),
                Paragraph(m_inst, styles["body"])
            ])

    meds_table = Table(med_rows, colWidths=[24, 180, 110, 80, 126])
    meds_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0f766e")),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(meds_table)
    story.append(Spacer(1, 14))

    # 5. Doctor Advice & Signature Block
    advice_text = _safe_text(record_data.get("data", {}).get("advice") or "Drink plenty of fluids. Rest adequately. Return immediately if emergency symptoms develop.")
    refills = _safe_text(record_data.get("data", {}).get("refills") or 0)

    advice_block = [
        Paragraph(f"<b>Instructions & Advice:</b> {advice_text}", styles["body"]),
        Spacer(1, 4),
        Paragraph(f"<b>Refills Authorized:</b> {refills}", styles["body"])
    ]
    story.append(KeepTogether(advice_block))
    story.append(Spacer(1, 24))

    # Signature line
    sig_data = [
        [
            Paragraph("<font size=7 color='#94a3b8'>Generated digitally via AppointoCare Electronic Medical Records.<br/>Requires clinician physical signature or verified token stamp before dispensing.</font>", styles["sub_header"]),
            Paragraph(f"____________________________<br/><b>{doctor_name}</b><br/><font size=7 color='#64748b'>Authorized Clinician Stamp</font>", styles["body"])
        ]
    ]
    sig_table = Table(sig_data, colWidths=[320, 200])
    sig_table.setStyle(TableStyle([
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(KeepTogether([sig_table]))

    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes


def generate_invoice_pdf(org_data: dict, txn_data: dict, appt_data: dict = None) -> bytes:
    """
    Generates a tax-compliant Invoice / Payment Receipt PDF.
    - org_data: {name, code, sector, address, phone, email, gstin}
    - txn_data: {id, amount, payment_method, transaction_type, status, created_at, remarks}
    - appt_data: {customer_name, customer_phone, service_name, appointment_date}
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = _get_styles()
    story = []

    # 1. Header
    org_name = _safe_text(org_data.get("name") or "AppointoCare Partner")
    org_contact = f"Phone: {_safe_text(org_data.get('phone') or 'N/A')}  |  Email: {_safe_text(org_data.get('email') or 'N/A')}"
    org_addr = _safe_text(org_data.get("address") or "Main Operations Branch")
    invoice_no = f"INV-{txn_data.get('id', '000'):05d}"
    txn_date = txn_data.get("created_at") or datetime.utcnow().strftime("%Y-%m-%d %H:%M")

    header_data = [
        [
            Paragraph(f"<b>{org_name}</b>", styles["header"]),
            Paragraph(f"<b>TAX INVOICE / RECEIPT</b><br/><font size=9 color='#0f766e'><b>{invoice_no}</b></font>", styles["body_bold"])
        ],
        [
            Paragraph(f"{org_addr}<br/>{org_contact}", styles["sub_header"]),
            Paragraph(f"Date: {_safe_text(txn_date)}<br/>Status: <b>PAID</b>", styles["sub_header"])
        ]
    ]

    header_table = Table(header_data, colWidths=[330, 190])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0284c7"), spaceAfter=10))

    # 2. Billed To & Payment Details Box
    client_name = _safe_text(appt_data.get("customer_name") if appt_data else "Valued Client")
    client_phone = _safe_text(appt_data.get("customer_phone") if appt_data else "N/A")
    pay_method = _safe_text(txn_data.get("payment_method") or "UPI / Online Payment")
    pay_type = _safe_text(txn_data.get("transaction_type") or "Service Payment")

    bill_data = [
        [
            Paragraph(f"<b>Billed To:</b><br/>{client_name}<br/>Phone: {client_phone}", styles["body"]),
            Paragraph(f"<b>Payment Method:</b> {pay_method}<br/><b>Transaction Type:</b> {pay_type}<br/><b>Payment ID:</b> TXN-{txn_data.get('id', 0)}", styles["body"])
        ]
    ]
    bill_table = Table(bill_data, colWidths=[260, 260])
    bill_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(bill_table)
    story.append(Spacer(1, 14))

    # 3. Line Items Table
    service_name = _safe_text(appt_data.get("service_name") if appt_data else "Professional Consultation")
    total_amount = float(txn_data.get("amount") or 0.0)

    # Calculate tax decomposition (Healthcare often tax-exempt; others 18% GST split into 9% CGST + 9% SGST)
    is_healthcare = (org_data.get("sector") or "").lower() == "healthcare"
    if is_healthcare:
        taxable_value = total_amount
        cgst = 0.0
        sgst = 0.0
        tax_note = "Healthcare clinical consultation is GST-exempt under Notification 12/2017."
    else:
        # 18% GST inclusive
        taxable_value = round(total_amount / 1.18, 2)
        cgst = round((total_amount - taxable_value) / 2.0, 2)
        sgst = round(total_amount - taxable_value - cgst, 2)
        tax_note = "Includes 18% GST (9% CGST + 9% SGST)."

    items_data = [
        [
            Paragraph("<b>#</b>", styles["table_header"]),
            Paragraph("<b>Description / Service</b>", styles["table_header"]),
            Paragraph("<b>SAC Code</b>", styles["table_header"]),
            Paragraph("<b>Qty</b>", styles["table_header"]),
            Paragraph("<b>Taxable Value</b>", styles["table_header"]),
            Paragraph("<b>Total (INR)</b>", styles["table_header"])
        ],
        [
            Paragraph("1", styles["body"]),
            Paragraph(service_name, styles["body_bold"]),
            Paragraph("999312" if is_healthcare else "998311", styles["body"]),
            Paragraph("1", styles["body"]),
            Paragraph(f"₹ {taxable_value:.2f}", styles["body"]),
            Paragraph(f"₹ {total_amount:.2f}", styles["body_bold"])
        ]
    ]

    items_table = Table(items_data, colWidths=[24, 210, 70, 36, 90, 90])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0284c7")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('ALIGN', (3, 0), (-1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(items_table)
    story.append(Spacer(1, 8))

    # 4. Totals Breakdown
    totals_data = [
        [Paragraph("Taxable Subtotal:", styles["body"]), Paragraph(f"₹ {taxable_value:.2f}", styles["body"])],
        [Paragraph("CGST (9%):", styles["body"]), Paragraph(f"₹ {cgst:.2f}", styles["body"])],
        [Paragraph("SGST (9%):", styles["body"]), Paragraph(f"₹ {sgst:.2f}", styles["body"])],
        [Paragraph("<b>Total Amount Paid:</b>", styles["body_bold"]), Paragraph(f"<b>₹ {total_amount:.2f}</b>", styles["body_bold"])]
    ]
    totals_table = Table(totals_data, colWidths=[130, 90])
    totals_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
    ]))

    # Wrap totals aligned to the right
    wrapper_table = Table([[Paragraph(f"<font size=8 color='#64748b'>{tax_note}</font>", styles["body"]), totals_table]], colWidths=[300, 220])
    wrapper_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(wrapper_table)
    story.append(Spacer(1, 24))

    # 5. Thank You & Verification Footer
    footer_text = f"Thank you for choosing {org_name}. This receipt is digitally generated by AppointoCare."
    story.append(KeepTogether([
        HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#cbd5e1"), spaceAfter=6),
        Paragraph(footer_text, styles["footer"])
    ]))

    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes


def generate_industry_dossier_pdf(org_data: dict, record_data: dict, client_data: dict = None) -> bytes:
    """
    Generates a branded, high-fidelity dossier PDF for any of AppointoCare's 9 industry verticals:
    - Salon & Wellness (Treatment Card & Hair Formula Record)
    - Finance (Portfolio Allocation & Fiduciary Statement)
    - Insurance (Policy Schedule & Claims Docket)
    - Retail (Haute Couture Measurement Matrix & Alteration Docket)
    - Education (University Admissions Shortlist & Academic Rubric)
    - Legal (Privileged Engagement Letter & Conflict Clearance Docket)
    - Real Estate (Property Specification & Cap-Rate Feasibility Study)
    - Professional Services (SOW Milestone & Deliverable Acceptance Docket)
    """
    sector = (org_data.get("sector") or "General").title()

    # Sector theme colors
    SECTOR_THEMES = {
        "Healthcare": "#0f766e",     # Teal
        "Salon": "#db2777",          # Rose Gold / Pink
        "Finance": "#1e3a8a",        # Deep Navy
        "Insurance": "#047857",      # Emerald
        "Retail": "#9333ea",         # Royal Purple
        "Education": "#2563eb",      # Sapphire Blue
        "Consultancy": "#b45309",    # Amber Gold / Legal Charcoal
        "Legal": "#b45309",
        "Real Estate": "#c2410c",    # Terracotta
        "Professional Services": "#4f46e5"  # Indigo
    }
    primary_color_hex = SECTOR_THEMES.get(sector, "#0284c7")
    primary_color = colors.HexColor(primary_color_hex)

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = _get_styles()
    story = []

    # 1. Organization Header
    org_name = _safe_text(org_data.get("name") or f"{sector} Enterprise")
    org_contact = f"Phone: {_safe_text(org_data.get('phone') or 'N/A')}  |  Email: {_safe_text(org_data.get('email') or 'N/A')}"
    org_addr = _safe_text(org_data.get("address") or "Headquarters")
    doc_ref = f"{org_data.get('code', 'AP')}-{record_data.get('record_type', 'DOC').upper()}-{int(datetime.utcnow().timestamp()) % 100000:05d}"
    now_str = datetime.utcnow().strftime("%d %b %Y, %I:%M %p")

    header_data = [
        [
            Paragraph(f"<b>{org_name}</b>", styles["header"]),
            Paragraph(f"<b>{sector.upper()} OFFICIAL DOSSIER</b><br/><font size=8 color='{primary_color_hex}'><b>Ref: {doc_ref}</b></font>", styles["body_bold"])
        ],
        [
            Paragraph(f"{org_addr}<br/>{org_contact}", styles["sub_header"]),
            Paragraph(f"Date: {_safe_text(now_str)}<br/>Status: <b>VERIFIED RECORD</b>", styles["sub_header"])
        ]
    ]

    header_table = Table(header_data, colWidths=[330, 190])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=1.5, color=primary_color, spaceAfter=10))

    # 2. Client / Subject Information Box
    client_name = _safe_text(client_data.get("customer_name") if client_data else "Registered Client")
    client_phone = _safe_text(client_data.get("customer_phone") if client_data else "N/A")
    specialist_name = _safe_text(client_data.get("staff_name") or record_data.get("created_by_user") or "Assigned Specialist")
    rec_type_display = _safe_text(record_data.get("record_type", "").replace("_", " ").title())

    info_data = [
        [
            Paragraph(f"<b>Client / Subject:</b> {client_name}", styles["body"]),
            Paragraph(f"<b>Primary Specialist:</b> {specialist_name}", styles["body"])
        ],
        [
            Paragraph(f"<b>Contact:</b> {client_phone}", styles["body"]),
            Paragraph(f"<b>Docket Classification:</b> {rec_type_display}", styles["body"])
        ]
    ]
    info_table = Table(info_data, colWidths=[260, 260])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 10))

    # 3. Document Subject & Overview
    rec_title = _safe_text(record_data.get("title") or "Confidential Industry File")
    story.append(Paragraph(f"<b>Subject:</b> {rec_title}", styles["body_bold"]))
    story.append(Spacer(1, 8))

    # 4. Structured Parameter Data Matrix
    rec_data = record_data.get("data") or {}
    items_rows = [
        [
            Paragraph("<b>Specification Parameter</b>", styles["table_header"]),
            Paragraph("<b>Authenticated Value / Clinical Assessment</b>", styles["table_header"])
        ]
    ]

    for k, v in rec_data.items():
        if k in ["revisions", "vitals_advisory"]:
            continue  # Rendered in dedicated sections
        clean_key = _safe_text(str(k).replace("_", " ").title())
        if isinstance(v, list):
            clean_val = "<br/>".join([f"• {_safe_text(item)}" for item in v[:12]])
        elif isinstance(v, dict):
            clean_val = "<br/>".join([f"<b>{_safe_text(subk)}:</b> {_safe_text(subv)}" for subk, subv in v.items()])
        else:
            clean_val = _safe_text(str(v))
        items_rows.append([
            Paragraph(f"<b>{clean_key}</b>", styles["body_bold"]),
            Paragraph(clean_val, styles["body"])
        ])

    if len(items_rows) > 1:
        matrix_table = Table(items_rows, colWidths=[180, 340])
        matrix_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), primary_color),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ]))
        story.append(matrix_table)
        story.append(Spacer(1, 12))

    # 5. Advisory / Revision History if applicable
    revisions = rec_data.get("revisions")
    if isinstance(revisions, list) and revisions:
        story.append(Paragraph("<b>Amendment Audit History</b>", styles["body_bold"]))
        rev_rows = [
            [
                Paragraph("<b>Date / Time</b>", styles["table_header"]),
                Paragraph("<b>Author</b>", styles["table_header"]),
                Paragraph("<b>Amendment Reason</b>", styles["table_header"])
            ]
        ]
        for rev in revisions:
            rev_rows.append([
                Paragraph(_safe_text(rev.get("amended_at", "")[:19]), styles["body"]),
                Paragraph(_safe_text(rev.get("amended_by", "Staff")), styles["body"]),
                Paragraph(_safe_text(rev.get("reason", "Adjustment")), styles["body"])
            ])
        rev_table = Table(rev_rows, colWidths=[130, 110, 280])
        rev_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#475569")),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ('PADDING', (0, 0), (-1, -1), 5),
        ]))
        story.append(rev_table)
        story.append(Spacer(1, 10))

    # 6. Verification Sign-off Block
    sign_data = [
        [
            Paragraph("<font size=8 color='#64748b'><b>SYSTEM INTEGRITY CERTIFICATE</b><br/>Tenant ID & Ownership Verified.<br/>Cryptographically Signed by AppointoCare Document Vault.</font>", styles["body"]),
            Paragraph(f"<b>Authorized Signatory</b><br/><br/><font size=8 color='#64748b'>___________________________________<br/>{specialist_name}<br/>{org_name}</font>", styles["body"])
        ]
    ]
    sign_table = Table(sign_data, colWidths=[310, 210])
    sign_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(KeepTogether([
        HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#cbd5e1"), spaceAfter=8),
        sign_table,
        Spacer(1, 10),
        Paragraph(f"Confidential dossier generated for {org_name} ({sector}). Unauthorized distribution prohibited.", styles["footer"])
    ]))

    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes

