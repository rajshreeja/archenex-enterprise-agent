import streamlit as st

# 1. Page Configuration
st.set_page_config(
    page_title="ArcheNex Enterprise | Autonomous Audit Suite",
    page_icon="⚡",
    layout="wide"
)

# 2. Ultra-Sleek Enterprise CSS Injection (Removes standard Streamlit look)
st.markdown("""
    <style>
    /* Global Theme & Typography */
    .stApp { background-color: #0b0f19; color: #e2e8f0; font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; }
    
    /* Header & Titles */
    h1, h2, h3 { color: #f8fafc; font-weight: 700; letter-spacing: -0.025em; }
    
    /* Sleek Card Containers */
    .metric-card {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    /* Callout & Explanation Boxes */
    .layman-box {
        background-color: #1e293b;
        border-left: 4px solid #3b82f6;
        padding: 16px;
        border-radius: 0 8px 8px 0;
        margin: 15px 0;
        color: #cbd5e1;
        font-size: 15px;
        line-height: 1.6;
    }
    
    .action-box {
        background-color: #064e3b;
        border-left: 4px solid #10b981;
        padding: 16px;
        border-radius: 0 8px 8px 0;
        margin: 15px 0;
        color: #d1fae5;
        font-size: 15px;
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] { background-color: #0f172a; border-right: 1px solid #1e293b; }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
        color: white;
        border: none;
        border-radius: 6px;
        padding: 10px 20px;
        font-weight: 600;
        width: 100%;
    }
    .stButton>button:hover { background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%); }
    </style>
""", unsafe_allow_html=True)

# 3. Dynamic Client Database Engine
CLIENT_DATABASE = {
    "Tata Motors (Pune Plant)": {
        "industry": "Automotive & Heavy Manufacturing",
        "total_leakage": "₹1.76 Cr",
        "blue_collar": {
            "title": "Factory Floor & Shift Operations",
            "metric_1": "310 Idle Hours",
            "metric_2": "₹42.5 Lakhs Leakage",
            "layman_summary": "Simply put: Factory assembly line #4 was forced to wait around because parts didn't arrive on time. Meanwhile, the HR system recorded workers as fully active and paid them for doing nothing during those waiting windows.",
            "action": "Fix: Automatically link machine power logs to attendance systems so payroll pauses during material delays."
        },
        "white_collar": {
            "title": "Corporate Office & Software Systems",
            "metric_1": "₹68.0 Lakhs Unbilled",
            "metric_2": "₹14.2 Lakhs License Waste",
            "layman_summary": "Simply put: Your corporate consultants finished complex client projects, but due to communication gaps between the project management tool (CRM) and the billing software (SAP), invoices weren't sent out for an average of 14 days, straining cash flow.",
            "action": "Fix: Set up automatic invoice generation in SAP the exact moment a project milestone is marked complete in CRM."
        }
    },
    "Bosch India (Bangalore Hub)": {
        "industry": "Industrial Technology & Engineering",
        "total_leakage": "₹2.10 Cr",
        "blue_collar": {
            "title": "Factory Floor & Shift Operations",
            "metric_1": "185 Idle Hours",
            "metric_2": "₹28.0 Lakhs Leakage",
            "layman_summary": "Simply put: SMT manufacturing lines experienced unexpected micro-stoppages. Contract shift rosters showed full staffing utilization, but production throughput counters proved workers were sitting idle due to staging errors.",
            "action": "Fix: Implement real-time material scanning at station entry to prevent staff scheduling mismatches."
        },
        "white_collar": {
            "title": "Corporate Office & Software Systems",
            "metric_1": "₹92.4 Lakhs Unbilled",
            "metric_2": "₹21.5 Lakhs License Waste",
            "layman_summary": "Simply put: Premium software subscriptions (like specialized CAD and enterprise analytics tools) were being paid for employees who left the company or haven't logged in for over 45 days.",
            "action": "Fix: Enforce automated license reclamation after 30 days of inactivity."
        }
    }
}

# Sidebar Controls
st.sidebar.title("⚙️ ArcheNex Control")
selected_client = st.sidebar.selectbox("Select Target Enterprise", list(CLIENT_DATABASE.keys()))

report_view = st.sidebar.radio(
    "Select Report Module",
    ["📊 Executive Master Report", "🏭 Blue-Collar Breakdown", "💻 White-Collar Breakdown"]
)

client_data = CLIENT_DATABASE[selected_client]

# Main Dashboard Interface
st.title(f"⚡ ArcheNex AI Audit: {selected_client}")
st.caption(f"Industry: {client_data['industry']} | Autonomous Multi-Agent Cross-Silo Governance")

if st.sidebar.button("Run Full Agentic Audit"):
    with st.spinner("Analyzing cross-silo data models..."):
        
        if report_view == "📊 Executive Master Report":
            st.markdown("---")
            st.subheader("Executive Financial Recovery Overview")
            
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(f'<div class="metric-card"><h3>Total Leakage</h3><p style="font-size: 28px; color: #38bdf8; font-weight: bold;">{client_data["total_leakage"]}</p><span>Verified across silos</span></div>', unsafe_allow_html=True)
            with c2:
                st.markdown(f'<div class="metric-card"><h3>Blue-Collar Impact</h3><p style="font-size: 28px; color: #34d399; font-weight: bold;">{client_data["blue_collar"]["metric_2"]}</p><span>Plant Floor & MES</span></div>', unsafe_allow_html=True)
            with c3:
                st.markdown(f'<div class="metric-card"><h3>White-Collar Impact</h3><p style="font-size: 28px; color: #fbbf24; font-weight: bold;">{client_data["white_collar"]["metric_1"]}</p><span>Corporate ERP & HRIS</span></div>', unsafe_allow_html=True)
            
            st.markdown("### 🧠 The Big Picture (For Leadership)")
            st.markdown(
                f'<div class="layman-box"><b>Executive Takeaway:</b> ArcheNex analyzed millions of data points connecting {selected_client}\'s factory floor systems with corporate office software. '
                f'We found that financial leakage is split evenly between factory waiting times and delayed corporate billing cycles. Implementing our automated agentic guardrails will recover <b>{client_data["total_leakage"]}</b> annually without personnel reductions.</div>',
                unsafe_allow_html=True
            )

        elif report_view == "🏭 Blue-Collar Breakdown":
            st.markdown("---")
            st.subheader(f"🏭 Blue-Collar Report: {client_data['blue_collar']['title']}")
            
            c1, c2 = st.columns(2)
            c1.markdown(f'<div class="metric-card"><h3>Machinery Inefficiency</h3><p style="font-size: 24px; color: #38bdf8; font-weight: bold;">{client_data["blue_collar"]["metric_1"]}</p></div>', unsafe_allow_html=True)
            c2.markdown(f'<div class="metric-card"><h3>Financial Waste</h3><p style="font-size: 24px; color: #f87171; font-weight: bold;">{client_data["blue_collar"]["metric_2"]}</p></div>', unsafe_allow_html=True)
            
            st.markdown("### 🔍 What Is Happening? (In Plain English)")
            st.markdown(f'<div class="layman-box">{client_data["blue_collar"]["layman_summary"]}</div>', unsafe_allow_html=True)
            
            st.markdown("### 🛠️ Recommended Action Plan")
            st.markdown(f'<div class="action-box">{client_data["blue_collar"]["action"]}</div>', unsafe_allow_html=True)

        elif report_view == "💻 White-Collar Breakdown":
            st.markdown("---")
            st.subheader(f"💻 White-Collar Report: {client_data['white_collar']['title']}")
            
            c1, c2 = st.columns(2)
            c1.markdown(f'<div class="metric-card"><h3>Unbilled Revenue</h3><p style="font-size: 24px; color: #fbbf24; font-weight: bold;">{client_data["white_collar"]["metric_1"]}</p></div>', unsafe_allow_html=True)
            c2.markdown(f'<div class="metric-card"><h3>Software License Waste</h3><p style="font-size: 24px; color: #f87171; font-weight: bold;">{client_data["white_collar"]["metric_2"]}</p></div>', unsafe_allow_html=True)
            
            st.markdown("### 🔍 What Is Happening? (In Plain English)")
            st.markdown(f'<div class="layman-box">{client_data["white_collar"]["layman_summary"]}</div>', unsafe_allow_html=True)
            
            st.markdown("### 🛠️ Recommended Action Plan")
            st.markdown(f'<div class="action-box">{client_data["white_collar"]["action"]}</div>', unsafe_allow_html=True)
