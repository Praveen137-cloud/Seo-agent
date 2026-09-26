import io
import html
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)

def clean_text(text: str) -> str:
    if not text:
        return ""
    # Escape HTML special chars so ReportLab XML parser doesn't crash on tags like <link> or <h1>
    return html.escape(str(text))

def generate_pdf_report(audit_data: dict, pages: list, issues: list, recommendations: list) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    story = []
    styles = getSampleStyleSheet()

    # Custom styles
    primary_color = colors.HexColor("#1e293b")
    brand_blue = colors.HexColor("#2563eb")
    light_bg = colors.HexColor("#f8fafc")
    text_dark = colors.HexColor("#0f172a")

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        textColor=primary_color,
        spaceAfter=6
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#64748b"),
        spaceAfter=15
    )

    h2_style = ParagraphStyle(
        'SectionH2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=primary_color,
        spaceBefore=15,
        spaceAfter=8
    )

    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=text_dark
    )

    bold_body_style = ParagraphStyle(
        'BoldBodyDark',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=13,
        textColor=text_dark
    )

    # 1. Header Banner
    target_url = clean_text(audit_data.get("target_url", ""))
    score = audit_data.get("score", 0)
    summary = audit_data.get("summary_data", {}) or {}
    grade = clean_text(summary.get("grade", "N/A"))
    date_str = datetime.now().strftime("%B %d, %Y")

    story.append(Paragraph("AI Website SEO Audit & Recommendations Report", title_style))
    story.append(Paragraph(f"Target URL: <b>{target_url}</b> | Generated on: {date_str}", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=brand_blue, spaceAfter=15))

    # 2. Score Overview Box
    score_color = colors.HexColor("#16a34a") if score >= 75 else (colors.HexColor("#ca8a04") if score >= 50 else colors.HexColor("#dc2626"))
    
    score_table_data = [
        [
            Paragraph(f"<font size=28 color='{score_color.hexval()}'><b>{score}/100</b></font><br/><font size=10 color='#64748b'>Overall SEO Score (Grade: {grade})</font>", body_style),
            Paragraph(f"<b>Pages Crawled:</b> {audit_data.get('pages_crawled', 0)}<br/>"
                      f"<b>Total Issues:</b> {len(issues)}<br/>"
                      f"<b>Critical / High:</b> {summary.get('severity_counts', {}).get('CRITICAL', 0) + summary.get('severity_counts', {}).get('HIGH', 0)}", body_style)
        ]
    ]

    t_score = Table(score_table_data, colWidths=[270, 270])
    t_score.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), light_bg),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#e2e8f0")),
        ('PADDING', (0, 0), (-1, -1), 12),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(t_score)
    story.append(Spacer(1, 15))

    # 3. Section Scores
    sec_scores = summary.get("section_scores", {})
    story.append(Paragraph("Category Performance Breakdowns", h2_style))
    
    sec_table_data = [
        ["Category", "Score", "Health Rating"],
        ["On-Page SEO", f"{sec_scores.get('on_page', 0)} / 100", "Good" if sec_scores.get('on_page', 0) >= 70 else "Needs Work"],
        ["Technical SEO", f"{sec_scores.get('technical', 0)} / 100", "Good" if sec_scores.get('technical', 0) >= 70 else "Needs Work"],
        ["Security (HTTPS/SSL)", f"{sec_scores.get('security', 0)} / 100", "Good" if sec_scores.get('security', 0) >= 70 else "Needs Work"],
        ["Performance", f"{sec_scores.get('performance', 0)} / 100", "Good" if sec_scores.get('performance', 0) >= 70 else "Needs Work"],
    ]

    t_sec = Table(sec_table_data, colWidths=[200, 150, 190])
    t_sec.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), primary_color),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
    ]))
    story.append(t_sec)
    story.append(Spacer(1, 15))

    # 4. Top Detected Issues
    story.append(Paragraph(f"Detected Audit Issues ({len(issues)} total)", h2_style))
    if issues:
        issue_rows = [["Severity", "Issue & Affected Page", "Category"]]
        for iss in issues[:12]:  # Limit top 12 for report size
            sev = clean_text(iss.get("severity", "LOW"))
            sev_color = "#dc2626" if sev == "CRITICAL" else ("#ea580c" if sev == "HIGH" else ("#d97706" if sev == "MEDIUM" else "#2563eb"))
            
            p_issue = Paragraph(f"<b>{clean_text(iss.get('title'))}</b><br/>"
                                f"<font color='#64748b'>{clean_text(iss.get('description'))}</font><br/>"
                                f"<font color='#2563eb'>URL: {clean_text(iss.get('page_url'))}</font>", body_style)
            
            p_sev = Paragraph(f"<font color='{sev_color}'><b>{sev}</b></font>", bold_body_style)
            p_cat = Paragraph(clean_text(iss.get("category", "on_page")).upper(), body_style)
            
            issue_rows.append([p_sev, p_issue, p_cat])

        t_issues = Table(issue_rows, colWidths=[80, 370, 90])
        t_issues.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(t_issues)
    else:
        story.append(Paragraph("No critical SEO issues detected.", body_style))

    story.append(Spacer(1, 15))

    # 5. AI Recommendations & Content Strategy
    story.append(Paragraph("AI-Generated Recommendations & Action Plan", h2_style))
    if recommendations:
        for idx, rec in enumerate(recommendations[:5], 1):
            p_rec_title = Paragraph(f"<b>{idx}. [{clean_text(rec.get('priority'))}] {clean_text(rec.get('title'))}</b>", bold_body_style)
            p_rec_exp = Paragraph(clean_text(rec.get("explanation", "")), body_style)
            
            steps = rec.get("actionable_steps", [])
            steps_text = "<br/>".join([f"• {clean_text(s)}" for s in steps]) if isinstance(steps, list) else clean_text(str(steps))
            p_steps = Paragraph(f"<b>Action Steps:</b><br/>{steps_text}", body_style)

            rec_box = Table([[p_rec_title], [p_rec_exp], [p_steps]], colWidths=[540])
            rec_box.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f0fdf4")),
                ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#bbf7d0")),
                ('PADDING', (0, 0), (-1, -1), 8),
            ]))
            story.append(rec_box)
            story.append(Spacer(1, 10))

    doc.build(story)
    return buffer.getvalue()
