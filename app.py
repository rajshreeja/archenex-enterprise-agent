"""ArcheNex Enterprise Intelligence: Streamlit app (v3)."""
import os
import sys
import streamlit as st
import pandas as pd

# Standard package import (works automatically once setup.py is added)
import archenex.agent as ag
import hashlib
import html
import io
import json
import os
import zipfile

import pandas as pd
import streamlit as st

from archenex import agent as ag
from archenex import auth, charts, insights as ins, mapping as mp, pipeline, store
from archenex import detectors as dt
from archenex.connectors import build_connectors, read_table
from archenex.demo_data import make_demo, templates
from archenex.dispatch import send
from archenex.report import build_pdf

st.set_page_config(page_title="ArcheNex Enterprise Intelligence", page_icon="⚡", layout="wide")
st.markdown("""
<style>
.stApp { background-color:#f8fafc; color:#0f172a; }
[data-testid="stSidebar"] { background-color:#ffffff; border-right:1px solid #e2e8f0; }
[data-testid="stMetric"] { background:#ffffff; border:1px solid #cbd5e1; border-top:4px solid #1e3a8a;
  border-radius:6px; padding:14px 16px; box-shadow:0 1px 3px rgba(0,0,0,.05); }
.plain { background:#eff6ff; border-left:4px solid #2563eb; padding:14px 18px; border-radius:0 6px 6px 0;
  color:#1e3a8a; font-size:14px; line-height:1.6; margin:12px 0; }
.action { background:#f0fdf4; border-left:4px solid #16a34a; padding:14px 18px; border-radius:0 6px 6px 0;
  color:#14532d; font-size:14px; line-height:1.6; margin:12px 0; }
.insight { background:#fff; border:1px solid #e2e8f0; border-left:4px solid #1e3a8a; padding:10px 16px;
  border-radius:0 6px 6px 0; margin:8px 0; font-size:14px; }
.stButton>button, .stDownloadButton>button { background:#1e3a8a; color:#fff; border:none; border-radius:4px; font-weight:600; }
.stButton>button:hover, .stDownloadButton>button:hover { background:#1d4ed8; color:#fff; }
</style>
""", unsafe_allow_html=True)


# ----------------------------------------------------------------------- helpers
def _secret(name, default=None):
    try:
        v = st.secrets.get(name, default)
        return v
    except Exception:
        return default


def plot(fig, key=None):
    if fig is None:
        return
    try:
        st.plotly_chart(fig, width="stretch", key=key)
    except TypeError:                       # older Streamlit
        st.plotly_chart(fig, use_container_width=True, key=key)


def _users():
    u = _secret("users")
    if not u:
        return None
    try:
        return {k: dict(v) for k, v in dict(u).items()}
    except Exception:
        return None


def login_gate():
    """Returns (role, user). Open demo mode if nothing is configured."""
    users, legacy = _users(), _secret("APP_PASSWORD")
    if not users and not legacy:
        return "admin", "demo-user", True
    if st.session_state.get("auth"):
        return (*st.session_state["auth"], False)
    st.markdown("### ArcheNex Enterprise Intelligence")
    uname = st.text_input("User name") if users else ""
    pw = st.text_input("Password" if users else "Access code", type="password")
    if st.button("Sign in"):
        res = auth.authenticate(uname, pw, users, legacy)
        if res:
            st.session_state["auth"] = res
            st.rerun()
        st.error("Incorrect credentials.")
    st.stop()


ROLE, USER, OPEN_MODE = login_gate()


@st.cache_data(show_spinner="Generating synthetic demo data…")
def load_demo():
    return make_demo()


def data_sig(data: dict) -> str:
    h = hashlib.sha256()
    for k in sorted(data):
        df = data[k]
        h.update(k.encode())
        h.update(str(len(df)).encode())
        h.update(pd.util.hash_pandas_object(df.head(2000), index=False).values.tobytes())
        h.update(pd.util.hash_pandas_object(df.tail(2000), index=False).values.tobytes())
    return h.hexdigest()


# ----------------------------------------------------------------------- sidebar
sb = st.sidebar
sb.markdown("### Engagement")
client_name = sb.text_input("Client organisation", "Demo Precision Engineering Pvt Ltd (synthetic)")
sector = sb.selectbox("Industry vertical", ["Auto-Component Manufacturing", "Industrial Tooling & Machinery",
                                            "Precision Casting & Foundry", "Contract Logistics & SC",
                                            "Pharma & Chemicals", "Textiles & Apparel", "Other manufacturing"])
hris = sb.selectbox("HRIS / attendance system", ["Darwinbox", "Workday HCM", "SAP SuccessFactors", "Keka HR", "greytHR", "Other"])
erp = sb.selectbox("ERP / finance system", ["SAP S/4HANA", "Microsoft Dynamics 365", "Oracle NetSuite", "Tally Prime",
                                            "Zoho Books", "Infor CloudSuite", "Other"])
reviewer = sb.text_input("Reviewer name (recorded in audit trail)", "" if OPEN_MODE else USER)
source = sb.radio("Data source", ["Synthetic demo data", "Upload files", "Live connectors"])
is_demo = source == "Synthetic demo data"
sb.caption(f"Signed in as **{USER}** · role **{ROLE}**" + (" · OPEN DEMO MODE" if OPEN_MODE else ""))

cfg = json.loads(json.dumps(dt.DEFAULT_CONFIG))
with sb.expander("Assumptions (editable)", expanded=False):
    editable = auth.can(ROLE, "admin")
    if not editable:
        st.caption("Only admins can change assumptions.")
    cfg["cost_of_capital_pct"] = st.number_input("Cost of capital (%)", 0.0, 40.0, cfg["cost_of_capital_pct"], 0.5, disabled=not editable)
    cfg["overtime_multiplier"] = st.number_input("Overtime pay multiplier", 1.0, 3.0, cfg["overtime_multiplier"], 0.25, disabled=not editable)
    cfg["invoice_grace_days"] = st.number_input("Invoice grace period (days)", 0, 60, cfg["invoice_grace_days"], disabled=not editable)
    cfg["saas_inactive_days"] = st.number_input("SaaS inactivity threshold (days)", 7, 365, cfg["saas_inactive_days"], disabled=not editable)
    cfg["low_utilisation_pct"] = st.number_input("Under-utilisation threshold (%)", 10.0, 100.0, cfg["low_utilisation_pct"], 5.0, disabled=not editable)
    cfg["weekly_ot_cap_hours"] = st.number_input("Weekly overtime cap (hours)", 4.0, 30.0, cfg["weekly_ot_cap_hours"], 1.0, disabled=not editable)
    cfg["dup_window_days"] = st.number_input("Duplicate-payment window (days)", 0, 30, cfg["dup_window_days"], disabled=not editable)
    cfg["avoidable_reasons"] = st.text_input("Avoidable downtime reasons (comma-separated)", cfg["avoidable_reasons"], disabled=not editable)
    cfg["ev_ebitda_multiple"] = st.number_input("EV/EBITDA multiple (illustrative)", 1.0, 40.0, cfg["ev_ebitda_multiple"], 0.5, disabled=not editable)
    cfg["annual_fee_inr"] = st.number_input("Annual platform fee (₹)", 0, 100_000_000, cfg["annual_fee_inr"], 100_000, disabled=not editable)
    st.caption("Share of each leak realistically recoverable (planning assumptions until a pilot measures real recovery):")
    for k in list(cfg["realisation_pct"]):
        cfg["realisation_pct"][k] = st.slider(k.replace("_", " ").title(), 0.0, 100.0, float(cfg["realisation_pct"][k]), 5.0,
                                              key=f"real_{k}", disabled=not editable)

# -------------------------------------------------------------------------- data
if is_demo:
    data = load_demo()
else:
    data = st.session_state.setdefault("uploaded_data", {})

findings, notes, summary, fingerprint = [], [], None, ""
if data:
    key = (source, data_sig(data), json.dumps(cfg, sort_keys=True))
    if st.session_state.get("run_key") != key:
        f_, n_ = dt.run_all(data, cfg)
        st.session_state.update(run_key=key, run_findings=f_, run_notes=n_,
                                run_summary=dt.summarise(f_, cfg) if f_ else None)
    findings, notes, summary = st.session_state["run_findings"], st.session_state["run_notes"], st.session_state["run_summary"]
data_basis = "SYNTHETIC DEMO DATA" if is_demo else ("Live connectors" if source == "Live connectors" else "Client-supplied files")
if findings:
    fingerprint, _canon = dt.build_fingerprint(client_name, data_basis, data, cfg, findings)

PAGES = ["0. Connect & Data", "1. Executive Cockpit", "2. Deep Dives", "3. Audit Log", "4. Action Queue",
         "5. Copilot", "6. What-if Scenarios", "7. History & Monitoring", "8. Report & Verify"]
page = sb.radio("Module", PAGES, index=1 if findings else 0)

st.markdown("### ARCHENEX ENTERPRISE GOVERNANCE & AUDIT SUITE")
status = ("<span style='color:#b45309;font-weight:bold;'>DEMO MODE</span>" if is_demo else
          "<span style='color:#16a34a;font-weight:bold;'>CLIENT DATA LOADED</span>" if findings else
          "<span style='color:#64748b;font-weight:bold;'>AWAITING DATA</span>")
st.markdown(f"**Client:** {html.escape(client_name)} &nbsp;|&nbsp; **Exports from:** {html.escape(hris)} + {html.escape(erp)} "
            f"&nbsp;|&nbsp; **Status:** {status}", unsafe_allow_html=True)
if is_demo:
    st.warning("SYNTHETIC DEMO DATA: every number on screen comes from invented data and is illustrative only. "
               "Choose 'Upload files' or 'Live connectors' in the sidebar to analyse real data.")
st.markdown("---")


def get(key):
    return next((f for f in findings if f.key == key and len(f.evidence)), None)


def need_data():
    st.info("No analysable data yet. Open **0. Connect & Data**.")
    st.stop()


# ============================================================== 0. CONNECT & DATA
if page == PAGES[0]:
    st.subheader("Connect & Data")
    st.markdown("ArcheNex reads from **files** (any column names; you map them once and it remembers), from a "
                "**read-only SQL** database or replica, or from a **REST API**. It never writes back to your systems.")
    if is_demo:
        st.success("Using the built-in synthetic dataset (7 data sources, 9 audit rules).")
        zbuf = io.BytesIO()
        with zipfile.ZipFile(zbuf, "w", zipfile.ZIP_DEFLATED) as z:
            for name, df in data.items():
                z.writestr(f"demo_{name}.csv", df.to_csv(index=False))
        st.download_button("Download the demo dataset as CSV files (.zip)", zbuf.getvalue(), file_name="archenex_demo_data.zip", mime="application/zip")
    elif source == "Upload files":
        up = st.session_state.setdefault("uploaded_data", {})
        st.markdown("Upload any of the seven files. Each rule runs as soon as its inputs are present.")
        for name, label in dt.DATASET_LABELS.items():
            f = st.file_uploader(f"{label}  ·  `{name}`", type=["csv", "xlsx", "xls"], key=f"up_{name}")
            if f is not None:
                try:
                    st.session_state[f"raw_{name}"] = read_table(f.name, f.getvalue())
                except Exception as e:
                    st.error(f"Could not read {f.name}: {e}")
            raw = st.session_state.get(f"raw_{name}")
            if raw is None:
                continue
            cols = [str(c) for c in raw.columns]
            sig = hashlib.md5("|".join(cols).encode()).hexdigest()[:6]
            saved = store.load_mapping(client_name, name)
            sug = mp.suggest_mapping(name, cols)
            m = {}
            need = mp.unmapped_required(name, {**sug, **{k: v for k, v in saved.items() if v in cols}})
            with st.expander(f"Column mapping · {label} · {len(raw):,} rows", expanded=bool(need)):
                st.caption("Match your column names to ArcheNex fields. Suggestions are pre-filled; confirm them once.")
                for fld in dt.REQUIRED[name]:
                    default = saved.get(fld) if saved.get(fld) in cols else sug.get(fld)
                    opts = ["(none)"] + cols
                    idx = opts.index(default) if default in opts else 0
                    pick = st.selectbox(fld, opts, index=idx, key=f"map_{name}_{fld}_{sig}",
                                        help=("Optional: defaults to empty if you have none." if fld in mp.SAFE_DEFAULTS.get(name, {}) else None))
                    m[fld] = None if pick == "(none)" else pick
            missing = mp.unmapped_required(name, m)
            if missing:
                st.error(f"{label}: still need a column for {', '.join(missing)}.")
                up.pop(name, None)
            else:
                up[name] = mp.apply_mapping(raw, name, m)
                st.success(f"{label}: {len(up[name]):,} rows ready.")
                if auth.can(ROLE, "reviewer") and st.button("Remember this mapping for this client", key=f"savemap_{name}_{sig}"):
                    store.upsert_client(client_name, sector)
                    store.save_mapping(client_name, name, m)
                    st.toast("Mapping saved.")
        if up and st.button("Clear uploaded data"):
            st.session_state["uploaded_data"] = {}
            for name in dt.REQUIRED:
                st.session_state.pop(f"raw_{name}", None)
            st.rerun()
    else:
        st.markdown("Paste a connections file (JSON) or set `CONNECTIONS` in Secrets. Credentials belong in Secrets / environment "
                    "variables and are referenced as `${NAME}`; never paste a password here.")
        cfg_text = st.text_area("Connections JSON", value=_secret("CONNECTIONS", "") or "", height=220,
                                placeholder=open("connections.example.json").read() if os.path.exists("connections.example.json") else "")
        c1, c2 = st.columns(2)
        conns = {}
        try:
            conns = build_connectors(cfg_text) if cfg_text.strip() else {}
        except Exception as e:
            st.error(f"Config problem: {e}")
        if conns and auth.can(ROLE, "admin"):
            if c1.button("Test connections"):
                for n, cn in conns.items():
                    ok, msg = cn.test()
                    (st.success if ok else st.error)(f"{n}: {msg}")
            if c2.button("Pull data now"):
                with st.spinner("Reading from client systems…"):
                    d_, n_ = pipeline.ingest(conns, client_name)
                st.session_state["uploaded_data"] = d_
                for n in n_:
                    st.caption(n)
                st.rerun()
        elif conns:
            st.info("Only admins can test or pull from live connections.")
        with st.expander("Example connections file"):
            st.code(open("connections.example.json").read() if os.path.exists("connections.example.json") else "{}", language="json")

    st.markdown("#### Required file formats")
    st.caption("Download templates, or use your own exports and map the columns above.")
    tpl = templates()
    cols = st.columns(4)
    for i, (name, df) in enumerate(tpl.items()):
        cols[i % 4].download_button(f"template_{name}.csv", df.to_csv(index=False).encode("utf-8"),
                                    file_name=f"template_{name}.csv", mime="text/csv", key=f"tpl_{name}")
    if data:
        st.markdown("#### Loaded data")
        for name, df in data.items():
            st.markdown(f"**{dt.DATASET_LABELS[name]}**: {len(df):,} rows")
            st.dataframe(df.head(6), hide_index=True)
    for n in notes:
        st.caption(f"ℹ️ {n}")
    st.stop()

if not findings:
    need_data()

# ============================================================ 1. EXECUTIVE COCKPIT
if page == PAGES[1]:
    st.subheader("Executive Cockpit: financial leakage found in your data")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Identified annual leakage", dt.inr(summary["identified_annual"]), help="Primary rules, scaled from the data window to 12 months.")
    c2.metric("Realistically addressable", dt.inr(summary["addressable_annual"]), help="Identified × realisation rate per rule (planning assumptions).")
    c3.metric("Return on platform fee", f"{summary['roi_multiple']:.1f}x / yr",
              delta=(f"payback {summary['payback_months']:.1f} months" if summary["payback_months"] != float("inf") else None), delta_color="off")
    c4.metric("One-time cash to release", dt.inr(summary["one_time_cash_release"] + summary["one_time_recovery"]),
              help="Unbilled milestones + recoverable duplicate payments. Not counted as annual savings.")

    st.markdown("#### What the data says")
    for it in ins.headline_insights(findings, summary, cfg):
        st.markdown(f"<div class='insight'><b>{html.escape(it['headline'])}</b><br>{html.escape(it['so_what'])} "
                    f"<i>Owner: {html.escape(it['owner'])}.</i></div>", unsafe_allow_html=True)
    left, right = st.columns(2)
    with left:
        plot(charts.waterfall(findings, cfg, summary), "wf")
    with right:
        plot(charts.sankey(findings, cfg), "sk")
    plot(charts.weekly_trend(findings), "tr")
    plot(charts.treemap(findings, cfg), "tm")
    with st.expander("How these numbers are built, and their limits"):
        for f in findings:
            st.markdown(f"**{f.title}**: {f.method}")
            if f.caveat:
                st.caption(f.caveat)
    for n in notes:
        st.caption(f"ℹ️ {n}")

# ================================================================== 2. DEEP DIVES
elif page == PAGES[2]:
    st.subheader("Deep dives")
    t1, t2, t3, t4 = st.tabs(["Plant: machines × people", "Finance: billing & payables", "People & payroll", "IT licences"])
    with t1:
        idle, ghost, ot, cap = get("idle_staging"), get("ghost_attendance"), get("overtime_underutil"), get("overtime_cap_breach")
        if not (idle or ghost or ot or cap):
            st.info("Upload the attendance and machine-log files to enable this view.")
        if idle:
            a, b = st.columns(2)
            with a:
                plot(charts.heatmap(idle), "hm")
            with b:
                plot(charts.pareto(idle, "cell"), "pa_idle")
            hot = ins.compound_hotspots([f for f in findings if f.tier == "primary"])
            if len(hot):
                st.markdown("**Compound hotspots**: cells that carry cost in several rules at once")
                show = hot.copy()
                for c_ in show.columns:
                    if c_ not in ("cell", "rules_hit"):
                        show[c_] = show[c_].map(dt.inr)
                st.dataframe(show, hide_index=True)
        if ghost:
            plot(charts.bar_by(ghost, "cell", charts.RED), "gh")
            st.caption(ghost.caveat)
        if ot:
            plot(charts.bar_by(ot, "cell", charts.BLUE), "ot")
            st.caption(ot.caveat)
        if cap:
            plot(charts.pareto(cap, "cell"), "cap")
    with t2:
        ms, dup = get("milestone_delay"), get("duplicate_payments")
        if not (ms or dup):
            st.info("Upload the milestones and/or vendor-invoice files to enable this view.")
        if ms:
            st.metric("Value-weighted invoicing delay", f"{ms.extra['value_weighted_delay_days']:.0f} days beyond grace")
            plot(charts.milestone_bubble(ms), "mb")
            st.dataframe(ms.evidence.sort_values("value_inr", ascending=False).head(10)[["project", "client", "value_inr", "status", "lag_days"]], hide_index=True)
        if dup:
            plot(charts.pareto(dup, "vendor"), "dup")
            st.dataframe(dup.evidence[["vendor", "invoice_id", "impact_inr", "basis"]].head(15), hide_index=True)
            st.caption(dup.caveat)
    with t3:
        pe, fr = get("payroll_after_exit"), get("flight_risk")
        if not (pe or fr):
            st.info("Upload the employee master and payroll files to enable this view.")
        if pe:
            plot(charts.bar_by(pe, "department", charts.RED), "pe")
            st.dataframe(pe.evidence[["employee_id", "department", "months_after_exit", "impact_inr"]].head(15), hide_index=True)
            st.caption(pe.caveat)
        if fr:
            st.markdown("##### Secondary view: retention watch-list")
            plot(charts.risk_scatter(fr), "fr")
            st.caption(fr.caveat)
    with t4:
        sa = get("orphaned_saas")
        if sa:
            plot(charts.pareto(sa, "app"), "sa")
            st.dataframe(sa.evidence[["app", "user_email", "monthly_cost_inr", "days_inactive", "status"]].head(15), hide_index=True)
        else:
            st.info("Upload the SaaS licence file to enable this view.")

# ================================================================= 3. AUDIT LOG
elif page == PAGES[3]:
    st.subheader("Audit Log: every flagged line item")
    st.markdown("Each row is a real record from the supplied data that tripped a rule. Nothing here is simulated.")
    log = pd.concat([f.evidence[dt._STD].assign(rule=f.title) for f in findings if len(f.evidence)], ignore_index=True)
    fc1, fc2 = st.columns([2, 1])
    picked = fc1.multiselect("Rule", sorted(log["rule"].unique()), default=sorted(log["rule"].unique()))
    min_imp = fc2.number_input("Minimum impact (₹)", 0, 10_000_000, 0, 1000)
    view = log[log["rule"].isin(picked) & (log["impact_inr"] >= min_imp)].sort_values("impact_inr", ascending=False)
    view = view[["rule", "date", "where", "detail", "impact_inr"]]
    st.caption(f"{len(view):,} line items · {dt.inr(view['impact_inr'].sum())} observed in the data window (before annualisation)")
    st.dataframe(view.head(5000), hide_index=True)
    st.download_button("Download filtered log (CSV)", view.to_csv(index=False).encode("utf-8"), file_name="archenex_audit_log.csv", mime="text/csv")

# ============================================================== 4. ACTION QUEUE
elif page == PAGES[4]:
    st.subheader("Action Queue: recommended actions need human approval")
    st.markdown("<div class='plain'>ArcheNex recommends; a person decides. Every decision is written to a tamper-evident log. "
                "ArcheNex does <b>not</b> change payroll, HRIS or ERP data; approved actions are handed to the owning team.</div>",
                unsafe_allow_html=True)
    actions = ag.recommend_actions(findings, cfg) + st.session_state.get("copilot_proposals", [])
    decided = store.decisions_for(client_name)
    who = reviewer.strip() or USER
    can_decide = auth.can(ROLE, "reviewer")
    if not can_decide:
        st.info("Your role is viewer: you can read actions but not decide on them.")
    webhook, wkind = _secret("WEBHOOK_URL"), _secret("WEBHOOK_KIND", "slack")
    dry = st.toggle("Dry-run dispatch (show the message, do not send)", value=True, help="Needs WEBHOOK_URL in Secrets to send for real.")

    for a in actions:
        with st.container(border=True):
            st.markdown(f"**{a['title']}**" + ("  ·  _proposed by Copilot_" if a.get("source") == "copilot" else ""))
            st.caption(f"Owner: {a['owner']} · Estimated impact: {dt.inr(a['impact_inr_annual'])} / yr")
            st.write(a["detail"])
            d = decided.get(a["id"])
            if d:
                st.info(f"Decision recorded: **{d}**")
                if d == "Approve" and can_decide and st.button("Send to owner", key=f"send_{a['id']}"):
                    out = send(a, client_name, who, webhook, wkind, dry_run=dry or not webhook)
                    store.append_audit(client_name, who, ROLE, a["id"], a["title"], "Dispatched (dry-run)" if out["dry_run"] else "Dispatched", "")
                    st.json(out["payload"]) if out["dry_run"] else st.success(f"Sent (HTTP {out.get('status')}).")
            elif can_decide:
                b1, b2, b3, _ = st.columns([1, 1, 1, 4])
                note = st.text_input("Note (optional)", key=f"note_{a['id']}", label_visibility="collapsed", placeholder="Note (optional)")
                for col, label in ((b1, "Approve"), (b2, "Reject"), (b3, "Defer")):
                    if col.button(label, key=f"{label}_{a['id']}"):
                        store.upsert_client(client_name, sector)
                        store.append_audit(client_name, who, ROLE, a["id"], a["title"], label, note)
                        st.rerun()

    st.markdown("#### Decision audit trail")
    trail = pd.DataFrame(store.list_audit(client_name))
    if len(trail):
        st.dataframe(trail[["ts", "reviewer", "role", "action", "decision", "note", "hash"]], hide_index=True)
        st.download_button("Download audit trail (CSV)", trail.to_csv(index=False).encode("utf-8"), file_name="archenex_decision_trail.csv", mime="text/csv")
    ok, msg = store.verify_chain()
    (st.success if ok else st.error)(msg)
    st.caption(f"Stored in {store.DB_PATH}. On a hosted demo this file can be reset on restart; use a persistent volume in production.")

# ==================================================================== 5. COPILOT
elif page == PAGES[5]:
    st.subheader("Copilot: ask questions about this data")
    api_key = _secret("ANTHROPIC_API_KEY")
    if not api_key:
        st.info("Add `ANTHROPIC_API_KEY` in Secrets to enable the Copilot. Everything else works without it.")
        st.stop()
    st.caption("The Copilot answers only through ArcheNex's own calculation tools, so figures come from your data. "
               "It sends aggregates and top-contributor labels to Claude, not employee-level rows. "
               "It can propose actions, never execute them.")
    cp = st.session_state.get("copilot")
    if cp is None or st.session_state.get("copilot_key") != st.session_state.get("run_key"):
        cp = ag.Copilot(findings, summary, cfg, api_key=api_key)
        st.session_state["copilot"], st.session_state["copilot_key"] = cp, st.session_state.get("run_key")
    hist = st.session_state.setdefault("chat", [])
    for m in hist:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])
    q = st.chat_input("e.g. Which cell should the plant head fix first, and what is it worth?")
    if q:
        with st.chat_message("user"):
            st.markdown(q)
        with st.chat_message("assistant"):
            with st.spinner("Working…"):
                r = cp.ask(q, [{"role": m["role"], "content": m["content"]} for m in hist])
            st.markdown(r["answer"])
            if r["unverified"]:
                st.warning("Check these figures before using them (not found in the tool results): " + ", ".join(r["unverified"]))
            if r["tools_used"]:
                st.caption("Tools used: " + ", ".join(r["tools_used"]))
        hist += [{"role": "user", "content": q}, {"role": "assistant", "content": r["answer"]}]
        st.session_state["copilot_proposals"] = list(cp.proposals)
        if cp.proposals:
            st.success(f"{len(cp.proposals)} proposed action(s) queued in **4. Action Queue** for human approval.")

# ============================================================ 6. WHAT-IF SCENARIOS
elif page == PAGES[6]:
    st.subheader("What-if: how much can realistically be recovered?")
    st.caption("Move the sliders to test different recovery rates. Planning tool only: the headline numbers use the sidebar assumptions.")
    ov = {}
    cols = st.columns(2)
    for i, f in enumerate([x for x in findings if x.tier == "primary"]):
        ov[f.key] = cols[i % 2].slider(charts.short(f), 0, 100, int(cfg["realisation_pct"].get(f.key, 0)), 5, key=f"wi_{f.key}")
    r = ins.scenario(findings, cfg, ov)
    a, b, c = st.columns(3)
    a.metric("Addressable (sidebar assumptions)", dt.inr(r["base_addressable"]))
    b.metric("Addressable (this scenario)", dt.inr(r["scenario_addressable"]), delta=dt.inr(r["delta"]))
    c.metric("Return on fee (scenario)", f"{r['roi_multiple']:.1f}x")
    import plotly.graph_objects as go
    prim = [f for f in findings if f.tier == "primary"]
    fig = go.Figure()
    fig.add_bar(y=[charts.short(f) for f in prim], x=[f.addressable(cfg) / 1e5 for f in prim], orientation="h", name="Sidebar assumptions", marker_color=charts.SLATE)
    fig.add_bar(y=[charts.short(f) for f in prim], x=[f.annualised_inr * ov[f.key] / 100 / 1e5 for f in prim], orientation="h", name="This scenario", marker_color=charts.NAVY)
    fig.update_layout(barmode="group", template="plotly_white", title="Addressable ₹ Lakhs / year by rule", margin=dict(l=10, r=10, t=44, b=10))
    plot(fig, "wi")

# ================================================== 7. HISTORY & MONITORING
elif page == PAGES[7]:
    st.subheader("History & monitoring")
    st.markdown("Save each analysis to track whether leakage is shrinking. For hands-off monitoring, schedule "
                "`python -m archenex.cli monitor` (see docs/DEPLOY.md): it pulls fresh data, re-runs every rule and alerts on changes.")
    if auth.can(ROLE, "reviewer") and st.button("Save this run to history"):
        store.upsert_client(client_name, sector)
        rid = store.save_run(client_name, data_basis, fingerprint, summary, cfg, pipeline.per_finding_snapshot(findings, cfg))
        st.success(f"Run {rid} saved.")
    runs = store.list_runs(client_name)
    if not runs:
        st.info("No saved runs for this client yet.")
    else:
        import plotly.graph_objects as go
        rr = list(reversed(runs))
        fig = go.Figure()
        fig.add_scatter(x=[r["ts"] for r in rr], y=[(r["identified"] or 0) / 1e5 for r in rr], name="Identified", mode="lines+markers")
        fig.add_scatter(x=[r["ts"] for r in rr], y=[(r["addressable"] or 0) / 1e5 for r in rr], name="Addressable", mode="lines+markers")
        fig.update_layout(template="plotly_white", title="Leakage across saved runs (₹ Lakhs / year)", margin=dict(l=10, r=10, t=44, b=10))
        plot(fig, "hist")
        st.dataframe(pd.DataFrame([{"run": r["id"], "time (UTC)": r["ts"], "data": r["data_basis"],
                                    "identified": dt.inr(r["identified"] or 0), "addressable": dt.inr(r["addressable"] or 0),
                                    "fingerprint": r["fingerprint"][:16] + "…"} for r in runs]), hide_index=True)

# ============================================================ 8. REPORT & VERIFY
elif page == PAGES[8]:
    st.subheader("Report & Verify")
    st.markdown("The report is a **draft for human review**. The fingerprint changes if any input, assumption or finding changes.")
    ai_text = st.session_state.get("ai_brief", "")
    api_key = _secret("ANTHROPIC_API_KEY")
    if api_key:
        if st.button("Write the AI CFO brief (aggregated numbers only)"):
            with st.spinner("Writing brief…"):
                st.session_state["ai_brief"] = ag.ai_brief(ag.summary_text(findings, summary), api_key)
            ai_text = st.session_state["ai_brief"]
        if ai_text:
            st.markdown(ai_text)
    decided = store.decisions_for(client_name)
    titles = {a["id"]: a["title"] for a in ag.recommend_actions(findings, cfg)}
    dec_titles = {titles.get(k, k): v for k, v in decided.items()}
    _ok, chain_msg = store.verify_chain()
    head = chain_msg.split("Head hash ")[-1] if _ok and "Head hash" in chain_msg else ""
    if st.button("Build PDF report"):
        with st.spinner("Building PDF…"):
            st.session_state["pdf"] = build_pdf(
                {"client": client_name, "sector": sector, "data_basis": data_basis, "hris": hris, "erp": erp, "is_demo": is_demo},
                findings, summary, cfg, fingerprint, reviewer.strip() or USER, ai_text=ai_text, decisions=dec_titles, audit_head=head)
    if st.session_state.get("pdf"):
        st.download_button("Download PDF report", st.session_state["pdf"], file_name="archenex_audit_dossier.pdf", mime="application/pdf")

    st.markdown("#### Integrity fingerprint")
    st.code(fingerprint)
    _fp, canonical = dt.build_fingerprint(client_name, data_basis, data, cfg, findings)
    st.download_button("Download findings JSON (for independent verification)", canonical.encode("utf-8"),
                       file_name="archenex_findings.json", mime="application/json")
    pasted = st.text_area("Verify: paste a findings JSON", height=100)
    if pasted.strip():
        h = dt.sha256_bytes(pasted.strip().encode("utf-8"))
        (st.success if h == fingerprint else st.error)(
            "Match: this JSON is exactly what produced the fingerprint." if h == fingerprint else
            "No match: the JSON differs from what produced this fingerprint.")
    st.markdown("#### Decision log integrity")
    (st.success if _ok else st.error)(chain_msg)
