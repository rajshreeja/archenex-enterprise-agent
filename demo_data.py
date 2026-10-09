"""
Synthetic demo data for ArcheNex.

Everything here is invented, seeded for repeatability, and clearly labelled as
synthetic in the app. It exists so the platform can be demonstrated without client
data; it is NOT evidence of results at any real company.
"""
import numpy as np
import pandas as pd

CELLS = ["Assembly Line 3", "Assembly Line 4", "CNC Machining Cell 1",
         "CNC Machining Cell 2", "Tooling & Maintenance", "Press Shop"]
SHIFTS = ["A", "B", "C"]
SHIFT_START_HOUR = {"A": 6, "B": 14, "C": 22}
# Cell/shift combinations with a (planted) chronic material-staging problem
HOTSPOTS = {("Assembly Line 4", "B"), ("Assembly Line 4", "C"), ("Assembly Line 3", "C")}
SAAS_APPS = {"Microsoft 365": 1650, "Salesforce": 6400, "Zoho CRM": 1800, "Jira": 950,
             "Tableau": 5200, "DocuSign": 2400, "SAP Concur": 1300}


def make_demo(seed: int = 42, n_employees: int = 1450, days: int = 90,
              end: str = "2026-09-30", n_saas: int = 380, n_milestones: int = 60) -> dict:
    rng = np.random.default_rng(seed)
    all_dates = pd.date_range(end=end, periods=days)
    work_dates = all_dates[all_dates.dayofweek != 6]  # no Sunday shifts

    # ---- machine / MES shift log -------------------------------------------------
    rows = []
    for d in work_dates:
        for c in CELLS:
            for s in SHIFTS:
                p_stage = 0.40 if (c, s) in HOTSPOTS else 0.05
                r = rng.random()
                idle, reason = 0.0, "none"
                if r < p_stage:
                    reason, idle = "material_staging", round(rng.uniform(1.5, 3.5), 1)
                elif r < p_stage + 0.12:
                    reason, idle = "changeover", round(rng.uniform(0.3, 0.8), 1)
                elif r < p_stage + 0.18:
                    reason, idle = "planned_maintenance", round(rng.uniform(0.5, 1.5), 1)
                elif r < p_stage + 0.22:
                    reason, idle = "breakdown", round(rng.uniform(1.0, 2.5), 1)
                rows.append((d, s, c, 8.0, round(8.0 - idle, 1), reason))
    mach = pd.DataFrame(rows, columns=["date", "shift", "cell", "scheduled_hours",
                                       "active_hours", "downtime_reason"])

    # ---- attendance --------------------------------------------------------------
    emp = pd.DataFrame({
        "employee_id": [f"EMP{10000 + i}" for i in range(n_employees)],
        "cell": rng.choice(CELLS, n_employees, p=[.20, .18, .20, .17, .10, .15]),
        "shift": rng.choice(SHIFTS, n_employees, p=[.50, .32, .18]),
        "hourly_rate": rng.integers(95, 215, n_employees),
    })
    att = emp.merge(pd.DataFrame({"date": work_dates}), how="cross")
    att = att[rng.random(len(att)) < 0.93].reset_index(drop=True)
    att["paid_hours"] = 8.0

    util = mach.assign(u=mach.active_hours / mach.scheduled_hours * 100)[["date", "shift", "cell", "u"]]
    att = att.merge(util, on=["date", "shift", "cell"], how="left")
    p_ot = np.where(att.u < 75, 0.28, 0.07)
    is_ot = rng.random(len(att)) < p_ot
    att["overtime_hours"] = np.where(is_ot, rng.choice([1.0, 1.5, 2.0, 3.0], len(att)), 0.0)

    # planted: a group of employees on sustained heavy overtime in the last five weeks
    heavy = rng.choice(emp.employee_id.to_numpy(), 25, replace=False)
    att.loc[att.employee_id.isin(heavy) & (att.date >= pd.Timestamp(end) - pd.Timedelta(days=35)),
            "overtime_hours"] = 3.0

    start_h = att["shift"].map(SHIFT_START_HOUR).to_numpy()
    mins = rng.integers(0, 20, len(att))
    gate = np.array([f"{h:02d}:{m:02d}" for h, m in zip(start_h, mins)], dtype=object)
    ghost = rng.random(len(att)) < 0.012
    gate[ghost] = np.nan
    att["gate_in"] = gate
    att = att[["employee_id", "date", "shift", "cell", "paid_hours", "hourly_rate",
               "overtime_hours", "gate_in"]]

    # ---- milestones / invoices ---------------------------------------------------
    sign = pd.Series(rng.choice(all_dates[:-5], n_milestones))
    lag = np.round(rng.gamma(3.0, 6.0, n_milestones)).astype(int) + 2
    inv = sign + pd.to_timedelta(lag, unit="D")
    inv[inv > pd.Timestamp(end)] = pd.NaT
    inv.iloc[rng.choice(n_milestones, 8, replace=False)] = pd.NaT   # never invoiced
    ms = pd.DataFrame({
        "milestone_id": [f"MS-{2000 + i}" for i in range(n_milestones)],
        "project": [f"PRJ-{rng.integers(10, 40)}" for _ in range(n_milestones)],
        "client": rng.choice(["Client A", "Client B", "Client C", "Client D", "Client E"], n_milestones),
        "value_inr": rng.integers(3, 40, n_milestones) * 100_000,
        "signoff_date": sign,
        "invoice_date": inv,
    })

    # ---- SaaS licences -----------------------------------------------------------
    app_names = rng.choice(list(SAAS_APPS), n_saas)
    days_since = np.where(rng.random(n_saas) < 0.20, rng.integers(61, 240, n_saas),
                          rng.integers(0, 45, n_saas))
    days_since[0] = 0
    saas = pd.DataFrame({
        "user_email": [f"user{i}@demo-plant.example" for i in range(n_saas)],
        "app": app_names,
        "monthly_cost_inr": [SAAS_APPS[a] for a in app_names],
        "last_login_date": pd.Timestamp(end) - pd.to_timedelta(days_since, unit="D"),
        "employment_status": np.where(rng.random(n_saas) < 0.06, "exited", "active"),
    })


    # ---- employee master + payroll ------------------------------------------------
    n_emp = len(emp)
    end_ts = pd.Timestamp(end)
    depts = np.array(["Production", "Quality", "Maintenance", "Stores & SCM", "Sales", "Finance", "HR & Admin", "IT"])
    dept = rng.choice(depts, n_emp, p=[.55, .10, .10, .08, .06, .04, .04, .03])
    base_ctc = np.where(np.isin(dept, ["Production", "Maintenance"]), 4.8e5, 9.0e5)
    ctc = (base_ctc * rng.normal(1.0, 0.18, n_emp)).clip(2.4e5).round(-3)
    join = end_ts - pd.to_timedelta(rng.integers(120, 3200, n_emp), unit="D")
    promo = pd.Series(join + pd.to_timedelta((rng.random(n_emp) * (end_ts - join).days).astype(int), unit="D"))
    promo[rng.random(n_emp) < 0.35] = pd.NaT
    exited_idx = rng.choice(n_emp, 60, replace=False)
    exit_dt = pd.Series([pd.NaT] * n_emp, dtype="datetime64[ns]")
    exit_dt.iloc[exited_idx] = end_ts - pd.to_timedelta(rng.integers(35, 120, 60), unit="D")
    employees = pd.DataFrame({
        "employee_id": emp.employee_id, "department": dept,
        "designation": np.where(base_ctc > 5e5, "Executive / Engineer", "Operator / Technician"),
        "ctc_inr": ctc, "join_date": join, "exit_date": exit_dt,
        "last_rating": rng.choice([2, 3, 3, 3, 4, 5], n_emp), "last_promotion_date": promo,
    })
    months = pd.period_range(end=end_ts, periods=3, freq="M").to_timestamp()
    pay = employees[["employee_id", "ctc_inr", "exit_date"]].merge(pd.DataFrame({"pay_month": months}), how="cross")
    pay["gross_inr"] = (pay.ctc_inr / 12).round(0)
    exm = pay.exit_date.dt.to_period("M").dt.to_timestamp()
    stopped = pay.exit_date.notna() & (pay.pay_month > exm)
    # planted: only ~12% of leavers keep getting paid; payroll normally drops them
    leak_ids = set(employees.employee_id.iloc[exited_idx[:8]])
    pay = pay[~(stopped & ~pay.employee_id.isin(leak_ids))]
    payroll = pay[["employee_id", "pay_month", "gross_inr"]].reset_index(drop=True)

    # ---- vendor invoices (accounts payable) ---------------------------------------
    n_inv = 640
    vendors = np.array(["Apex Tooling", "Bharat Fasteners", "Coastal Logistics", "Delta Lubricants",
                        "Eastern Packaging", "FlexiSteel Traders", "Gamma Calibration", "Hind Electricals"])
    inv_dates = pd.Series(rng.choice(all_dates, n_inv))
    ap = pd.DataFrame({
        "invoice_id": [f"AP-{5000 + i}" for i in range(n_inv)],
        "vendor": rng.choice(vendors, n_inv),
        "invoice_no": [f"INV/{rng.integers(1000, 99999)}" for _ in range(n_inv)],
        "invoice_date": inv_dates,
        "amount_inr": (rng.integers(8, 400, n_inv) * 1000 + rng.integers(0, 999, n_inv)),
    })
    ap["paid_date"] = ap.invoice_date + pd.to_timedelta(rng.integers(20, 55, n_inv), unit="D")
    ap.loc[ap.paid_date > end_ts, "paid_date"] = pd.NaT
    dup_src = ap.sample(22, random_state=seed).copy()
    dup_src["invoice_id"] = [f"AP-{9000 + i}" for i in range(len(dup_src))]
    dup_src["invoice_date"] = dup_src.invoice_date + pd.to_timedelta(rng.integers(0, 4, len(dup_src)), unit="D")
    dup_src["paid_date"] = dup_src.invoice_date + pd.to_timedelta(rng.integers(20, 40, len(dup_src)), unit="D")
    dup_src.loc[dup_src.paid_date > end_ts, "paid_date"] = pd.NaT
    ap = pd.concat([ap, dup_src], ignore_index=True)

    return {"attendance": att, "machine_log": mach, "milestones": ms, "saas": saas,
            "employees": employees, "payroll": payroll, "ap_invoices": ap}


def templates() -> dict:
    """Tiny example files showing the exact columns a client export must have."""
    return {
        "attendance": pd.DataFrame({
            "employee_id": ["EMP001", "EMP002"], "date": ["2026-09-01", "2026-09-01"],
            "shift": ["A", "A"], "cell": ["Assembly Line 3", "Assembly Line 3"],
            "paid_hours": [8, 8], "hourly_rate": [150, 130], "overtime_hours": [0, 2],
            "gate_in": ["06:05", ""]}),
        "machine_log": pd.DataFrame({
            "date": ["2026-09-01"], "shift": ["A"], "cell": ["Assembly Line 3"],
            "scheduled_hours": [8], "active_hours": [5.5], "downtime_reason": ["material_staging"]}),
        "milestones": pd.DataFrame({
            "milestone_id": ["MS-1"], "project": ["PRJ-12"], "client": ["Client A"],
            "value_inr": [1500000], "signoff_date": ["2026-08-10"], "invoice_date": ["2026-09-02"]}),
        "saas": pd.DataFrame({
            "user_email": ["a@company.com"], "app": ["Salesforce"], "monthly_cost_inr": [6400],
            "last_login_date": ["2026-05-01"], "employment_status": ["active"]}),
        "employees": pd.DataFrame({
            "employee_id": ["EMP001", "EMP002"], "department": ["Production", "Finance"],
            "designation": ["Operator", "Accountant"], "ctc_inr": [480000, 900000],
            "join_date": ["2022-04-01", "2020-01-15"], "exit_date": ["", "2026-06-30"],
            "last_rating": [4, 3], "last_promotion_date": ["2023-04-01", ""]}),
        "payroll": pd.DataFrame({
            "employee_id": ["EMP001", "EMP002"], "pay_month": ["2026-09-01", "2026-09-01"],
            "gross_inr": [40000, 75000]}),
        "ap_invoices": pd.DataFrame({
            "invoice_id": ["AP-1"], "vendor": ["Apex Tooling"], "invoice_no": ["INV/1001"],
            "invoice_date": ["2026-08-01"], "amount_inr": [125000], "paid_date": ["2026-09-02"]}),
    }


if __name__ == "__main__":
    for name, df in templates().items():
        df.to_csv(f"templates/template_{name}.csv", index=False)
    print("Template files written.")
