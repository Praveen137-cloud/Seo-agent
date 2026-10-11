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

    # Custom styling
    primary_color = colors.HexColor("#0f172a")
    brand_red = colors.HexColor("#dc2626")
    brand_blue = colors.HexColor("#2563eb")
    light_bg = colors.HexColor("#f8fafc")
    text_dark = colors.HexColor("#1e293b")

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=primary_color,
        spaceAfter=4
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#64748b"),
        spaceAfter=12
    )

    h2_style = ParagraphStyle(
        'SectionH2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=primary_color,
        spaceBefore=14,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=text_dark
    )

    bold_body_style = ParagraphStyle(
        'BoldBodyDark',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=12,
        textColor=text_dark
    )

    code_snippet_style = ParagraphStyle(
        'CodeSnippet',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor("#0f172a")
    )

    # 1. Real-Time Header
    target_url = clean_text(audit_data.get("target_url", ""))
    score = audit_data.get("score", 0)
    summary = audit_data.get("summary_data", {}) or {}
    grade = clean_text(summary.get("grade", "N/A"))
    real_time_timestamp = datetime.utcnow().strftime("%B %d, %Y at %H:%M:%S UTC")

    story.append(Paragraph("AI-Powered Website SEO Analysis & Audit Report", title_style))
    story.append(Paragraph(f"Target: <b>{target_url}</b> &nbsp;|&nbsp; Audit Timestamp: <b>{real_time_timestamp}</b>", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=brand_red, spaceAfter=12))

    # 2. Executive Scorecard Box
    score_color = colors.HexColor("#16a34a") if score >= 75 else (colors.HexColor("#ca8a04") if score >= 50 else colors.HexColor("#dc2626"))
    pages_crawled = audit_data.get('pages_crawled', 0)
    
    score_table_data = [
        [
            Paragraph(f"<font size=28 color='{score_color.hexval()}'><b>{score}/100</b></font><br/><font size=10 color='#64748b'>Overall SEO Score (Grade: {grade})</font>", body_style),
            Paragraph(
                f"<b>Real-Time Diagnostic Metrics:</b><br/>"
                f"• Crawled Pages: <b>{pages_crawled}</b><br/>"
                f"• Total Detected Issues: <b>{len(issues)}</b><br/>"
                f"• Critical Issues: <font color='#dc2626'><b>{summary.get('severity_counts', {}).get('CRITICAL', 0)}</b></font> &nbsp;|&nbsp; "
                f"High: <font color='#ea580c'><b>{summary.get('severity_counts', {}).get('HIGH', 0)}</b></font> &nbsp;|&nbsp; "
                f"Medium: <b>{summary.get('severity_counts', {}).get('MEDIUM', 0)}</b>",
                body_style
            )
        ]
    ]

    t_score = Table(score_table_data, colWidths=[240, 300])
    t_score.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), light_bg),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
        ('PADDING', (0, 0), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(t_score)
    story.append(Spacer(1, 10))

    # 3. Category Breakdown Matrix
    sec_scores = summary.get("section_scores", {})
    story.append(Paragraph("Category Health Breakdown", h2_style))
    
    sec_table_data = [
        ["Category", "Score", "Benchmark Status"],
        ["On-Page Content & Metadata", f"{sec_scores.get('on_page', 0)} / 100", "Optimized" if sec_scores.get('on_page', 0) >= 70 else "Action Required"],
        ["Technical SEO & Crawlability", f"{sec_scores.get('technical', 0)} / 100", "Optimized" if sec_scores.get('technical', 0) >= 70 else "Action Required"],
        ["Security & HTTPS Protocol", f"{sec_scores.get('security', 0)} / 100", "Secure" if sec_scores.get('security', 0) >= 90 else "Vulnerable"],
        ["Performance & Server Latency", f"{sec_scores.get('performance', 0)} / 100", "Fast" if sec_scores.get('performance', 0) >= 70 else "Needs Work"],
    ]

    t_sec = Table(sec_table_data, colWidths=[200, 140, 200])
    t_sec.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), primary_color),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 5),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
    ]))
    story.append(t_sec)
    story.append(Spacer(1, 10))

    # 4. Real-Time Detected SEO Issues
    story.append(Paragraph(f"Real-Time Detected SEO Issues ({len(issues)} total findings)", h2_style))
    if issues:
        issue_rows = [["Severity", "Finding & Context", "Category"]]
        for iss in issues[:16]:  # Display top 16 distinct issues
            sev = clean_text(iss.get("severity", "LOW"))
            sev_color = "#dc2626" if sev == "CRITICAL" else ("#ea580c" if sev == "HIGH" else ("#d97706" if sev == "MEDIUM" else "#2563eb"))
            
            p_issue = Paragraph(
                f"<b>{clean_text(iss.get('title'))}</b><br/>"
                f"<font color='#64748b'>{clean_text(iss.get('description'))}</font><br/>"
                f"<font color='#2563eb'>Affected: {clean_text(iss.get('page_url'))}</font>",
                body_style
            )
            p_sev = Paragraph(f"<font color='{sev_color}'><b>{sev}</b></font>", bold_body_style)
            p_cat = Paragraph(clean_text(iss.get("category", "on_page")).replace("_", " ").upper(), body_style)
            issue_rows.append([p_sev, p_issue, p_cat])

        t_issues = Table(issue_rows, colWidths=[70, 390, 80])
        t_issues.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('PADDING', (0, 0), (-1, -1), 5),
        ]))
        story.append(t_issues)
    else:
        story.append(Paragraph("No critical SEO issues detected during crawl.", body_style))

    story.append(Spacer(1, 12))

    # 5. AI Recommendations & Content Strategy
    story.append(Paragraph("AI-Generated Recommendations & Copywriting Action Plan", h2_style))
    if recommendations:
        for idx, rec in enumerate(recommendations[:5], 1):
            p_rec_title = Paragraph(f"<b>{idx}. [{clean_text(rec.get('priority'))}] {clean_text(rec.get('title'))}</b>", bold_body_style)
            p_rec_exp = Paragraph(clean_text(rec.get("explanation", "")), body_style)
            
            steps = rec.get("actionable_steps", [])
            steps_text = "<br/>".join([f"• {clean_text(s)}" for s in steps]) if isinstance(steps, list) else clean_text(str(steps))
            p_steps = Paragraph(f"<b>Action Steps:</b><br/>{steps_text}", body_style)

            # AI Content Suggestions if present
            content = rec.get("suggested_content") or {}
            content_elements = [p_rec_title, p_rec_exp, p_steps]
            
            if content.get("suggested_meta_title") or content.get("suggested_meta_description"):
                p_copy = Paragraph(
                    f"<b>AI Recommended Content Fix:</b><br/>"
                    f"• <b>Proposed Title:</b> {clean_text(content.get('suggested_meta_title', ''))}<br/>"
                    f"• <b>Proposed Description:</b> {clean_text(content.get('suggested_meta_description', ''))}<br/>"
                    f"• <b>Proposed H1:</b> {clean_text(content.get('suggested_h1', ''))}<br/>"
                    f"• <b>Target Keyword:</b> <i>{clean_text(content.get('primary_keyword', ''))}</i>",
                    code_snippet_style
                )
                content_elements.append(p_copy)

            rec_box = Table([[elem] for elem in content_elements], colWidths=[540])
            rec_box.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f0fdf4")),
                ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#86efac")),
                ('PADDING', (0, 0), (-1, -1), 7),
            ]))
            story.append(rec_box)
            story.append(Spacer(1, 8))

    doc.build(story)
    return buffer.getvalue()
