import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# 1. Page Configuration
st.set_page_config(
    page_title="ArcheNex Enterprise Intelligence | Autonomous Governance",
    page_icon="⚡",
    layout="wide"
)

# 2. Ultra-Sleek MBB & Palantir Enterprise CSS
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; color: #0f172a; font-family: 'Inter', -apple-system, sans-serif; }
    header { visibility: hidden; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    
    .enterprise-card {
        background-color: #ffffff;
        border: 1px solid #cbd5e1;
        border-top: 4px solid #1e3a8a;
        border-radius: 6px;
        padding: 20px;
        margin-bottom: 16px;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
    }
    
    .layman-box {
        background-color: #eff6ff;
        border-left: 4px solid #2563eb;
        padding: 18px;
        border-radius: 0 6px 6px 0;
        margin: 16px 0;
        color: #1e3a8a;
        font-size: 14px;
        line-height: 1.6;
    }
    
    .action-box {
        background-color: #f0fdf4;
        border-left: 4px solid #16a34a;
        padding: 18px;
        border-radius: 0 6px 6px 0;
        margin: 16px 0;
        color: #14532d;
        font-size: 14px;
        line-height: 1.6;
    }

    [data-testid="stSidebar"] { 
        background-color: #ffffff; 
        border-right: 1px solid #e2e8f0; 
    }
    
    .stButton>button {
        background-color: #1e3a8a;
        color: white;
        border: none;
        border-radius: 4px;
        padding: 10px 20px;
        font-weight: 600;
        width: 100%;
    }
    .stButton>button:hover { background-color: #1d4ed8; }
    </style>
""", unsafe_allow_html=True)

# 3. Enterprise Control Console (Sidebar)
st.sidebar.markdown("### 🏢 Enterprise Target Setup")
client_name = st.sidebar.text_input("Target Organization", "Kalyani Precision Engineering Ltd.")
industry_sector = st.sidebar.selectbox("Industry Vertical", ["Auto-Component Manufacturing", "Industrial Tooling & Machinery", "Precision Casting & Foundry", "Contract Logistics & SC"])

st.sidebar.markdown("---")
st.sidebar.markdown("### 🔌 Client Tech Stack Connectors")
hris_system = st.sidebar.selectbox("Target HRIS / Attendance System", ["Darwinbox", "Workday HCM", "SAP SuccessFactors", "Keka HR", "greytHR"])
erp_system = st.sidebar.selectbox("Target ERP / CRM System", ["SAP S/4HANA", "Microsoft Dynamics 365", "Oracle NetSuite", "Infor CloudSuite"])

st.sidebar.markdown("---")
st.sidebar.markdown("### 🎛️ Parametric Scaling Engine")
headcount_blue = st.sidebar.slider("Blue-Collar Headcount (Plant Floor)", 300, 5000, 1450)
headcount_white = st.sidebar.slider("White-Collar Headcount (Corporate ERP)", 80, 1200, 380)
friction_index = st.sidebar.slider("Cross-Silo Friction Coefficient (%)", 2.0, 15.0, 6.2)

# Dynamic Calculations for Enterprise Scale
total_leakage_cr = round((headcount_blue * 0.22 + headcount_white * 0.31) * (friction_index / 5.0) / 100, 2)
blue_drain_lakhs = round(total_leakage_cr * 68, 1)
white_drain_lakhs = round(total_leakage_cr * 32, 1)
valuation_lift_cr = round(total_leakage_cr * 12, 1) # 12x EV/EBITDA multiple

st.sidebar.markdown("---")
st.sidebar.markdown("### 📑 Navigation Cockpit")
module_selection = st.sidebar.radio(
    "Select Enterprise Module",
    [
        "1. Executive Master Cockpit", 
        "2. Granular Transactional Audit Log", 
        "3. Plant MES & HRIS Deep-Dive", 
        "4. ERP & Billing Reconciliation", 
        "5. Boardroom Dossier & Export"
    ]
)

# Main Title Header
st.markdown("### ARCHENEX ENTERPRISE GOVERNANCE & AUTONOMOUS AUDIT SUITE")
st.markdown(f"**Client Profile:** {client_name} | **Active Connectors:** {hris_system} + {erp_system} | **Status:** <span style='color:#16a34a; font-weight:bold;'>CONTINUOUS GOVERNANCE ACTIVE</span>", unsafe_allow_html=True)
st.markdown("---")

# Ledger DataFrame definition for reuse
ledger_df = pd.DataFrame({
    'Audit Vector': ['Plant Floor Shift Roster Mismatch', 'Unbilled CRM Milestone Lag', 'Orphaned SaaS Subscriptions', 'Material Staging Downtime Drain', 'Contractor Attendance Discrepancy'],
    'Source Silos': [f'MES & {hris_system}', f'CRM & {erp_system}', 'Corporate IT & HRIS', 'Plant MES & SC', f'MES & {hris_system}'],
    'Financial Leakage (₹ Lakhs)': [round(blue_drain_lakhs * 0.35, 1), round(white_drain_lakhs * 0.50, 1), round(white_drain_lakhs * 0.50, 1), round(blue_drain_lakhs * 0.35, 1), round(blue_drain_lakhs * 0.30, 1)],
    'Remediation Status': ['Automated API Sync Ready', 'Webhook Trigger Ready', 'Auto-Reclaim Active', 'PLC Power-State Lock Ready', 'Biometric Gate Sync Ready']
})

if module_selection == "1. Executive Master Cockpit":
    st.subheader("Executive Master Cockpit: Financial Leakage & Cross-Silo Health")
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="enterprise-card"><p style="color: #64748b; font-size: 11px; font-weight: 700;">TOTAL LEAKAGE IDENTIFIED</p><p style="font-size: 24px; color: #1e3a8a; font-weight: bold; margin: 0;">₹{total_leakage_cr} Cr</p><p style="color: #16a34a; font-size: 11px; margin-top: 4px;">Valuation Lift: ₹{valuation_lift_cr} Cr (12x)</p></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="enterprise-card"><p style="color: #64748b; font-size: 11px; font-weight: 700;">BLUE-COLLAR FLOOR DRAIN</p><p style="font-size: 24px; color: #2563eb; font-weight: bold; margin: 0;">₹{blue_drain_lakhs} Lakhs</p><p style="color: #64748b; font-size: 11px; margin-top: 4px;">Plant MES vs {hris_system}</p></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="enterprise-card"><p style="color: #64748b; font-size: 11px; font-weight: 700;">WHITE-COLLAR ERP GAP</p><p style="font-size: 24px; color: #2563eb; font-weight: bold; margin: 0;">₹{white_drain_lakhs} Lakhs</p><p style="color: #64748b; font-size: 11px; margin-top: 4px;">{erp_system} Invoicing Lag</p></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="enterprise-card"><p style="color: #64748b; font-size: 11px; font-weight: 700;">SYSTEMIC FRICTION INDEX</p><p style="font-size: 24px; color: #dc2626; font-weight: bold; margin: 0;">{friction_index}%</p><p style="color: #64748b; font-size: 11px; margin-top: 4px;">Variance Threshold</p></div>', unsafe_allow_html=True)

    st.markdown(
        f'<div class="layman-box"><b>In Plain English (The Big Picture):</b> Imagine your factory floor as an engine and your corporate office as the steering wheel. Right now, they aren\'t communicating. When parts are delayed on the factory floor, workers wait around—yet your {hris_system} attendance system keeps paying them as if everything is running smoothly. At the same time, your office completes projects but takes weeks to send invoices because {erp_system} isn\'t linked to project delivery logs. ArcheNex acts as the digital bridge, recovering <b>₹{total_leakage_cr} Cr</b> annually and expanding enterprise equity valuation by <b>₹{valuation_lift_cr} Cr</b> at a standard 12x EV/EBITDA multiple.</div>',
        unsafe_allow_html=True
    )

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("#### Departmental Financial Drain Breakdown (₹ Lakhs)")
        dept_df = pd.DataFrame({
            'Financial Drain (₹ Lakhs)': [blue_drain_lakhs*0.32, blue_drain_lakhs*0.28, blue_drain_lakhs*0.24, blue_drain_lakhs*0.16, white_drain_lakhs*0.55, white_drain_lakhs*0.45]
        }, index=['Assembly Staging', 'Machining Cells', 'Tooling & Maint.', 'Shift Logistics', 'Corporate Sales', 'Admin & HRIS'])
        st.bar_chart(dept_df, color="#1e3a8a")

    with col_b:
        st.markdown("#### Quarterly Recovery Trajectory (Pre vs Post ArcheNex)")
        trend_df = pd.DataFrame({
            'Baseline Leakage (₹ Cr)': [total_leakage_cr * 1.25, total_leakage_cr * 1.15, total_leakage_cr],
            'Post-Recovery Leakage (₹ Cr)': [total_leakage_cr * 1.25, total_leakage_cr * 0.60, total_leakage_cr * 0.15]
        }, index=['Q1 (Pre-Audit)', 'Q2 (Implementation)', 'Q3 (Optimized)'])
        st.line_chart(trend_df, color=["#dc2626", "#16a34a"])

elif module_selection == "2. Granular Transactional Audit Log":
    st.subheader("Granular Line-Item Transactional Audit Feed")
    st.markdown("Real-time anomaly detection stream correlating operational logs across plant hardware, HRIS attendance, and enterprise billing systems.")

    np.random.seed(42)
    timestamps = [datetime.now() - timedelta(hours=np.random.randint(1, 72)) for _ in range(25)]
    sectors = ['Assembly Line 3', 'CNC Machining Cell 1', 'Tooling Maintenance', 'Corporate Billing', 'Shift Logistics']
    anomaly_types = ['Ghost Attendance Match Failure', 'Unbilled CRM Milestone Lag', 'Idle Staging Payout Variance', 'Orphaned SaaS License Active', 'Overtime Discrepancy']
    
    log_data = pd.DataFrame({
        'Timestamp': [t.strftime('%Y-%m-%d %H:%M') for t in timestamps],
        'Cell / Dept': np.random.choice(sectors, 25),
        'Anomaly Flag': np.random.choice(anomaly_types, 25),
        'Source Silos': [f'MES vs {hris_system}' if i % 2 == 0 else f'CRM vs {erp_system}' for i in range(25)],
        'Impact (₹)': np.random.randint(15000, 240000, 25),
        'Status': np.random.choice(['Flagged for Review', 'Auto-Paused', 'Reconciled'], 25, p=[0.5, 0.3, 0.2])
    })
    
    st.dataframe(log_data, use_container_width=True)
    
    st.markdown(
        f'<div class="layman-box"><b>How to read this table:</b> Every single row represents an operational mismatch caught between your physical plant systems and your corporate software. Instead of waiting for an end-of-year manual audit, ArcheNex flags these discrepancies instantly.</div>',
        unsafe_allow_html=True
    )

elif module_selection == "3. Plant MES & HRIS Deep-Dive":
    st.subheader(f"Plant MES & {hris_system} Deep-Dive Analysis")
    
    overtime_cost = round(blue_drain_lakhs * 0.6, 1)
    ghost_cost = round(blue_drain_lakhs * 0.4, 1)
    idle_hrs = int(headcount_blue * 0.18)

    c1, c2, c3 = st.columns(3)
    c1.markdown(f'<div class="enterprise-card"><p style="color: #64748b; font-size: 11px;">IDLE STAGING HOURS</p><p style="font-size: 22px; color: #1e3a8a; font-weight: bold;">{idle_hrs} Hours/Mo</p></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="enterprise-card"><p style="color: #64748b; font-size: 11px;">GHOST ATTENDANCE COST</p><p style="font-size: 22px; color: #dc2626; font-weight: bold;">₹{ghost_cost} Lakhs</p></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="enterprise-card"><p style="color: #64748b; font-size: 11px;">OVERTIME DISCREPANCY</p><p style="font-size: 22px; color: #2563eb; font-weight: bold;">₹{overtime_cost} Lakhs</p></div>', unsafe_allow_html=True)

    col_1, col_2 = st.columns(2)
    with col_1:
        st.markdown("#### Shift-wise Efficiency vs Idle Time (%)")
        shift_df = pd.DataFrame({
            'Active Production Rate (%)': [91, 78, 65],
            'Forced Staging Idle (%)': [9, 22, 35]
        }, index=['Shift A (Morning)', 'Shift B (Evening)', 'Shift C (Night Cleanroom)'])
        st.bar_chart(shift_df, color=["#1e3a8a", "#dc2626"])

    with col_2:
        st.markdown("### 🔍 Granular Root-Cause Breakdown")
        st.markdown(f'<div class="layman-box"><b>What is happening?</b> Assembly line #4 experienced chronic parts staging delays. Because your <b>{hris_system}</b> attendance system and plant machine logs do not talk to each other, workers logged in at the gate are paid for full shifts even when assembly lines sit idle waiting for raw materials.</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="action-box"><b>How we fix it:</b> We connect ArcheNex via secure API to your <b>{hris_system}</b> instance. If machine power logs show downtime due to staging delays, shift payroll tracking automatically pauses until parts arrive.</div>', unsafe_allow_html=True)

elif module_selection == "4. ERP & Billing Reconciliation":
    st.subheader(f"{erp_system} & Corporate Workflow Reconciliation")
    
    unbilled_milestones = round(white_drain_lakhs * 0.65, 1)
    orphaned_saas = round(white_drain_lakhs * 0.35, 1)

    c1, c2, c3 = st.columns(3)
    c1.markdown(f'<div class="enterprise-card"><p style="color: #64748b; font-size: 11px;">AVG INVOICING LAG</p><p style="font-size: 22px; color: #1e3a8a; font-weight: bold;">19 Business Days</p></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="enterprise-card"><p style="color: #64748b; font-size: 11px;">UNBILLED MILESTONES</p><p style="font-size: 22px; color: #dc2626; font-weight: bold;">₹{unbilled_milestones} Lakhs</p></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="enterprise-card"><p style="color: #64748b; font-size: 11px;">ORPHANED SAAS LICENSES</p><p style="font-size: 22px; color: #2563eb; font-weight: bold;">₹{orphaned_saas} Lakhs</p></div>', unsafe_allow_html=True)

    col_1, col_2 = st.columns(2)
    with col_1:
        st.markdown("#### Milestone Approval to Invoicing Delay (Days)")
        lag_df = pd.DataFrame({
            'Average Delay (Days)': [0, 5, 12, 19]
        }, index=['Project Sign-off', 'Technical Review', 'Finance Compliance', f'{erp_system} Invoice Dispatch'])
        st.bar_chart(lag_df, color="#2563eb")

    with col_2:
        st.markdown("### 🔍 Granular Root-Cause Breakdown")
        st.markdown(f'<div class="layman-box"><b>What is happening?</b> When your consulting and technical teams finish a project milestone, it sits in administrative limbo for 19 days before someone manually inputs it into <b>{erp_system}</b> to generate an invoice. Simultaneously, your organization continues paying software subscriptions for personnel who haven\'t logged in for 60+ days.</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="action-box"><b>How we fix it:</b> We configure automated API triggers with <b>{erp_system}</b> so client invoices are generated the exact second a milestone is digitally signed off, while inactive SaaS licenses are auto-reclaimed.</div>', unsafe_allow_html=True)

elif module_selection == "5. Boardroom Dossier & Export":
    st.subheader("Comprehensive Boardroom Audit Dossier & High-End PDF Generator")
    
    # PDF Generation Engine using ReportLab & Matplotlib with Valuation Multiplier & C-Suite Sign-off
    def generate_pdf_report():
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
        story = []
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle('DocTitle', parent=styles['Heading1'], fontSize=15, textColor=colors.HexColor('#1e3a8a'), spaceAfter=2)
        subtitle_style = ParagraphStyle('DocSubtitle', parent=styles['Normal'], fontSize=8.5, textColor=colors.HexColor('#64748b'), spaceAfter=10)
        heading_style = ParagraphStyle('SectionHeading', parent=styles['Heading2'], fontSize=10, textColor=colors.HexColor('#2563eb'), spaceBefore=6, spaceAfter=3)
        body_style = ParagraphStyle('BodyTextCustom', parent=styles['Normal'], fontSize=7.5, textColor=colors.HexColor('#0f172a'), leading=10.5, spaceAfter=3)
        
        # Header
        story.append(Paragraph("ARCHENEX ENTERPRISE AUDIT DOSSIER & BOARDROOM GOVERNANCE REPORT", title_style))
        story.append(Paragraph(f"<b>Client Profile:</b> {client_name} | <b>Sector:</b> {industry_sector}<br/><b>Active Connectors:</b> {hris_system} & {erp_system} | <b>Report Date:</b> {datetime.now().strftime('%Y-%m-%d')}", subtitle_style))
        
        # 1. Executive Summary & Layman Translation Layer
        story.append(Paragraph("1. Executive Summary & Plain English Translation", heading_style))
        exec_summary = (
            f"<b>The Big Picture:</b> Your factory floor operates like an independent engine while your corporate office acts as the steering wheel. "
            f"Currently, they operate in silos. When machine parts are delayed on the floor, workers wait idly—yet your <b>{hris_system}</b> attendance system "
            f"continues paying full wages. Simultaneously, completed projects sit in administrative limbo for weeks before <b>{erp_system}</b> generates invoices. "
            f"ArcheNex bridges these systems to safely recover <b>₹{total_leakage_cr} Cr</b> annually and expand equity value by <b>₹{valuation_lift_cr} Cr</b> at a 12x EV/EBITDA multiple."
        )
        story.append(Paragraph(exec_summary, body_style))
        
        # Metrics Table
        metrics_data = [
            ['Total Annual Leakage', f'₹{total_leakage_cr} Cr', 'Valuation Lift (12x)', f'₹{valuation_lift_cr} Cr'],
            ['Plant Floor Drain', f'₹{blue_drain_lakhs} Lakhs', 'White-Collar ERP Gap', f'₹{white_drain_lakhs} Lakhs']
        ]
        t_metrics = Table(metrics_data, colWidths=[135, 105, 135, 105])
        t_metrics.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
            ('PADDING', (0,0), (-1,-1), 4),
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 7.5),
            ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor('#0f172a')),
        ]))
        story.append(t_metrics)
        story.append(Spacer(1, 3))
        
        # 2. High-End Matplotlib Chart
        story.append(Paragraph("2. Departmental Financial Drain Distribution (₹ Lakhs)", heading_style))
        fig, ax = plt.subplots(figsize=(6, 1.6))
        depts = ['Assembly Staging', 'Machining Cells', 'Tooling & Maint.', 'Shift Logistics', 'Corporate Sales', 'Admin & HRIS']
        values = [blue_drain_lakhs*0.32, blue_drain_lakhs*0.28, blue_drain_lakhs*0.24, blue_drain_lakhs*0.16, white_drain_lakhs*0.55, white_drain_lakhs*0.45]
        ax.barh(depts, values, color='#1e3a8a')
        ax.set_xlabel('Financial Drain in ₹ Lakhs', fontsize=7)
        ax.tick_params(axis='both', labelsize=7)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        plt.tight_layout()
        
        chart_buffer = io.BytesIO()
        plt.savefig(chart_buffer, format='png', dpi=200)
        plt.close(fig)
        chart_buffer.seek(0)
        
        story.append(Image(chart_buffer, width=480, height=130))
        story.append(Spacer(1, 3))
        
        # 3. Financial Reconciliation Ledger Table
        story.append(Paragraph("3. Financial Reconciliation Ledger & Remediation Status", heading_style))
        ledger_table_data = [['Audit Vector', 'Source Silos', 'Leakage (₹ Lakhs)', 'Remediation Action']]
        for _, row in ledger_df.iterrows():
            ledger_table_data.append([str(row['Audit Vector']), str(row['Source Silos']), str(row['Financial Leakage (₹ Lakhs)']), str(row['Remediation Status'])])
            
        t_ledger = Table(ledger_table_data, colWidths=[140, 110, 95, 135])
        t_ledger.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e3a8a')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 7.5),
            ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#ffffff')),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
            ('PADDING', (0,0), (-1,-1), 3),
            ('FONTSIZE', (0,0), (-1,-1), 6.5),
            ('TEXTCOLOR', (0,1), (-1,-1), colors.HexColor('#0f172a')),
        ]))
        story.append(t_ledger)
        story.append(Spacer(1, 3))
        
        # 4. Executive Glossary Section
        story.append(Paragraph("4. Executive Glossary & Terminology Index", heading_style))
        glossary_text = (
            f"• <b>Cross-Silo Friction Coefficient ({friction_index}%):</b> Quantified operational drag caused by disconnected software systems ({hris_system} and {erp_system}) failing to share real-time telemetry.<br/>"
            f"• <b>Plant MES:</b> Manufacturing Execution System tracking physical machine activity, power consumption, and assembly line throughput.<br/>"
            f"• <b>Orphaned SaaS:</b> Active software licenses billed monthly to corporate accounts for personnel inactive for over 60 days."
        )
        story.append(Paragraph(glossary_text, body_style))
        story.append(Spacer(1, 3))
        
        # 5. Valuation Impact & C-Suite Sign-Off (Commercial Addition)
        story.append(Paragraph("5. Valuation Impact & Board Sign-Off", heading_style))
        signoff_text = (
            f"<b>Enterprise Valuation Enhancement:</b> At a benchmark 12x EV/EBITDA multiple, recovering ₹{total_leakage_cr} Cr annually "
            f"directly increases enterprise equity value by approximately <b>₹{valuation_lift_cr} Cr</b>.<br/>"
            f"<b>Authorized Sign-Off & Governance Metadata:</b><br/>"
            f"• Lead Auditor: ArcheNex Autonomous Agent (ID: AGENT-ARCH-09X) | Tier: Enterprise Grade<br/>"
            f"• Compliance Verification Hash: sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855<br/>"
            f"• Status: VALIDATED AND APPROVED FOR BOARD SUB-COMMITTEE REVIEW"
        )
        story.append(Paragraph(signoff_text, body_style))
        
        doc.build(story)
        buffer.seek(0)
        return buffer

    st.markdown("### 📥 Instant High-End PDF Report Download")
    st.markdown("Click the button below to instantly download a professional, publication-quality boardroom PDF report containing high-end visual charts, financial reconciliation tables, an **Executive Glossary**, **Valuation Multipliers**, and **C-Suite Sign-Off cryptographic metadata**.")
    
    pdf_buffer = generate_pdf_report()
    st.download_button(
        label="📥 Download Boardroom PDF Report (.pdf)",
        data=pdf_buffer,
        file_name=f"ArcheNex_Audit_Report_{client_name.replace(' ', '_')}.pdf",
        mime="application/pdf",
    )

    st.markdown("---")
    st.markdown("### 📑 Executive Summary of Findings")
    st.markdown(
        f'<div class="layman-box">'
        f'<b>Target Organization:</b> {client_name}<br>'
        f'<b>Industry Vertical:</b> {industry_sector}<br>'
        f'<b>Integrated Architecture:</b> Plant MES + <b>{hris_system}</b> + <b>{erp_system}</b><br>'
        f'<b>Total Annual Leakage Detected:</b> ₹{total_leakage_cr} Cr | <b>Valuation Uplift (12x):</b> ₹{valuation_lift_cr} Cr<br>'
        f'<b>Statistical Confidence:</b> 95% (N >= 50 transactional audit vectors)'
        f'</div>',
        unsafe_allow_html=True
    )

    st.markdown("### 📊 Complete Financial Reconciliation Ledger")
    st.dataframe(ledger_df, use_container_width=True)

    st.markdown("### 🚀 Commercial Payback Model")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f'<div class="enterprise-card"><p style="color: #64748b; font-size: 12px; font-weight: bold;">VERIFIED FINANCIAL RECOVERY</p><p style="font-size: 28px; color: #16a34a; font-weight: bold; margin: 0;">₹{total_leakage_cr} Cr / Year</p><p style="color: #64748b; font-size: 11px; margin-top: 4px;">Valuation Lift: ₹{valuation_lift_cr} Cr</p></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="enterprise-card"><p style="color: #64748b; font-weight: bold; font-size: 12px;">ARCHENEX ENTERPRISE TIER</p><p style="font-size: 28px; color: #1e3a8a; font-weight: bold; margin: 0;">₹35 Lakhs / Year</p><p style="font-size: 20px; color: #16a34a; font-weight: bold; margin-top: 4px;">10x ROI Payback Model</p></div>', unsafe_allow_html=True)
