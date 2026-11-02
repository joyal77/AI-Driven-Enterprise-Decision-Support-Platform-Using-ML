import os
import datetime
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY

def build_pdf_presentation():
    pdf_filename = "Enterprise_Decision_Platform_Updated_Presentation.pdf"
    
    # 11 x 8.5 inches landscape slides
    doc = SimpleDocTemplate(
        pdf_filename,
        pagesize=landscape(letter),
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Brand Palette
    PRIMARY = colors.HexColor("#0A2540")      # Deep Executive Navy
    SECONDARY = colors.HexColor("#0073E6")    # Royal Accent Blue
    GOLD_ACCENT = colors.HexColor("#FF9900")  # Amazon Gold
    TEXT_DARK = colors.HexColor("#1E293B")    # Slate Dark
    TEXT_MUTED = colors.HexColor("#64748B")   # Slate Muted
    BG_LIGHT = colors.HexColor("#F8FAFC")     # Soft Background
    BORDER_COLOR = colors.HexColor("#CBD5E1") # Light Border
    HIGH_RISK = colors.HexColor("#DC2626")    # Red
    MED_RISK = colors.HexColor("#D97706")     # Amber
    LOW_RISK = colors.HexColor("#16A34A")     # Green

    # Typography Styles
    slide_title_style = ParagraphStyle(
        'SlideTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=PRIMARY,
        spaceAfter=4
    )

    slide_subtitle_style = ParagraphStyle(
        'SlideSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=10,
        leading=13,
        textColor=TEXT_MUTED,
        spaceAfter=12
    )

    card_header_style = ParagraphStyle(
        'CardHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=15,
        textColor=SECONDARY,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        'SlideBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=TEXT_DARK
    )

    body_bold_style = ParagraphStyle(
        'SlideBodyBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=13.5,
        textColor=PRIMARY
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.white,
        alignment=TA_CENTER
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10.5,
        textColor=TEXT_DARK
    )

    table_cell_center_style = ParagraphStyle(
        'TableCellCenter',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10.5,
        textColor=TEXT_DARK,
        alignment=TA_CENTER
    )

    story = []

    def add_header(title, subtitle=""):
        tb = [
            [
                Paragraph(title.upper(), slide_title_style),
                Paragraph("MINI PROJECT – 20MCA245 | PANEL PRESENTATION", ParagraphStyle('SubHeader', fontName='Helvetica-Bold', fontSize=8.5, textColor=SECONDARY, alignment=TA_RIGHT))
            ]
        ]
        t = Table(tb, colWidths=[520, 200])
        t.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('PADDING', (0,0), (-1,-1), 0),
        ]))
        story.append(t)
        story.append(HRFlowable(width="100%", thickness=2, color=GOLD_ACCENT, spaceBefore=4, spaceAfter=8))

    # =========================================================================
    # SLIDE 1: Title Slide
    # =========================================================================
    title_box_data = [
        [
            Paragraph("MINI PROJECT – 20MCA245 | ACADEMIC PANEL PRESENTATION", ParagraphStyle('T1', fontName='Helvetica-Bold', fontSize=11, textColor=SECONDARY, alignment=TA_CENTER)),
        ],
        [
            Paragraph("AI-BASED ENTERPRISE DECISION SUPPORT PLATFORM USING MACHINE LEARNING", ParagraphStyle('T2', fontName='Helvetica-Bold', fontSize=20, leading=24, textColor=PRIMARY, alignment=TA_CENTER)),
        ],
        [
            Paragraph("An Explainable AI-Driven Customer Churn Prediction & Sales Forecasting System", ParagraphStyle('T3', fontName='Helvetica-Oblique', fontSize=11, textColor=TEXT_MUTED, alignment=TA_CENTER))
        ]
    ]

    title_table = Table(title_box_data, colWidths=[720])
    title_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), BG_LIGHT),
        ('BOX', (0,0), (-1,-1), 1.5, SECONDARY),
        ('PADDING', (0,0), (-1,-1), 12),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(Spacer(1, 20))
    story.append(title_table)
    story.append(Spacer(1, 25))

    info_data = [
        [
            Paragraph("<b>STUDENT DETAILS</b>", card_header_style),
            Paragraph("<b>PROJECT GUIDANCE</b>", card_header_style)
        ],
        [
            Paragraph("• <b>Student Name:</b> Joyal Jobai<br/>• <b>Roll No:</b> 34<br/>• <b>Course:</b> MCA, S3<br/>• <b>Branch:</b> Master of Computer Applications", body_style),
            Paragraph("• <b>Guide Name:</b> Sukrith Lal<br/>• <b>Designation:</b> Assistant Professor<br/>• <b>Department:</b> Dept of Computer Applications<br/>• <b>Institution:</b> ASIET / APJ Abdul Kalam Technological University", body_style)
        ]
    ]
    info_table = Table(info_data, colWidths=[350, 350])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.white),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('PADDING', (0,0), (-1,-1), 10),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(info_table)
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 2: Introduction – Problem & Motivation
    # =========================================================================
    add_header("Introduction: Problem & Motivation")
    
    prob_data = [
        [
            Paragraph("1. Problem Domain Overview", card_header_style),
            Paragraph("2. Motivation Behind Selection", card_header_style)
        ],
        [
            Paragraph(
                "• <b>Subscription Economy:</b> Modern B2B SaaS, E-Commerce, and Finance rely heavily on recurring account revenue for growth.<br/>"
                "• <b>High Cost of Churn:</b> Acquiring a new customer costs <b>5x to 7x more</b> than retaining an existing account. A 5% churn reduction boosts profit by 25%–95%.<br/>"
                "• <b>Executive Decision Support:</b> Leadership requires automated platforms combining predictive scoring with actionable retention strategy.<br/>"
                "• <b>Proactive Risk Monitoring:</b> Legacy tools act after customer loss, whereas enterprise systems demand continuous risk identification.",
                body_style
            ),
            Paragraph(
                "• <b>Explainable AI (XAI):</b> Traditional ML models predict churn probability but fail to explain <i>why</i> specific accounts are leaving.<br/>"
                "• <b>Eliminating Black-Box Opacity:</b> Integrating SHAP TreeExplainer to calculate exact feature attributions for every prediction.<br/>"
                "• <b>Automated Prescriptive Engine:</b> Legacy dashboards alert managers of churn but offer no automated, personalized retention action playbooks.<br/>"
                "• <b>Unified Full-Stack Architecture:</b> End-to-end integration: Database → Random Forest / XGBoost → Risk Triage → Severity Root Causes → SHAP → React SPA & PDF Preview.",
                body_style
            )
        ]
    ]
    prob_table = Table(prob_data, colWidths=[350, 350])
    prob_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.white),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('PADDING', (0,0), (-1,-1), 10),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(prob_table)
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 3: Literature Review – Part 1
    # =========================================================================
    add_header("Literature Review: Selected Research Papers (Part 1)")
    
    lit1_data = [
        [
            Paragraph("<b>Paper 1: Joy et al. (IEEE Access, 2024)</b>", card_header_style),
            Paragraph("<b>Paper 2: Bhuria & Aluvala (IEEE InCACCT, 2025)</b>", card_header_style)
        ],
        [
            Paragraph(
                "• <b>Title:</b> A Big Data-Driven Hybrid Model for Enhancing Streaming Service Customer Retention Through Churn Prediction Integrated With Explainable AI<br/>"
                "• <b>Authors & Venue:</b> U. G. Joy, K. E. Hoque, M. N. Uddin, et al. (IEEE Access, 2024)<br/>"
                "• <b>Methodology:</b> Big Data hybrid ML architecture combined with SHAP feature attribution.<br/>"
                "• <b>Key Advantage:</b> Connects churn prediction directly with SHAP feature importance.<br/>"
                "• <b>Key Limitation:</b> Restricted to streaming domain; lacks automated prescriptive playbooks and live web application backend.",
                body_style
            ),
            Paragraph(
                "• <b>Title:</b> Predicting Bank Customer Churn: An XGBoost Approach to Enhancing Customer Retention<br/>"
                "• <b>Authors & Venue:</b> R. Bhuria, S. Aluvala (IEEE InCACCT, 2025)<br/>"
                "• <b>Methodology:</b> Multi-level ML framework evaluating KNN, XGBoost, Random Forest, and SVM.<br/>"
                "• <b>Key Advantage:</b> Empirical validation for XGBoost superiority in customer churn classification.<br/>"
                "• <b>Key Limitation:</b> Focuses strictly on accuracy; lacks SHAP explainability, root cause diagnosis, and action playbooks.",
                body_style
            )
        ]
    ]
    lit1_table = Table(lit1_data, colWidths=[350, 350])
    lit1_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.white),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('PADDING', (0,0), (-1,-1), 10),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(lit1_table)
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 4: Literature Review – Part 2
    # =========================================================================
    add_header("Literature Review: Selected Research Papers (Part 2)")
    
    lit2_data = [
        [
            Paragraph("<b>Paper 3: Chandan et al. (IEEE ICRTCST, 2024)</b>", card_header_style),
            Paragraph("<b>Paper 4: Li & Yan (DSFE Journal, 2025)</b>", card_header_style)
        ],
        [
            Paragraph(
                "• <b>Title:</b> A Novel Machine Learning-Based Early Warning Detection System for Business Customer Churn<br/>"
                "• <b>Authors & Venue:</b> R. R. Chandan, R. S., Sarishma, P. P. Devi, et al. (IEEE ICRTCST, 2024)<br/>"
                "• <b>Methodology:</b> Early warning detection architecture leveraging ML classifiers for risk identification.<br/>"
                "• <b>Key Advantage:</b> Establishes conceptual early-warning risk flow (Behavior → Risk → Action).<br/>"
                "• <b>Key Limitation:</b> Lacks post-hoc SHAP feature attribution, root cause diagnostic mapping, and unified database support.",
                body_style
            ),
            Paragraph(
                "• <b>Title:</b> Prediction of Bank Credit Customers Churn Based on Machine Learning and Interpretability Analysis<br/>"
                "• <b>Authors & Venue:</b> Y. Li, K. Yan (Data Science in Finance and Economics, 2025)<br/>"
                "• <b>Methodology:</b> XGBoost classifier + SHAP interpretability for bank credit churn detection.<br/>"
                "• <b>Key Advantage:</b> Evaluates individual variable influences using SHAP (~97% AUC).<br/>"
                "• <b>Key Limitation:</b> Purely diagnostic research study; lacks automated prescriptive action playbooks and enterprise web platform.",
                body_style
            )
        ]
    ]
    lit2_table = Table(lit2_data, colWidths=[350, 350])
    lit2_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.white),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('PADDING', (0,0), (-1,-1), 10),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(lit2_table)
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 5: Literature Review – Comparison Matrix
    # =========================================================================
    add_header("Literature Review: Comparative Analysis Matrix")

    comp_data = [
        [
            Paragraph("Paper / Reference System", table_header_style),
            Paragraph("ML Model", table_header_style),
            Paragraph("Risk Triage", table_header_style),
            Paragraph("SHAP / XAI", table_header_style),
            Paragraph("Severity Root Cause", table_header_style),
            Paragraph("Prescriptive Playbooks", table_header_style),
            Paragraph("Unified Full-Stack SPA & PDF Preview", table_header_style)
        ],
        [
            Paragraph("<b>Paper 1: Joy et al. (IEEE 2024)</b>", table_cell_style),
            Paragraph("ML Hybrid", table_cell_center_style),
            Paragraph("✓ Yes", table_cell_center_style),
            Paragraph("✓ SHAP", table_cell_center_style),
            Paragraph("✕ Partial", table_cell_center_style),
            Paragraph("✕ No", table_cell_center_style),
            Paragraph("✕ No", table_cell_center_style)
        ],
        [
            Paragraph("<b>Paper 2: Bhuria & Aluvala (IEEE 2025)</b>", table_cell_style),
            Paragraph("XGBoost / RF", table_cell_center_style),
            Paragraph("✓ Yes", table_cell_center_style),
            Paragraph("✕ No", table_cell_center_style),
            Paragraph("✕ No", table_cell_center_style),
            Paragraph("✕ No", table_cell_center_style),
            Paragraph("✕ No", table_cell_center_style)
        ],
        [
            Paragraph("<b>Paper 3: Chandan et al. (IEEE 2024)</b>", table_cell_style),
            Paragraph("ML Classifier", table_cell_center_style),
            Paragraph("✓ Early Warning", table_cell_center_style),
            Paragraph("✕ No", table_cell_center_style),
            Paragraph("✕ No", table_cell_center_style),
            Paragraph("✕ No", table_cell_center_style),
            Paragraph("✕ No", table_cell_center_style)
        ],
        [
            Paragraph("<b>Paper 4: Li & Yan (DSFE 2025)</b>", table_cell_style),
            Paragraph("XGBoost", table_cell_center_style),
            Paragraph("✓ Yes", table_cell_center_style),
            Paragraph("✓ SHAP", table_cell_center_style),
            Paragraph("✓ Yes", table_cell_center_style),
            Paragraph("✕ No", table_cell_center_style),
            Paragraph("✕ No", table_cell_center_style)
        ],
        [
            Paragraph("<b>PROPOSED SYSTEM (Joyal Jobai)</b>", ParagraphStyle('P1', parent=table_cell_style, fontName='Helvetica-Bold', textColor=PRIMARY)),
            Paragraph("<b>RF & XGBoost</b>", table_cell_center_style),
            Paragraph("<b>✓ High/Med/Low</b>", table_cell_center_style),
            Paragraph("<b>✓ SHAP Engine</b>", table_cell_center_style),
            Paragraph("<b>✓ Severity-Ranked</b>", table_cell_center_style),
            Paragraph("<b>✓ Automated Playbooks</b>", table_cell_center_style),
            Paragraph("<b>✓ FastAPI + React SPA & PDF Preview</b>", table_cell_center_style)
        ]
    ]

    comp_table = Table(comp_data, colWidths=[140, 80, 80, 80, 100, 100, 140])
    comp_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('PADDING', (0,0), (-1,-1), 6),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0,1), (-1,-2), [colors.white, BG_LIGHT]),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor("#FEF3C7")), # Highlighted Proposed System row
        ('BOX', (0,-1), (-1,-1), 1.5, GOLD_ACCENT)
    ]))
    story.append(comp_table)
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 6: Literature Review – Research Gap & Novelty
    # =========================================================================
    add_header("Literature Review: Identified Research Gap & Novelty")

    gap_data = [
        [
            Paragraph("1. Research Gap & Theoretical Progression", card_header_style),
            Paragraph("2. The Core Innovation & Novelty", card_header_style)
        ],
        [
            Paragraph(
                "• <b>Fragmented State-of-the-Art:</b> Prior research treats churn scoring, SHAP feature attributions, and early warning systems as isolated theoretical techniques.<br/>"
                "• <b>Diagnostic Void:</b> Existing academic frameworks stop at raw prediction probabilities or static plots, failing to translate model output into automated retention playbooks.<br/>"
                "• <b>Static Output Limitations:</b> Literature lacks customer-specific primary driver ranking, returning identical generic statements for high-risk accounts.",
                body_style
            ),
            Paragraph(
                "• <b>End-to-End Platform Integration:</b> Seamlessly connects SQLite/MySQL Database → Random Forest / XGBoost ML Inference → High/Med/Low Risk Triage → Severity-Ranked Root Cause Extractor → SHAP Explainability → Prescriptive Retention Action Engine → React SPA & Live PDF Preview.<br/>"
                "• <b>Dynamic Severity Ranking:</b> Ranks customer friction vectors mathematically to surface personalized primary drivers.<br/>"
                "• <b>Interactive PDF Preview Integration:</b> Enables instant browser preview (`window.open(url, '_blank')`) without force-downloading files.",
                body_style
            )
        ]
    ]
    gap_table = Table(gap_data, colWidths=[350, 350])
    gap_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.white),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('PADDING', (0,0), (-1,-1), 10),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(gap_table)
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 7: Existing System – Overview & Limitations
    # =========================================================================
    add_header("Existing System: Operational Overview & Limitations")

    exist_data = [
        [
            Paragraph("1. Existing Approaches in Enterprise", card_header_style),
            Paragraph("2. Critical Operational Limitations", card_header_style)
        ],
        [
            Paragraph(
                "• <b>Traditional BI Dashboards:</b> Static reporting tools (Tableau/PowerBI) display historical churn numbers after accounts have already cancelled.<br/>"
                "• <b>Manual Spreadsheet Audits:</b> Account managers review customer logs manually using basic Excel filtering and subjective guesswork.<br/>"
                "• <b>Isolated Statistical Models:</b> Standalone logistic regression scripts operate independently of production CRM databases.<br/>"
                "• <b>Unstructured Retention Process:</b> Customer intervention relies on ad-hoc phone calls without standardized risk playbooks.",
                body_style
            ),
            Paragraph(
                "• <b>Reactive Detection:</b> Churn is detected after accounts have ceased purchasing, missing early intervention windows.<br/>"
                "• <b>Black-Box AI Opacity:</b> ML models output raw risk scores (e.g., 85% risk) without explaining individual feature drivers.<br/>"
                "• <b>Manual Investigation Delays:</b> Teams must manually investigate churn drivers, delaying outreach by days or weeks.<br/>"
                "• <b>Data & Workflow Fragmentation:</b> Databases, predictive models, and retention steps exist in silos, incurring 5x–7x re-acquisition costs.",
                body_style
            )
        ]
    ]
    exist_table = Table(exist_data, colWidths=[350, 350])
    exist_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.white),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('PADDING', (0,0), (-1,-1), 10),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(exist_table)
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 8: Proposed System – Overview & Core Features
    # =========================================================================
    add_header("Proposed System: Overview & Key Platform Modules")

    prop_data = [
        [
            Paragraph("High-Level Platform Architecture & Modules", card_header_style)
        ],
        [
            Paragraph(
                "1. <b>Database Ingestion Layer:</b> SQLite / MySQL relational storage for customer profiles, transaction history, and prediction logs.<br/>"
                "2. <b>ML Predictive Engine:</b> Scikit-Learn Random Forest Classifier (v1.0) & XGBoost scoring risk with <b>94.87% accuracy</b>.<br/>"
                "3. <b>Risk Triage Classification:</b> Automatically categorizes accounts into High Risk (≥70%), Medium Risk (30-69%), and Low Risk (<30%).<br/>"
                "4. <b>Dynamic Severity Root Cause Engine:</b> Evaluates customer friction signals (support tickets, late deliveries, inactivity days, cart abandonments, ratings) and ranks them mathematically.<br/>"
                "5. <b>SHAP TreeExplainer (XAI):</b> Computes exact local Shapley values showing exact positive and negative feature attributions.<br/>"
                "6. <b>Prescriptive Retention Playbooks:</b> Automatically maps friction vectors to targeted action plans (priority support, win-back discounts).<br/>"
                "7. <b>React SPA & Live PDF Preview:</b> Interactive executive dashboard featuring single page navigation and browser PDF preview (`window.open(url, '_blank')`).",
                body_style
            )
        ]
    ]
    prop_table = Table(prop_data, colWidths=[700])
    prop_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.white),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('PADDING', (0,0), (-1,-1), 12),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(prop_table)
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 9: System Architecture – Data Flow Pipeline
    # =========================================================================
    add_header("System Architecture: Data Flow Pipeline")

    pipe_data = [
        [
            Paragraph("1. Data Ingestion<br/>(SQLite / MySQL)", table_header_style),
            Paragraph("2. ML Inference<br/>(Random Forest)", table_header_style),
            Paragraph("3. Risk Triage<br/>(High/Med/Low)", table_header_style),
            Paragraph("4. Severity Root Cause<br/>(Diagnostic Engine)", table_header_style),
            Paragraph("5. SHAP XAI<br/>(TreeExplainer)", table_header_style),
            Paragraph("6. Prescriptive Action<br/>(Decision Engine)", table_header_style),
            Paragraph("7. Dashboard & PDF<br/>(React + ReportLab)", table_header_style)
        ]
    ]
    pipe_table = Table(pipe_data, colWidths=[100, 100, 100, 100, 100, 100, 100])
    pipe_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), PRIMARY),
        ('BOX', (0,0), (-1,-1), 1.5, GOLD_ACCENT),
        ('GRID', (0,0), (-1,-1), 0.5, colors.white),
        ('PADDING', (0,0), (-1,-1), 8),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ALIGN', (0,0), (-1,-1), 'CENTER')
    ]))
    story.append(pipe_table)
    story.append(Spacer(1, 15))

    pipe_desc_data = [
        [
            Paragraph("<b>Pipeline Stage Execution Breakdown</b>", card_header_style)
        ],
        [
            Paragraph(
                "• <b>Data Preprocessing & Scaling:</b> Customer records are ingested, missing values imputed via SimpleImputer, and continuous variables normalized via StandardScaler.<br/>"
                "• <b>Inference & Risk Triage:</b> Random Forest Classifier predicts churn probability ($P(\\text{Churn})$) and categorizes accounts into High, Medium, or Low Risk.<br/>"
                "• <b>Severity-Ranked Root Cause Analysis:</b> Friction metrics are evaluated against mathematical severity formulas to identify the #1 primary cause per customer.<br/>"
                "• <b>SHAP Feature Attribution:</b> TreeExplainer calculates exact local Shapley values (\\phi_i) quantifying exact feature contributions.<br/>"
                "• <b>Prescriptive Action & Presentation:</b> Action playbooks are generated and exposed via FastAPI REST endpoints to the React SPA dashboard and ReportLab PDF preview generator.",
                body_style
            )
        ]
    ]
    pipe_desc_table = Table(pipe_desc_data, colWidths=[700])
    pipe_desc_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), BG_LIGHT),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('PADDING', (0,0), (-1,-1), 10),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(pipe_desc_table)
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 10: Methodology & Core ML/XAI Modules
    # =========================================================================
    add_header("Methodology & Core ML/XAI Modules")

    meth_data = [
        [
            Paragraph("Predictive Analytics & XAI Modules", card_header_style),
            Paragraph("Diagnostic & Prescriptive Engine Modules", card_header_style)
        ],
        [
            Paragraph(
                "• <b>Random Forest Classifier (v1.0):</b> Ensemble of 100 decision trees (max depth = 12) trained with balanced class weights for robust churn probability scoring.<br/>"
                "• <b>XGBoost Classifier:</b> Baseline gradient boosted trees model optimizing binary cross-entropy loss.<br/>"
                "• <b>SHAP TreeExplainer:</b> Computes local Shapley values breaking down feature contributions (+/-) for every customer.<br/>"
                "• <b>Scikit-Learn Pipeline:</b> Clean ColumnTransformer handling categorical OneHotEncoding and numerical scaling.",
                body_style
            ),
            Paragraph(
                "• <b>Dynamic Severity Root Cause Extractor:</b> Ranks friction metrics (support tickets, late deliveries, inactivity days, cart abandonments, ratings) mathematically to derive personalized primary drivers.<br/>"
                "• <b>Prescriptive Action Engine:</b> Rule-driven recommendation algorithm mapping primary causes to retention playbooks.<br/>"
                "• <b>Executive React SPA & ReportLab PDF Engine:</b> Modern single-page web dashboard and server-side PDF generator with live browser preview.",
                body_style
            )
        ]
    ]
    meth_table = Table(meth_data, colWidths=[350, 350])
    meth_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.white),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('PADDING', (0,0), (-1,-1), 10),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(meth_table)
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 11: Technology Stack & Tools
    # =========================================================================
    add_header("Technology Stack & Development Environment")

    tech_data = [
        [
            Paragraph("Category", table_header_style),
            Paragraph("Technologies Used", table_header_style),
            Paragraph("Project Application & Purpose", table_header_style)
        ],
        [
            Paragraph("<b>Programming</b>", table_cell_style),
            Paragraph("Python 3.12, JavaScript (ES6+), SQL, HTML5/CSS3", table_cell_style),
            Paragraph("Backend API logic, ML pipelines, SHAP calculations, and React frontend dashboard UI.", table_cell_style)
        ],
        [
            Paragraph("<b>ML & Data Science</b>", table_cell_style),
            Paragraph("Random Forest, XGBoost, SHAP, Scikit-Learn, Pandas, NumPy", table_cell_style),
            Paragraph("Classification modeling, feature transformation, SHAP TreeExplainer, data manipulation.", table_cell_style)
        ],
        [
            Paragraph("<b>Backend & ORM</b>", table_cell_style),
            Paragraph("FastAPI, Uvicorn, SQLAlchemy ORM, Pydantic v2", table_cell_style),
            Paragraph("High-performance asynchronous REST API server, CORS handling, data schema validation.", table_cell_style)
        ],
        [
            Paragraph("<b>Frontend UI</b>", table_cell_style),
            Paragraph("React 18, Vite, Recharts, Lucide React Icons, Axios", table_cell_style),
            Paragraph("Single Page Application (SPA), executive KPI cards, customer inspection modals, PDF preview.", table_cell_style)
        ],
        [
            Paragraph("<b>Database & Reports</b>", table_cell_style),
            Paragraph("SQLite, MySQL 8.0, PyMySQL, ReportLab Engine", table_cell_style),
            Paragraph("Relational storage for customer profiles, orders, churn predictions, and dynamic PDF reports.", table_cell_style)
        ]
    ]
    tech_table = Table(tech_data, colWidths=[130, 240, 330])
    tech_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('PADDING', (0,0), (-1,-1), 6),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, BG_LIGHT])
    ]))
    story.append(tech_table)
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 12: Sprint Planner – Agile Roadmap
    # =========================================================================
    add_header("Sprint Planner: Agile Development Roadmap")

    sprint_data = [
        [
            Paragraph("<b>SPRINT 1 (WEEKS 1-3) — COMPLETED ✓</b>", card_header_style),
            Paragraph("<b>SPRINT 2 (WEEKS 4-6) — COMPLETED ✓</b>", card_header_style)
        ],
        [
            Paragraph(
                "• <b>Major Tasks:</b> Requirements gathering, dataset cleaning, Random Forest & XGBoost model training, SQLAlchemy schema initialization.<br/>"
                "• <b>Deliverables:</b> Model artifacts (`random_forest_model.joblib`, `preprocessor.joblib`), connected database schemas.<br/>"
                "• <b>Status:</b> 100% Completed & Verified.",
                body_style
            ),
            Paragraph(
                "• <b>Major Tasks:</b> SHAP TreeExplainer integration, dynamic severity root cause engine, ReportLab PDF generation service, FastAPI REST routing.<br/>"
                "• <b>Deliverables:</b> Functional XAI API backend, automated severity-ranked primary drivers, ReportLab PDF engine.<br/>"
                "• <b>Status:</b> 100% Completed & Verified.",
                body_style
            )
        ],
        [
            Paragraph("<b>SPRINT 3 (WEEKS 7-9) — COMPLETED ✓</b>", card_header_style),
            Paragraph("<b>SPRINT 4 (WEEKS 10-12) — ACTIVE 🚀</b>", card_header_style)
        ],
        [
            Paragraph(
                "• <b>Major Tasks:</b> React + Vite Single Page Application, Executive Dashboard, Customer Portfolio Directory, Account Inspection Modal, PDF preview integration.<br/>"
                "• <b>Deliverables:</b> Production-ready web dashboard with live `window.open()` PDF preview.<br/>"
                "• <b>Status:</b> 100% Completed & Deployed.",
                body_style
            ),
            Paragraph(
                "• <b>Major Tasks:</b> End-to-end integration testing, query optimization, governance documentation, final presentation panel preparation.<br/>"
                "• <b>Deliverables:</b> Integrated Decision Support Platform & final presentation documentation.<br/>"
                "• <b>Status:</b> Active Final Phase.",
                body_style
            )
        ]
    ]
    sprint_table = Table(sprint_data, colWidths=[350, 350])
    sprint_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.white),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('PADDING', (0,0), (-1,-1), 8),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(sprint_table)
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 13: Sprint Results & Performance Metrics
    # =========================================================================
    add_header("Sprint Results & Model Performance Metrics")

    metric_cards = [
        [
            Paragraph("<b>94.87%</b>", ParagraphStyle('M1', fontName='Helvetica-Bold', fontSize=22, textColor=LOW_RISK, alignment=TA_CENTER)),
            Paragraph("<b>0.954</b>", ParagraphStyle('M2', fontName='Helvetica-Bold', fontSize=22, textColor=SECONDARY, alignment=TA_CENTER)),
            Paragraph("<b>0.910</b>", ParagraphStyle('M3', fontName='Helvetica-Bold', fontSize=22, textColor=PRIMARY, alignment=TA_CENTER)),
            Paragraph("<b>0.890</b>", ParagraphStyle('M4', fontName='Helvetica-Bold', fontSize=22, textColor=PRIMARY, alignment=TA_CENTER))
        ],
        [
            Paragraph("<b>CLASSIFICATION ACCURACY</b>", ParagraphStyle('L1', fontName='Helvetica-Bold', fontSize=8, textColor=TEXT_MUTED, alignment=TA_CENTER)),
            Paragraph("<b>AUC-ROC SCORE</b>", ParagraphStyle('L2', fontName='Helvetica-Bold', fontSize=8, textColor=TEXT_MUTED, alignment=TA_CENTER)),
            Paragraph("<b>PRECISION SCORE</b>", ParagraphStyle('L3', fontName='Helvetica-Bold', fontSize=8, textColor=TEXT_MUTED, alignment=TA_CENTER)),
            Paragraph("<b>RECALL SCORE</b>", ParagraphStyle('L4', fontName='Helvetica-Bold', fontSize=8, textColor=TEXT_MUTED, alignment=TA_CENTER))
        ]
    ]
    metric_table = Table(metric_cards, colWidths=[175, 175, 175, 175])
    metric_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), BG_LIGHT),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('PADDING', (0,0), (-1,-1), 10),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
    ]))
    story.append(metric_table)
    story.append(Spacer(1, 15))

    deliv_data = [
        [
            Paragraph("<b>Sprint Deliverables Achieved</b>", card_header_style),
            Paragraph("<b>Current Project Operational Status</b>", card_header_style)
        ],
        [
            Paragraph(
                "✔ <b>10,000+ Records Preprocessed:</b> Handled missing value imputation, categorical one-hot encoding, and standard scaling.<br/>"
                "✔ <b>Random Forest & XGBoost Deployed:</b> 100% operational inference pipeline trained on customer telemetry.<br/>"
                "✔ <b>Dynamic Severity Root Causes:</b> Eliminates static text duplication by mathematically ranking top friction vectors.<br/>"
                "✔ <b>Live PDF Preview Integration:</b> Enabled instant browser PDF preview (`window.open(url, '_blank')`) across all dashboard views.",
                body_style
            ),
            Paragraph(
                "• <b>FastAPI REST Backend:</b> 100% operational REST endpoints for authentication, customer directory, model info, and PDF reports.<br/>"
                "• <b>React SPA Frontend:</b> Polished Single Page Application featuring interactive KPI cards, account profile inspection modals, and live PDF preview.<br/>"
                "• <b>Validation Check:</b> All model metrics and PDF outputs verified with zero boundary overflow issues.",
                body_style
            )
        ]
    ]
    deliv_table = Table(deliv_data, colWidths=[350, 350])
    deliv_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.white),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('PADDING', (0,0), (-1,-1), 10),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(deliv_table)
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 14: Expected Outcomes & Conclusion
    # =========================================================================
    add_header("Expected Outcomes & Future Scope")

    out_data = [
        [
            Paragraph("<b>Expected Platform Impact</b>", card_header_style),
            Paragraph("<b>Real-World Applications</b>", card_header_style),
            Paragraph("<b>Scope for Future Scope</b>", card_header_style)
        ],
        [
            Paragraph(
                "• <b>15–20% Churn Reduction:</b> Proactive early warning risk triage enables timely account retention.<br/>"
                "• <b><2 sec Explainability:</b> Instant SHAP feature attributions and automated severity root cause analysis.<br/>"
                "• <b>Actionable Playbooks:</b> Replaces guesswork with automated retention recommendations.",
                body_style
            ),
            Paragraph(
                "• <b>B2B SaaS Enterprises:</b> Subscription retention management and automated customer success workflows.<br/>"
                "• <b>E-Commerce Platforms:</b> Customer drop-off detection, return friction reduction, and win-back offers.<br/>"
                "• <b>Banking & Telecom:</b> Account churn monitoring, deposit retention, and proactive contract renewal.",
                body_style
            ),
            Paragraph(
                "• <b>Real-Time Streaming:</b> Apache Kafka streaming pipeline for instant transaction telemetry ingestion.<br/>"
                "• <b>LLM Decision Summaries:</b> Generative AI natural language executive briefing reports.<br/>"
                "• <b>Multi-Tenant Cloud:</b> Dockerized microservices architecture with AWS/GCP deployment.",
                body_style
            )
        ]
    ]
    out_table = Table(out_data, colWidths=[230, 235, 235])
    out_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.white),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('PADDING', (0,0), (-1,-1), 10),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(out_table)
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 15: References & Academic Bibliography
    # =========================================================================
    add_header("References & Academic Bibliography")

    refs_data = [
        [
            Paragraph("<b>Academic Literature Citations (IEEE Format)</b>", card_header_style)
        ],
        [
            Paragraph(
                "[1] U. G. Joy, K. E. Hoque, M. N. Uddin, L. Chowdhury, and S.-B. Park, \"A Big Data-Driven Hybrid Model for Enhancing Streaming Service Customer Retention Through Churn Prediction Integrated With Explainable AI,\" <i>IEEE Access</i>, vol. 12, pp. 69130–69150, 2024, doi: 10.1109/ACCESS.2024.3401247.<br/><br/>"
                "[2] R. Bhuria and S. Aluvala, \"Predicting Bank Customer Churn: An XGBoost Approach to Enhancing Customer Retention,\" in <i>Proc. 2025 3rd International Conference on Advancement in Computation & Computer Technologies (InCACCT)</i>, IEEE, 2025, doi: 10.1109/InCACCT65424.2025.11011351.<br/><br/>"
                "[3] R. R. Chandan, S. Ramaraj, Sarishma, and P. P. Devi, et al., \"A Novel Machine Learning-Based Early Warning Detection System for Business Customer Churn,\" in <i>Proc. 5th International Conference on Recent Trends in Computer Science and Technology (ICRTCST)</i>, IEEE, 2024, doi: 10.1109/ICRTCST61793.2024.10578489.<br/><br/>"
                "[4] Y. Li and K. Yan, \"Prediction of Bank Credit Customers Churn Based on Machine Learning and Interpretability Analysis,\" <i>Data Science in Finance and Economics</i>, vol. 5, no. 1, pp. 25–42, 2025, doi: 10.3934/DSFE.2025002.",
                body_style
            )
        ]
    ]
    refs_table = Table(refs_data, colWidths=[700])
    refs_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), BG_LIGHT),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('PADDING', (0,0), (-1,-1), 12),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(refs_table)

    doc.build(story)
    print(f"Successfully generated updated 15-page presentation PDF: {pdf_filename}")

if __name__ == "__main__":
    build_pdf_presentation()
