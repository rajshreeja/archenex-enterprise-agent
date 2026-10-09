"""
Column mapping: lets a client's export keep ITS OWN column names.

Mid-size companies will not reshape their Darwinbox / SAP / Tally exports to match our templates.
So we suggest a mapping (known aliases, then fuzzy match), the analyst confirms it once, and it is
remembered per client.
"""
from __future__ import annotations

import difflib

import numpy as np
import pandas as pd

from detectors import REQUIRED, normalise_columns

# Common header names seen in HR / ERP / MES exports. These are SUGGESTIONS only; the mapping
# screen always shows them to a person for confirmation.
ALIASES: dict[str, dict[str, list[str]]] = {
    "attendance": {
        "employee_id": ["emp_id", "emp_code", "employee_code", "employee_no", "empid", "staff_id", "pernr", "personnel_number"],
        "date": ["attendance_date", "work_date", "punch_date", "day", "posting_date"],
        "shift": ["shift_code", "shift_name", "shift_id"],
        "cell": ["work_center", "workcenter", "line", "department", "dept", "location", "cost_center", "plant_area"],
        "paid_hours": ["hours_paid", "paid_hrs", "payable_hours", "worked_hours", "total_hours", "regular_hours"],
        "hourly_rate": ["rate", "hourly_wage", "wage_rate", "rate_per_hour", "cost_per_hour"],
        "overtime_hours": ["ot_hours", "ot_hrs", "overtime", "ot", "extra_hours"],
        "gate_in": ["in_time", "punch_in", "first_in", "gate_entry", "check_in", "swipe_in", "entry_time"],
    },
    "machine_log": {
        "date": ["production_date", "log_date", "shift_date", "day"],
        "shift": ["shift_code", "shift_name"],
        "cell": ["work_center", "workcenter", "machine_group", "line", "cell_name", "resource"],
        "scheduled_hours": ["planned_hours", "available_hours", "planned_time_h", "scheduled_time"],
        "active_hours": ["run_hours", "running_hours", "productive_hours", "actual_hours", "uptime_hours"],
        "downtime_reason": ["stop_reason", "downtime_code", "loss_reason", "reason", "stoppage_reason"],
    },
    "milestones": {
        "milestone_id": ["ms_id", "milestone_no", "billing_plan_item", "id"],
        "project": ["project_id", "project_code", "wbs", "job_no", "order_no"],
        "client": ["customer", "customer_name", "party", "account"],
        "value_inr": ["amount", "milestone_value", "value", "net_value", "billing_amount", "amount_inr"],
        "signoff_date": ["completion_date", "acceptance_date", "approved_date", "milestone_date", "signed_off_on"],
        "invoice_date": ["billed_date", "billing_date", "invoiced_on", "invoice_dt"],
    },
    "saas": {
        "user_email": ["email", "user", "username", "user_id", "mail"],
        "app": ["application", "product", "software", "app_name", "service"],
        "monthly_cost_inr": ["cost", "monthly_cost", "price", "license_cost", "seat_cost"],
        "last_login_date": ["last_login", "last_active", "last_seen", "last_activity"],
        "employment_status": ["status", "hr_status", "employee_status", "emp_status"],
    },
    "employees": {
        "employee_id": ["emp_id", "emp_code", "employee_code", "employee_no", "pernr", "staff_id"],
        "department": ["dept", "function", "org_unit", "business_unit"],
        "designation": ["title", "job_title", "grade", "position", "role"],
        "ctc_inr": ["ctc", "annual_ctc", "annual_salary", "salary", "total_ctc"],
        "join_date": ["doj", "date_of_joining", "joining_date", "hire_date", "start_date"],
        "exit_date": ["dol", "date_of_leaving", "last_working_day", "lwd", "separation_date", "termination_date"],
        "last_rating": ["rating", "performance_rating", "appraisal_rating", "pms_rating"],
        "last_promotion_date": ["promotion_date", "last_promoted_on", "date_of_last_promotion"],
    },
    "payroll": {
        "employee_id": ["emp_id", "emp_code", "employee_code", "pernr"],
        "pay_month": ["month", "payroll_month", "period", "pay_period"],
        "gross_inr": ["gross", "gross_pay", "gross_salary", "net_pay", "amount", "total_earnings"],
    },
    "ap_invoices": {
        "invoice_id": ["voucher_no", "document_no", "doc_no", "entry_no", "id"],
        "vendor": ["supplier", "vendor_name", "party", "creditor"],
        "invoice_no": ["bill_no", "invoice_number", "supplier_invoice", "reference", "ref_no"],
        "invoice_date": ["bill_date", "document_date", "posting_date", "date"],
        "amount_inr": ["amount", "invoice_amount", "gross_amount", "bill_amount", "value"],
        "paid_date": ["payment_date", "paid_on", "cleared_date", "clearing_date"],
    },
}

# Fields that are safe to default when a client genuinely does not have them: leaving them
# empty can only make a rule find LESS, never invent findings.
SAFE_DEFAULTS: dict[str, dict] = {
    "attendance": {"overtime_hours": 0.0},
    "machine_log": {"downtime_reason": ""},
    "saas": {"employment_status": "active"},
    "employees": {"designation": "", "last_rating": np.nan, "last_promotion_date": pd.NaT, "exit_date": pd.NaT},
}


def _n(x: str) -> str:
    return str(x).strip().lower().replace(" ", "_").replace("-", "_")


def suggest_mapping(dataset: str, columns: list[str]) -> dict[str, str | None]:
    """{required_field: client_column or None}."""
    cols = {_n(c): c for c in columns}
    used: set[str] = set()
    out: dict[str, str | None] = {}
    for field in REQUIRED[dataset]:
        pick = None
        if field in cols and cols[field] not in used:
            pick = cols[field]
        if pick is None:
            for al in ALIASES.get(dataset, {}).get(field, []):
                if al in cols and cols[al] not in used:
                    pick = cols[al]
                    break
        if pick is None:
            close = difflib.get_close_matches(field, list(cols), n=1, cutoff=0.78)
            if close and cols[close[0]] not in used:
                pick = cols[close[0]]
        if pick:
            used.add(pick)
        out[field] = pick
    return out


def unmapped_required(dataset: str, mapping: dict) -> list[str]:
    """Required fields still missing AND not safely defaultable."""
    safe = SAFE_DEFAULTS.get(dataset, {})
    return [f for f in REQUIRED[dataset] if not mapping.get(f) and f not in safe]


def apply_mapping(df: pd.DataFrame, dataset: str, mapping: dict) -> pd.DataFrame:
    """Return a frame with exactly the canonical columns, in canonical order."""
    out = {}
    safe = SAFE_DEFAULTS.get(dataset, {})
    for field in REQUIRED[dataset]:
        src = mapping.get(field)
        if src and src in df.columns:
            out[field] = df[src].to_numpy()
        elif field in safe:
            out[field] = [safe[field]] * len(df)
        else:
            raise ValueError(f"No column mapped for required field '{field}'.")
    return pd.DataFrame(out)


def auto_ingest(dataset: str, df: pd.DataFrame, saved: dict | None = None) -> tuple[pd.DataFrame | None, dict, list[str]]:
    """Try saved mapping, else suggestion. Returns (canonical_df or None, mapping, problems)."""
    raw = df.copy()
    mapping = dict(saved or {})
    if not mapping or any(v and v not in raw.columns for v in mapping.values()):
        mapping = suggest_mapping(dataset, list(raw.columns))
    missing = unmapped_required(dataset, mapping)
    if missing:
        return None, mapping, missing
    return apply_mapping(raw, dataset, mapping), mapping, []
