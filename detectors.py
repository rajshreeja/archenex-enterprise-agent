"""
ArcheNex detection engine.

Every rupee figure produced here is computed from rows in the client's own files,
and every finding carries the evidence rows behind it. No random numbers, no
hard-coded results.

Input datasets (CSV or Excel), column names are case-insensitive:
  attendance   : employee_id, date, shift, cell, paid_hours, hourly_rate, overtime_hours, gate_in
  machine_log  : date, shift, cell, scheduled_hours, active_hours, downtime_reason
  milestones   : milestone_id, project, client, value_inr, signoff_date, invoice_date
  saas         : user_email, app, monthly_cost_inr, last_login_date, employment_status
  employees    : employee_id, department, designation, ctc_inr, join_date, exit_date, last_rating, last_promotion_date
  payroll      : employee_id, pay_month, gross_inr
  ap_invoices  : invoice_id, vendor, invoice_no, invoice_date, amount_inr, paid_date
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

TOOL_VERSION = "3.0.0"

REQUIRED = {
    "attendance": ["employee_id", "date", "shift", "cell", "paid_hours",
                   "hourly_rate", "overtime_hours", "gate_in"],
    "machine_log": ["date", "shift", "cell", "scheduled_hours", "active_hours",
                    "downtime_reason"],
    "milestones": ["milestone_id", "project", "client", "value_inr",
                   "signoff_date", "invoice_date"],
    "saas": ["user_email", "app", "monthly_cost_inr", "last_login_date",
             "employment_status"],
    "employees": ["employee_id", "department", "designation", "ctc_inr", "join_date",
                  "exit_date", "last_rating", "last_promotion_date"],
    "payroll": ["employee_id", "pay_month", "gross_inr"],
    "ap_invoices": ["invoice_id", "vendor", "invoice_no", "invoice_date", "amount_inr",
                    "paid_date"],
}

DATASET_LABELS = {
    "attendance": "Attendance / payroll export (HRIS)",
    "machine_log": "Machine / MES shift log",
    "milestones": "Project milestones & invoices (ERP / CRM)",
    "saas": "SaaS licence & last-login report (IT)",
    "employees": "Employee master (HRIS)",
    "payroll": "Payroll register, monthly (HRIS / payroll)",
    "ap_invoices": "Vendor invoices & payments (ERP accounts payable)",
}

# Planning assumptions. Everything here is editable in the app and is written into
# the integrity fingerprint, so a report always shows which assumptions it used.
DEFAULT_CONFIG = {
    "cost_of_capital_pct": 11.0,       # used to cost delayed invoicing
    "overtime_multiplier": 2.0,        # statutory double rate for overtime
    "invoice_grace_days": 7,           # sign-off -> invoice allowed days
    "saas_inactive_days": 60,
    "low_utilisation_pct": 75.0,       # cell utilisation below this = "under-utilised"
    "avoidable_reasons": "material_staging",   # comma-separated downtime reasons
    "ev_ebitda_multiple": 12.0,        # illustrative; applies to recurring savings only
    "annual_fee_inr": 3_500_000,
    "weekly_ot_cap_hours": 12.0,       # overtime hours per employee per week above this = breach
    "dup_window_days": 5,              # same vendor + amount within N days = suspected duplicate
    "replacement_cost_pct": 50.0,      # cost to replace a leaver, as % of annual CTC (planning assumption)
    "flight_min_score": 5,             # flight-risk points needed to be listed
    # Share of each identified leak that is realistically recoverable.
    # These are PLANNING ASSUMPTIONS until a pilot gives measured numbers.
    "realisation_pct": {
        "idle_staging": 30.0,
        "ghost_attendance": 90.0,
        "overtime_underutil": 50.0,
        "milestone_delay": 60.0,
        "orphaned_saas": 90.0,
        "payroll_after_exit": 90.0,
        "duplicate_payments": 70.0,
        "overtime_cap_breach": 40.0,
        "flight_risk": 15.0,
    },
}

EXITED_WORDS = {"exited", "terminated", "inactive", "left", "resigned", "separated"}


# ----------------------------------------------------------------- formatting
def inr(x: float) -> str:
    x = float(x)
    a = abs(x)
    sign = "-" if x < 0 else ""
    if a >= 1e7:
        return f"{sign}₹{a / 1e7:,.2f} Cr"
    if a >= 1e5:
        return f"{sign}₹{a / 1e5:,.2f} L"
    return f"{sign}₹{a:,.0f}"


# --------------------------------------------------------------- data helpers
def normalise_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]
    return df


def missing_columns(name: str, df: pd.DataFrame) -> list[str]:
    return [c for c in REQUIRED[name] if c not in df.columns]


def _dt(s: pd.Series) -> pd.Series:
    """Parse dates safely. ISO text (2026-07-03) is read as year-month-day; anything else is
    read day-first (Indian convention, e.g. 03/07/2026 = 3 July). Excel dates pass through."""
    if pd.api.types.is_datetime64_any_dtype(s):
        return s.dt.normalize()
    iso = pd.to_datetime(s, errors="coerce", format="ISO8601")
    rest = iso.isna() & s.notna() & (s.astype(str).str.strip() != "")
    if rest.any():
        iso = iso.copy()
        iso[rest] = pd.to_datetime(s[rest], errors="coerce", dayfirst=True, format="mixed")
    return iso.dt.normalize()


def _num(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s, errors="coerce").fillna(0.0)


def _txt(s: pd.Series) -> pd.Series:
    return s.astype(str).str.strip()


def _window(dates: pd.Series) -> int:
    d = dates.dropna()
    return int((d.max() - d.min()).days) + 1 if len(d) else 0


def _annualise(observed: float, window_days: int) -> float:
    return float(observed) * 365.0 / window_days if window_days > 0 else 0.0


def _prep_att(att: pd.DataFrame) -> pd.DataFrame:
    a = att.copy()
    a["date"] = _dt(a["date"])
    a = a.dropna(subset=["date"])
    for c in ("paid_hours", "hourly_rate", "overtime_hours"):
        a[c] = _num(a[c])
    for c in ("employee_id", "shift", "cell"):
        a[c] = _txt(a[c])
    return a


def _prep_mach(m: pd.DataFrame) -> pd.DataFrame:
    m = m.copy()
    m["date"] = _dt(m["date"])
    m = m.dropna(subset=["date"])
    for c in ("scheduled_hours", "active_hours"):
        m[c] = _num(m[c])
    for c in ("shift", "cell"):
        m[c] = _txt(m[c])
    m["downtime_reason"] = m["downtime_reason"].fillna("").astype(str).str.strip().str.lower()
    return m


@dataclass
class Finding:
    key: str
    title: str
    silos: str
    rows_checked: int
    rows_flagged: int
    window_days: int
    observed_inr: float          # cost found inside the data window
    annualised_inr: float        # scaled to 12 months
    evidence: pd.DataFrame       # one row per flagged item (first 4 columns standard)
    method: str
    caveat: str = ""
    extra: dict = field(default_factory=dict)
    tier: str = "primary"        # "primary" counts in the headline; "secondary" is reported separately
    owner: str = ""              # function that owns the fix

    def addressable(self, cfg: dict) -> float:
        return self.annualised_inr * cfg["realisation_pct"].get(self.key, 0.0) / 100.0


_STD = ["date", "where", "detail", "impact_inr"]


def _short_window_note(window: int) -> str:
    return (f" Data window is only {window} days, so annualised figures are unreliable; "
            "supply at least 60-90 days." if 0 < window < 28 else "")


# ------------------------------------------------------------------ detectors
def detect_idle_staging(att, mach, cfg) -> Finding:
    a, m = _prep_att(att), _prep_mach(mach)
    keys = ["date", "shift", "cell"]
    reasons = {r.strip().lower() for r in str(cfg["avoidable_reasons"]).split(",") if r.strip()}

    crew = (a[a.paid_hours > 0].groupby(keys)
            .agg(workers_paid=("employee_id", "nunique"), avg_rate=("hourly_rate", "mean"))
            .reset_index())
    m = m.assign(idle_hours=(m.scheduled_hours - m.active_hours).clip(lower=0))
    av = m[m.downtime_reason.isin(reasons) & (m.idle_hours > 0)]
    j = av.merge(crew, on=keys, how="left")
    j["workers_paid"] = j["workers_paid"].fillna(0)
    j["avg_rate"] = j["avg_rate"].fillna(0)
    j["impact_inr"] = j.idle_hours * j.workers_paid * j.avg_rate
    j = j[j.impact_inr > 0]

    ev = pd.DataFrame({
        "date": j.date.dt.date,
        "where": j.cell + " / Shift " + j["shift"],
        "detail": [f"{h:.1f}h idle ({r}); {int(w)} workers on paid roster"
                   for h, r, w in zip(j.idle_hours, j.downtime_reason, j.workers_paid)],
        "impact_inr": j.impact_inr.round(2),
        "cell": j.cell, "shift": j["shift"], "reason": j.downtime_reason,
        "idle_hours": j.idle_hours, "workers_paid": j.workers_paid.astype(int),
        "avg_rate": j.avg_rate.round(2),
    }).sort_values("impact_inr", ascending=False).reset_index(drop=True)

    win = _window(m.date)
    obs = float(ev.impact_inr.sum())
    return Finding(
        "idle_staging", "Idle-time labour cost (avoidable downtime)",
        "Machine log × Attendance", len(m), len(ev), win, obs, _annualise(obs, win), ev,
        method=("Avoidable idle hours (scheduled - active, for downtime reasons: "
                f"{', '.join(sorted(reasons)) or 'none'}) × workers on the paid roster for that "
                "cell/shift/day × their average hourly rate."),
        caveat=("This is labour cost ATTRIBUTABLE to avoidable idle time. It is recovered by fixing "
                "staging or redeploying crews, not by withholding wages (which carries labour-law "
                "risk). Realisation is therefore set conservatively." + _short_window_note(win)),
    )


def detect_ghost_attendance(att, cfg) -> Finding:
    a = _prep_att(att)
    gi = a["gate_in"].astype(str).str.strip().str.lower()
    no_gate = a["gate_in"].isna() | gi.isin(["", "nan", "none", "nat", "-", "<na>"])
    g = a[(a.paid_hours > 0) & no_gate].copy()
    g["impact_inr"] = g.paid_hours * g.hourly_rate

    ev = pd.DataFrame({
        "date": g.date.dt.date,
        "where": g.cell + " / Shift " + g["shift"],
        "detail": [f"{e}: {h:.1f} paid hours, no gate swipe recorded"
                   for e, h in zip(g.employee_id, g.paid_hours)],
        "impact_inr": g.impact_inr.round(2),
        "cell": g.cell, "shift": g["shift"], "employee_id": g.employee_id,
        "paid_hours": g.paid_hours,
    }).sort_values("impact_inr", ascending=False).reset_index(drop=True)

    win = _window(a.date)
    obs = float(ev.impact_inr.sum())
    return Finding(
        "ghost_attendance", "Paid shifts with no gate swipe",
        "Attendance × Gate/biometric", len(a), len(ev), win, obs, _annualise(obs, win), ev,
        method="Paid hours × hourly rate for every attendance row that has paid hours but no gate-in record.",
        caveat=("A missing swipe is an exception to verify, not proof of fraud (device outages, "
                "manual regularisation and field duty create legitimate gaps). Confirm with Plant HR "
                "before any payroll action." + _short_window_note(win)),
    )


def detect_overtime_underutil(att, mach, cfg) -> Finding:
    a, m = _prep_att(att), _prep_mach(mach)
    keys = ["date", "shift", "cell"]
    low = float(cfg["low_utilisation_pct"])
    mult = float(cfg["overtime_multiplier"])

    util = (m.assign(utilisation_pct=np.where(m.scheduled_hours > 0,
                                              m.active_hours / m.scheduled_hours.where(m.scheduled_hours > 0, np.nan) * 100,
                                              np.nan))
            .groupby(keys, as_index=False)["utilisation_pct"].mean())
    ot = a[a.overtime_hours > 0]
    j = ot.merge(util, on=keys, how="left")
    verified = j[j.utilisation_pct.notna()]
    flag = verified[verified.utilisation_pct < low].copy()
    flag["impact_inr"] = flag.overtime_hours * flag.hourly_rate * mult

    ev = pd.DataFrame({
        "date": flag.date.dt.date,
        "where": flag.cell + " / Shift " + flag["shift"],
        "detail": [f"{e}: {h:.1f}h overtime while cell ran at {u:.0f}% utilisation"
                   for e, h, u in zip(flag.employee_id, flag.overtime_hours, flag.utilisation_pct)],
        "impact_inr": flag.impact_inr.round(2),
        "cell": flag.cell, "shift": flag["shift"], "employee_id": flag.employee_id,
        "overtime_hours": flag.overtime_hours,
        "utilisation_pct": flag.utilisation_pct.round(1),
    }).sort_values("impact_inr", ascending=False).reset_index(drop=True)

    win = _window(a.date)
    obs = float(ev.impact_inr.sum())
    unverified = len(j) - len(verified)
    return Finding(
        "overtime_underutil", "Overtime paid on under-utilised cells",
        "Attendance × Machine log", len(ot), len(ev), win, obs, _annualise(obs, win), ev,
        method=(f"Overtime hours × hourly rate × {mult:g} (overtime multiplier) for shifts where the "
                f"cell's active/scheduled hours were below {low:g}%."),
        caveat=(f"{unverified} overtime rows could not be matched to a machine-log shift and were not "
                "assessed. Overtime can be justified by backlog or catch-up work; treat as a review "
                "list." + _short_window_note(win)),
        extra={"unverified_rows": int(unverified)},
    )


def detect_milestone_delay(ms, cfg) -> Finding:
    d = ms.copy()
    d["signoff_date"] = _dt(d["signoff_date"])
    d["invoice_date"] = _dt(d["invoice_date"])
    d["value_inr"] = _num(d["value_inr"])
    d = d.dropna(subset=["signoff_date"])
    grace = int(cfg["invoice_grace_days"])
    cop = float(cfg["cost_of_capital_pct"]) / 100.0

    as_of = pd.concat([d.signoff_date, d.invoice_date]).max()
    end = d.invoice_date.fillna(as_of)
    d["lag_days"] = (end - d.signoff_date).dt.days
    d["delay_days"] = (d.lag_days - grace).clip(lower=0)
    d["status"] = np.where(d.invoice_date.isna(), "UNBILLED", "Invoiced late")
    d["impact_inr"] = d.value_inr * cop * d.delay_days / 365.0
    flag = d[(d.delay_days > 0) & (d.impact_inr > 0)]

    ev = pd.DataFrame({
        "date": flag.signoff_date.dt.date,
        "where": flag.project.astype(str),
        "detail": [f"{c}: signed off {s:%d %b %Y}, {st.lower()}, {int(l)} days to invoice, {inr(v)}"
                   for c, s, st, l, v in zip(flag.client, flag.signoff_date, flag.status,
                                             flag.lag_days, flag.value_inr)],
        "impact_inr": flag.impact_inr.round(2),
        "project": flag.project.astype(str), "client": flag.client.astype(str),
        "value_inr": flag.value_inr, "status": flag.status,
        "lag_days": flag.lag_days.astype(int), "delay_days": flag.delay_days.astype(int),
    }).sort_values("impact_inr", ascending=False).reset_index(drop=True)

    win = _window(d.signoff_date)
    obs = float(ev.impact_inr.sum())
    unbilled = float(flag.loc[flag.status == "UNBILLED", "value_inr"].sum())
    wavg = float(np.average(flag.delay_days, weights=flag.value_inr)) if len(flag) and flag.value_inr.sum() > 0 else 0.0
    return Finding(
        "milestone_delay", "Delayed milestone invoicing (financing cost)",
        "CRM/ERP billing", len(d), len(ev), win, obs, _annualise(obs, win), ev,
        method=(f"Milestone value × {cop*100:g}% cost of capital × days beyond the {grace}-day "
                "grace period ÷ 365."),
        caveat=("Only the recurring financing cost counts toward annual leakage. The cash stuck in "
                "unbilled milestones is a ONE-TIME working-capital release, reported separately and "
                "never multiplied into valuation." + _short_window_note(win)),
        extra={"unbilled_exposure_inr": unbilled, "value_weighted_delay_days": wavg},
    )


def detect_orphaned_saas(saas, cfg) -> Finding:
    s = saas.copy()
    s["last_login_date"] = _dt(s["last_login_date"])
    s["monthly_cost_inr"] = _num(s["monthly_cost_inr"])
    thr = int(cfg["saas_inactive_days"])
    as_of = s.last_login_date.max()
    s["days_inactive"] = (as_of - s.last_login_date).dt.days
    status = s["employment_status"].fillna("").astype(str).str.strip().str.lower()
    exited = status.isin(EXITED_WORDS)
    flag = s[(s.days_inactive > thr) | exited].copy()
    flag["exited"] = exited.loc[flag.index]
    flag["impact_inr"] = flag.monthly_cost_inr * 12

    ev = pd.DataFrame({
        "date": flag.last_login_date.dt.date,
        "where": flag.app.astype(str),
        "detail": [f"{u}: " + ("employee exited" if x else f"no login for {int(dd)} days")
                   + f", {inr(c)}/month"
                   for u, x, dd, c in zip(flag.user_email, flag.exited, flag.days_inactive,
                                          flag.monthly_cost_inr)],
        "impact_inr": flag.impact_inr.round(2),
        "app": flag.app.astype(str), "user_email": flag.user_email.astype(str),
        "monthly_cost_inr": flag.monthly_cost_inr,
        "days_inactive": flag.days_inactive.fillna(0).astype(int),
        "status": status.loc[flag.index],
    }).sort_values("impact_inr", ascending=False).reset_index(drop=True)

    obs = float(ev.impact_inr.sum())
    return Finding(
        "orphaned_saas", "Orphaned SaaS licences",
        "IT licence report × HR status", len(s), len(ev), 365, obs, obs, ev,
        method=(f"Licences with no login for over {thr} days (measured against the latest login in the "
                "file) or belonging to exited employees, × monthly cost × 12."),
        caveat="Confirm seats are not shared service accounts or seasonal users before reclaiming.",
    )



# ------------------------------------------------------------- v3 detectors
def _month_start(s: pd.Series) -> pd.Series:
    d = _dt(s)
    return d.dt.to_period("M").dt.to_timestamp()


def detect_payroll_after_exit(emp, pay, cfg) -> Finding:
    e = emp.copy()
    e["exit_date"] = _dt(e["exit_date"])
    e["employee_id"] = _txt(e["employee_id"])
    p = pay.copy()
    p["employee_id"] = _txt(p["employee_id"])
    p["pay_month"] = _month_start(p["pay_month"])
    p["gross_inr"] = _num(p["gross_inr"])
    p = p.dropna(subset=["pay_month"])
    left = e.dropna(subset=["exit_date"])[["employee_id", "exit_date", "department"]]
    j = p.merge(left, on="employee_id", how="inner")
    j["exit_month"] = j.exit_date.dt.to_period("M").dt.to_timestamp()
    flag = j[(j.pay_month > j.exit_month) & (j.gross_inr > 0)].copy()

    ev = pd.DataFrame({
        "date": flag.pay_month.dt.date,
        "where": flag.department.astype(str),
        "detail": [f"{i}: exited {x:%d %b %Y}, still paid for {m:%b %Y}"
                   for i, x, m in zip(flag.employee_id, flag.exit_date, flag.pay_month)],
        "impact_inr": flag.gross_inr.round(2),
        "employee_id": flag.employee_id, "department": flag.department.astype(str),
        "months_after_exit": ((flag.pay_month.dt.year - flag.exit_month.dt.year) * 12
                              + flag.pay_month.dt.month - flag.exit_month.dt.month),
    }).sort_values("impact_inr", ascending=False).reset_index(drop=True)

    win = int(round(p.pay_month.nunique() * 30.4)) if len(p) else 0   # payroll is monthly
    obs = float(ev.impact_inr.sum())
    return Finding(
        "payroll_after_exit", "Salary paid after exit date",
        "Payroll × Employee master", len(p), len(ev), win, obs, _annualise(obs, win), ev,
        method="Gross pay in any payroll month later than the employee's exit month.",
        caveat=("Check full-and-final settlements, notice-period buy-outs and garden leave before "
                "treating any row as an error. Recovery is an HR/payroll process, not automatic."
                + _short_window_note(win)),
        owner="HR Operations + Payroll",
    )


def detect_duplicate_payments(ap, cfg) -> Finding:
    d = ap.copy()
    d["invoice_date"] = _dt(d["invoice_date"])
    d["paid_date"] = _dt(d["paid_date"])
    d["amount_inr"] = _num(d["amount_inr"])
    d["vendor"] = _txt(d["vendor"]).str.lower()
    d["invoice_no_n"] = _txt(d["invoice_no"]).str.lower().str.replace(r"[^a-z0-9]", "", regex=True)
    d = d.dropna(subset=["invoice_date"])
    d = d[d.paid_date.notna()].sort_values("invoice_date").reset_index(drop=True)
    win_days = int(cfg["dup_window_days"])

    d["dup_same_no"] = d.duplicated(["vendor", "invoice_no_n", "amount_inr"], keep="first")
    d["prev_amt_date"] = d.groupby(["vendor", "amount_inr"])["invoice_date"].shift(1)
    d["dup_same_amt"] = ((d.invoice_date - d.prev_amt_date).dt.days.abs() <= win_days) & ~d.dup_same_no
    flag = d[(d.dup_same_no | d.dup_same_amt) & (d.amount_inr > 0)].copy()
    flag["basis"] = np.where(flag.dup_same_no, "same vendor + invoice no. + amount",
                             f"same vendor + amount within {win_days} days")

    ev = pd.DataFrame({
        "date": flag.invoice_date.dt.date,
        "where": flag.vendor.str.title(),
        "detail": [f"{iv} ({n}): {inr(a)} paid again; {b}"
                   for iv, n, a, b in zip(flag.invoice_id, flag.invoice_no, flag.amount_inr, flag.basis)],
        "impact_inr": flag.amount_inr.round(2),
        "vendor": flag.vendor.str.title(), "invoice_id": flag.invoice_id.astype(str),
        "basis": flag.basis,
    }).sort_values("impact_inr", ascending=False).reset_index(drop=True)

    win = _window(d.invoice_date)
    obs = float(ev.impact_inr.sum())
    return Finding(
        "duplicate_payments", "Suspected duplicate vendor payments",
        "ERP accounts payable", len(d), len(ev), win, obs, _annualise(obs, win), ev,
        method=("Second and later invoices that repeat vendor + invoice number + amount, or "
                f"vendor + amount within {win_days} days, where payment was made."),
        caveat=("Recurring same-amount charges (rent, retainers) can be legitimate. Recovering "
                "already-paid duplicates is a one-time cash event; the annualised figure shows the "
                "pace of leakage if the control gap stays open." + _short_window_note(win)),
        extra={"one_time_recovery_inr": obs},
        owner="Accounts Payable + Procurement",
    )


def detect_overtime_cap(att, cfg) -> Finding:
    a = _prep_att(att)
    cap = float(cfg["weekly_ot_cap_hours"])
    mult = float(cfg["overtime_multiplier"])
    a["week"] = a.date.dt.to_period("W").dt.start_time
    w = (a.groupby(["employee_id", "week"], as_index=False)
         .agg(ot=("overtime_hours", "sum"), rate=("hourly_rate", "mean"),
              cell=("cell", lambda x: x.mode().iat[0] if len(x) else "")))
    flag = w[w.ot > cap].copy()
    flag["excess"] = flag.ot - cap
    flag["impact_inr"] = flag.excess * flag.rate * mult

    ev = pd.DataFrame({
        "date": flag.week.dt.date, "where": flag.cell,
        "detail": [f"{e}: {o:.1f}h overtime in week of {w_:%d %b}, {x:.1f}h above the {cap:g}h cap"
                   for e, o, w_, x in zip(flag.employee_id, flag.ot, flag.week, flag.excess)],
        "impact_inr": flag.impact_inr.round(2),
        "cell": flag.cell, "employee_id": flag.employee_id,
        "overtime_hours": flag.ot, "excess_hours": flag.excess.round(1),
    }).sort_values("impact_inr", ascending=False).reset_index(drop=True)

    win = _window(a.date)
    obs = float(ev.impact_inr.sum())
    return Finding(
        "overtime_cap_breach", "Overtime above the weekly cap",
        "Attendance / payroll", len(w), len(ev), win, obs, _annualise(obs, win), ev,
        method=(f"Overtime hours per employee per week above {cap:g}h × hourly rate × {mult:g}. "
                "Also a fatigue and safety signal."),
        caveat=("Peak-season or breakdown recovery can justify excess overtime. Treat as a control "
                "review list." + _short_window_note(win)),
        owner="Plant Head + HR Operations",
    )


def detect_flight_risk(emp, cfg) -> Finding:
    """Secondary offering. Transparent points system, NOT a prediction model."""
    e = emp.copy()
    e["join_date"] = _dt(e["join_date"])
    e["exit_date"] = _dt(e["exit_date"])
    e["last_promotion_date"] = _dt(e["last_promotion_date"])
    e["ctc_inr"] = _num(e["ctc_inr"])
    e["last_rating"] = _num(e["last_rating"])
    e["employee_id"] = _txt(e["employee_id"])
    e["department"] = _txt(e["department"])
    act = e[e.exit_date.isna()].copy()
    as_of = pd.concat([e.join_date, e.last_promotion_date, e.exit_date]).max()
    if pd.isna(as_of):
        as_of = pd.Timestamp.today().normalize()
    act["tenure_y"] = (as_of - act.join_date).dt.days / 365.25
    ref = act.last_promotion_date.fillna(act.join_date)
    act["since_promo_y"] = (as_of - ref).dt.days / 365.25
    med = act.groupby("department")["ctc_inr"].transform("median")
    act["pay_ratio"] = np.where(med > 0, act.ctc_inr / med, 1.0)

    pts = np.zeros(len(act), dtype=int)
    why = [[] for _ in range(len(act))]
    rules = [
        (act.last_rating >= 4, 2, "top performer (rating >= 4)"),
        (act.since_promo_y >= 3, 2, "no promotion in 3+ years"),
        (act.pay_ratio < 0.9, 2, "paid below department median"),
        (act.tenure_y.between(1, 3), 1, "1-3 years tenure (typical exit window)"),
    ]
    for cond, p, label in rules:
        c = cond.fillna(False).to_numpy()
        pts += np.where(c, p, 0)
        for i in np.where(c)[0]:
            why[i].append(label)
    act["score"] = pts
    act["reasons"] = ["; ".join(w) for w in why]
    prob = act.score.map(lambda x: {3: 0.10, 4: 0.18, 5: 0.28, 6: 0.38, 7: 0.45, 8: 0.50}.get(int(x), 0.5 if x > 8 else 0.0))
    rc = float(cfg["replacement_cost_pct"]) / 100.0
    act["impact_inr"] = act.ctc_inr * rc * prob
    flag = act[act.score >= int(cfg["flight_min_score"])].copy()

    ev = pd.DataFrame({
        "date": flag.join_date.dt.date, "where": flag.department,
        "detail": [f"{i}: risk score {s}/7 ({r})" for i, s, r in zip(flag.employee_id, flag.score, flag.reasons)],
        "impact_inr": flag.impact_inr.round(2),
        "employee_id": flag.employee_id, "department": flag.department,
        "score": flag.score, "ctc_inr": flag.ctc_inr, "reasons": flag.reasons,
        "tenure_y": flag.tenure_y.round(1), "pay_ratio": flag.pay_ratio.round(2),
    }).sort_values("impact_inr", ascending=False).reset_index(drop=True)

    obs = float(ev.impact_inr.sum())
    return Finding(
        "flight_risk", "Retention exposure: critical people at risk (secondary)",
        "HRIS employee master", len(act), len(ev), 365, obs, obs, ev,
        method=(f"Points: top rating +2, no promotion 3+ yrs +2, pay below dept median +2, 1-3 yrs tenure +1. "
                f"Expected cost = CTC × {rc*100:g}% replacement cost × a fixed probability per score band."),
        caveat=("A rules-based watch-list, not a prediction model: the probabilities are planning "
                "assumptions until validated against this company's own exit history. Use for retention "
                "conversations only."),
        tier="secondary", owner="HR Business Partners",
    )


DETECTORS = [
    ("idle_staging", ("attendance", "machine_log"), detect_idle_staging),
    ("ghost_attendance", ("attendance",), detect_ghost_attendance),
    ("overtime_underutil", ("attendance", "machine_log"), detect_overtime_underutil),
    ("milestone_delay", ("milestones",), detect_milestone_delay),
    ("orphaned_saas", ("saas",), detect_orphaned_saas),
    ("payroll_after_exit", ("employees", "payroll"), detect_payroll_after_exit),
    ("duplicate_payments", ("ap_invoices",), detect_duplicate_payments),
    ("overtime_cap_breach", ("attendance",), detect_overtime_cap),
    ("flight_risk", ("employees",), detect_flight_risk),
]


def run_all(data: dict, cfg: dict):
    """Run every detector whose input files are present. Returns (findings, notes)."""
    findings, notes = [], []
    for key, needs, fn in DETECTORS:
        if not all(n in data for n in needs):
            notes.append(f"Skipped '{key}': needs {', '.join(needs)}.")
            continue
        try:
            args = [data[n] for n in needs]
            findings.append(fn(*args, cfg))
        except Exception as e:  # keep the app alive; surface the problem
            notes.append(f"Rule '{key}' failed: {type(e).__name__}: {e}")
    return findings, notes


def summarise(findings: list[Finding], cfg: dict) -> dict:
    """Headline numbers count PRIMARY findings only; secondary offerings are reported apart."""
    prim = [f for f in findings if f.tier == "primary"]
    sec = [f for f in findings if f.tier != "primary"]
    identified = sum(f.annualised_inr for f in prim)
    addressable = sum(f.addressable(cfg) for f in prim)
    fee = float(cfg["annual_fee_inr"])
    one_time = sum(f.extra.get("unbilled_exposure_inr", 0.0) for f in findings)
    one_time_rec = sum(f.extra.get("one_time_recovery_inr", 0.0) for f in findings)
    return {
        "identified_annual": identified,
        "addressable_annual": addressable,
        "secondary_identified": sum(f.annualised_inr for f in sec),
        "secondary_addressable": sum(f.addressable(cfg) for f in sec),
        "valuation_lift": addressable * float(cfg["ev_ebitda_multiple"]),
        "fee": fee,
        "roi_multiple": addressable / fee if fee > 0 else 0.0,
        "payback_months": (fee / (addressable / 12.0)) if addressable > 0 else float("inf"),
        "one_time_cash_release": one_time,
        "one_time_recovery": one_time_rec,
        "rows_flagged": sum(f.rows_flagged for f in prim),
    }


def build_fingerprint(client: str, data_basis: str, data: dict, cfg: dict,
                      findings: list[Finding]) -> tuple[str, str]:
    """SHA-256 over inputs + assumptions + findings. Tamper-evident integrity check."""
    inputs = {
        name: {"rows": int(len(df)),
               "sha256": hashlib.sha256(df.to_csv(index=False).encode("utf-8")).hexdigest()}
        for name, df in sorted(data.items())
    }
    payload = {
        "tool_version": TOOL_VERSION,
        "client": client,
        "data_basis": data_basis,
        "assumptions": cfg,
        "inputs": inputs,
        "findings": [
            {"key": f.key, "rows_flagged": int(f.rows_flagged),
             "observed_inr": round(f.observed_inr, 2),
             "annualised_inr": round(f.annualised_inr, 2)}
            for f in findings
        ],
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"),
                           ensure_ascii=False, default=str)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest(), canonical


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()
