import pandas as pd
import pytest

from archenex import detectors as dt
from archenex import insights as ins
from archenex.demo_data import make_demo

CFG = dt.DEFAULT_CONFIG


@pytest.fixture(scope="module")
def demo():
    return make_demo()


@pytest.fixture(scope="module")
def result(demo):
    f, notes = dt.run_all(demo, CFG)
    return f, notes, dt.summarise(f, CFG)


def test_all_nine_rules_run(result):
    f, notes, _ = result
    assert notes == []
    assert {x.key for x in f} == {k for k, _, _ in dt.DETECTORS}
    assert all(x.rows_flagged > 0 for x in f)


def test_demo_is_deterministic():
    a, b = make_demo(), make_demo()
    assert a["attendance"].equals(b["attendance"])


def test_headline_excludes_secondary(result):
    f, _, s = result
    prim = sum(x.annualised_inr for x in f if x.tier == "primary")
    assert s["identified_annual"] == pytest.approx(prim)
    assert s["secondary_identified"] > 0


def test_evidence_sums_to_observed(result):
    for x in result[0]:
        assert x.observed_inr == pytest.approx(float(x.evidence.impact_inr.sum()), rel=1e-6)


def test_ghost_attendance_exact():
    att = pd.DataFrame({"employee_id": ["A", "B"], "date": ["2026-09-01"] * 2, "shift": ["A"] * 2,
                        "cell": ["L1"] * 2, "paid_hours": [8, 8], "hourly_rate": [100, 200],
                        "overtime_hours": [0, 0], "gate_in": ["06:00", ""]})
    f = dt.detect_ghost_attendance(att, CFG)
    assert f.rows_flagged == 1 and f.observed_inr == 1600


def test_payroll_after_exit_exact():
    emp = pd.DataFrame({"employee_id": ["A"], "department": ["Fin"], "designation": ["x"], "ctc_inr": [1.2e6],
                        "join_date": ["2020-01-01"], "exit_date": ["2026-06-30"], "last_rating": [3],
                        "last_promotion_date": [""]})
    pay = pd.DataFrame({"employee_id": ["A"] * 3, "pay_month": ["2026-06-01", "2026-07-01", "2026-08-01"],
                        "gross_inr": [100000] * 3})
    f = dt.detect_payroll_after_exit(emp, pay, CFG)
    assert f.rows_flagged == 2 and f.observed_inr == 200000      # exit-month pay is NOT flagged


def test_duplicate_payments_exact():
    ap = pd.DataFrame({"invoice_id": ["1", "2", "3"], "vendor": ["Apex", "APEX", "Apex"],
                       "invoice_no": ["INV/1", "inv-1", "INV/9"], "invoice_date": ["2026-08-01", "2026-08-03", "2026-08-30"],
                       "amount_inr": [50000, 50000, 70000], "paid_date": ["2026-09-01", "2026-09-03", "2026-09-30"]})
    f = dt.detect_duplicate_payments(ap, CFG)
    assert f.rows_flagged == 1 and f.observed_inr == 50000


def test_overtime_cap_exact():
    rows = [{"employee_id": "A", "date": f"2026-09-0{d}", "shift": "A", "cell": "L1", "paid_hours": 8,
             "hourly_rate": 100, "overtime_hours": 4, "gate_in": "06:00"} for d in range(1, 5)]   # Tue..Fri = 16h
    f = dt.detect_overtime_cap(pd.DataFrame(rows), {**CFG, "weekly_ot_cap_hours": 12, "overtime_multiplier": 2})
    assert f.rows_flagged == 1 and f.observed_inr == pytest.approx(4 * 100 * 2)


def test_flight_risk_is_secondary_and_bounded(result):
    fr = next(x for x in result[0] if x.key == "flight_risk")
    assert fr.tier == "secondary" and fr.evidence.score.max() <= 7


def test_date_parsing_is_day_first_for_non_iso():
    s = dt._dt(pd.Series(["03/07/2026", "2026-07-03"]))
    assert list(s.dt.month) == [7, 7] and list(s.dt.day) == [3, 3]


def test_fingerprint_changes_with_assumptions(demo, result):
    f = result[0]
    a, _ = dt.build_fingerprint("X", "demo", demo, CFG, f)
    cfg2 = {**CFG, "cost_of_capital_pct": 15.0}
    b, _ = dt.build_fingerprint("X", "demo", demo, cfg2, f)
    assert a != b


def test_insights_cross_silo(result):
    f, _, s = result
    heads = ins.headline_insights(f, s, CFG)
    assert any("separate rules" in h["headline"] for h in heads)
    assert not ins.compound_hotspots(f).empty


def test_scenario_math(result):
    f, _, _ = result
    r = ins.scenario(f, CFG, {"idle_staging": 60.0})
    assert r["delta"] > 0
