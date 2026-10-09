import json
import os
import sqlite3
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

import pandas as pd
import pytest

from archenex import agent, auth, dispatch, mapping, pipeline, report, store
from archenex import detectors as dt
from archenex.connectors import assert_read_only, build_connectors
from archenex.demo_data import make_demo


# ------------------------------------------------------------------ audit chain
def test_audit_chain_detects_tampering(tmp_path):
    p = str(tmp_path / "a.db")
    store.append_audit("C", "r", "reviewer", "a1", "Do X", "Approve", path=p)
    store.append_audit("C", "r", "reviewer", "a2", "Do Y", "Reject", path=p)
    assert store.verify_chain(p)[0]
    sqlite3.connect(p).execute("UPDATE audit SET decision='Approve' WHERE id=2").connection.commit()
    ok, msg = store.verify_chain(p)
    assert not ok and "altered" in msg


def test_audit_chain_detects_deletion(tmp_path):
    p = str(tmp_path / "a.db")
    for i in range(3):
        store.append_audit("C", "r", "reviewer", f"a{i}", "x", "Approve", path=p)
    c = sqlite3.connect(p); c.execute("DELETE FROM audit WHERE id=2"); c.commit()
    assert not store.verify_chain(p)[0]


def test_run_history_roundtrip(tmp_path):
    p = str(tmp_path / "r.db")
    d = make_demo(n_employees=200, days=60)
    res = pipeline.analyse_and_save("Acme", d, dt.DEFAULT_CONFIG, "demo", db_path=p)
    runs = store.list_runs("Acme", path=p)
    assert runs and runs[0]["fingerprint"] == res["fingerprint"]


def test_raw_rows_never_stored(tmp_path):
    p = str(tmp_path / "r.db")
    d = make_demo(n_employees=100, days=40)
    pipeline.analyse_and_save("Acme", d, dt.DEFAULT_CONFIG, "demo", db_path=p)
    blob = open(p, "rb").read()
    assert b"EMP10000" not in blob and b"@demo-plant.example" not in blob


def test_monitor_alerts_on_worsening(tmp_path):
    p = str(tmp_path / "m.db")
    cfg = dt.DEFAULT_CONFIG
    d = make_demo(n_employees=300, days=60)
    pipeline.analyse_and_save("Acme", d, cfg, "x", db_path=p)
    worse = {**d, "saas": d["saas"].assign(employment_status="exited")}
    res = pipeline.analyse_and_save("Acme", worse, cfg, "x", db_path=p)
    alerts = pipeline.compare_with_previous("Acme", res["findings"], cfg, db_path=p)
    assert any("SaaS" in a for a in alerts)


# --------------------------------------------------------------------- mapping
def test_mapping_suggests_and_applies():
    df = pd.DataFrame({"Emp Code": ["E1"], "Attendance Date": ["2026-01-01"], "Shift Code": ["A"], "Work Center": ["L3"],
                       "Hours Paid": [8], "Rate": [100], "OT Hours": [1], "In Time": ["06:00"]})
    out, m, missing = mapping.auto_ingest("attendance", df)
    assert missing == [] and list(out.columns) == dt.REQUIRED["attendance"]


def test_mapping_refuses_when_critical_column_missing():
    df = pd.DataFrame({"emp_id": ["E1"], "date": ["2026-01-01"], "shift": ["A"], "cell": ["x"],
                       "paid_hours": [8], "hourly_rate": [1]})
    out, m, missing = mapping.auto_ingest("attendance", df)
    assert out is None and missing == ["gate_in"]      # would otherwise flag every row as a ghost shift


# ------------------------------------------------------------------ connectors
@pytest.mark.parametrize("sql,ok", [("select 1", True), ("WITH a AS (select 1) select * from a", True),
                                    ("select 'update' as x", True), ("DROP TABLE t", False),
                                    ("select 1; delete from t", False), ("select * into x from y", False),
                                    ("update t set a=1", False)])
def test_sql_guard(sql, ok):
    if ok:
        assert_read_only(sql)
    else:
        with pytest.raises(ValueError):
            assert_read_only(sql)


def test_sql_connector_and_ingest(tmp_path):
    db = str(tmp_path / "erp.db")
    c = sqlite3.connect(db)
    c.execute("CREATE TABLE s(user_email TEXT, app TEXT, monthly_cost_inr REAL, last_login_date TEXT, employment_status TEXT)")
    c.execute("INSERT INTO s VALUES('a@x.com','Jira',1000,'2026-01-01','exited')")
    c.commit(); c.close()
    conns = build_connectors({"connections": {"erp": {"kind": "sql", "url": "sqlite:///" + db,
                                                      "queries": {"saas": "SELECT * FROM s"}}}})
    assert conns["erp"].test()[0]
    data, notes = pipeline.ingest(conns, "Acme", db_path=str(tmp_path / "s.db"))
    assert "saas" in data


class _H(BaseHTTPRequestHandler):
    def do_GET(self):
        q = parse_qs(urlparse(self.path).query)
        pg, n = int(q["page"][0]), int(q["per_page"][0])
        assert self.headers["Authorization"] == "Bearer tok"
        rows = [{"emp_code": f"E{i}"} for i in range((pg - 1) * n, min(pg * n, 5))]
        b = json.dumps({"data": {"items": rows}}).encode()
        self.send_response(200); self.send_header("Content-Type", "application/json"); self.end_headers(); self.wfile.write(b)

    def log_message(self, *a):
        pass


def test_rest_connector_pagination_and_auth(monkeypatch):
    srv = HTTPServer(("127.0.0.1", 0), _H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    monkeypatch.setenv("T", "tok")
    cn = build_connectors({"connections": {"h": {
        "kind": "rest", "base_url": f"http://127.0.0.1:{srv.server_port}", "allow_private": True,
        "auth": {"type": "bearer", "token": "${T}"},
        "endpoints": {"employees": {"path": "/x", "records_path": "data.items",
                                    "pagination": {"type": "page", "size": 2}, "field_map": {"emp_code": "employee_id"}}}}}})["h"]
    df = cn.fetch("employees")
    assert len(df) == 5 and "employee_id" in df.columns
    srv.shutdown()


def test_rest_blocks_plain_http_and_private():
    for url in ("http://example.com", "https://127.0.0.1", "https://10.0.0.5"):
        cn = build_connectors({"connections": {"h": {"kind": "rest", "base_url": url, "endpoints": {"a": {"path": "/"}}}}})["h"]
        with pytest.raises(ValueError):
            cn.fetch("a")


# ------------------------------------------------------------------------ auth
def test_password_hashing_and_roles():
    h = auth.hash_password("s3cret")
    assert auth.verify_password("s3cret", h) and not auth.verify_password("nope", h)
    users = {"priya": {"password_hash": h, "role": "reviewer"}}
    assert auth.authenticate("priya", "s3cret", users, None) == ("reviewer", "priya")
    assert auth.authenticate("priya", "bad", users, None) is None
    assert auth.can("admin", "reviewer") and not auth.can("viewer", "reviewer")


# ------------------------------------------------------------- agent + dispatch
class _Block:
    def __init__(self, **kw): self.__dict__.update(kw)


class _FakeClient:
    def __init__(self, final): self.n = 0; self.final = final; self.messages = self

    def create(self, **kw):
        self.n += 1
        if self.n == 1:
            return _Block(stop_reason="tool_use", content=[
                _Block(type="tool_use", id="1", name="drill_down", input={"finding_key": "idle_staging", "group_by": "cell", "top_n": 1}),
                _Block(type="tool_use", id="2", name="propose_action", input={"title": "Fix staging", "owner": "Plant Head", "detail": "x"})])
        return _Block(stop_reason="end_turn", content=[_Block(type="text", text=self.final)])


def test_copilot_grounding_and_no_execution():
    d = make_demo(n_employees=300, days=60)
    f, _ = dt.run_all(d, dt.DEFAULT_CONFIG)
    s = dt.summarise(f, dt.DEFAULT_CONFIG)
    cp = agent.Copilot(f, s, dt.DEFAULT_CONFIG, client=_FakeClient("The worst cell loses 987654321 rupees."))
    r = cp.ask("where?")
    assert "987654321" in r["unverified"]                # invented number is flagged
    assert cp.proposals and cp.proposals[0]["source"] == "copilot"   # proposed, not executed


def test_copilot_without_key_degrades():
    cp = agent.Copilot([], {}, dt.DEFAULT_CONFIG)
    assert "ANTHROPIC_API_KEY" in cp.ask("hi")["answer"]


def test_dispatch_is_dry_run_by_default():
    out = dispatch.send({"title": "t", "owner": "o", "detail": "d", "impact_inr_annual": 1}, "C", "r", "https://hooks.example/x")
    assert out["dry_run"] and not out["sent"]


# ---------------------------------------------------------------------- report
def test_pdf_builds_and_has_pages():
    d = make_demo(n_employees=400, days=70)
    cfg = dt.DEFAULT_CONFIG
    f, _ = dt.run_all(d, cfg)
    s = dt.summarise(f, cfg)
    fp, _ = dt.build_fingerprint("X", "demo", d, cfg, f)
    pdf = report.build_pdf({"client": "X", "sector": "Auto", "data_basis": "SYNTHETIC", "hris": "A", "erp": "B", "is_demo": True},
                           f, s, cfg, fp, "R")
    assert pdf[:4] == b"%PDF" and len(pdf) > 100_000
