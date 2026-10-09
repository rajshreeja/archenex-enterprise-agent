"""
Persistence (SQLite). Stores configuration, run summaries and the decision audit trail.

PRIVACY BY DESIGN: raw client rows (employee IDs, e-mails, payroll lines) are never written
here. Only aggregates, assumptions, fingerprints and human decisions are stored. That keeps the
store small, easy to back up and easy to defend in a security review.

The audit trail is hash-chained: each row's hash covers the previous row's hash, so editing or
deleting any past row breaks verification. This is tamper-EVIDENT, not tamper-proof: for stronger
guarantees, ship the latest chain hash to an external system (e.g. e-mail it to the client monthly).
"""
from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import threading
from contextlib import contextmanager
from datetime import datetime, timezone

DB_PATH = os.environ.get("ARCHENEX_DB", os.path.join("data", "archenex.db"))
_LOCK = threading.Lock()
GENESIS = "0" * 64

SCHEMA = """
CREATE TABLE IF NOT EXISTS clients(
  id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE NOT NULL, sector TEXT, created TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS runs(
  id INTEGER PRIMARY KEY AUTOINCREMENT, client TEXT NOT NULL, ts TEXT NOT NULL, data_basis TEXT,
  fingerprint TEXT NOT NULL, identified REAL, addressable REAL, summary_json TEXT, cfg_json TEXT);
CREATE TABLE IF NOT EXISTS audit(
  id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT NOT NULL, client TEXT NOT NULL, reviewer TEXT,
  role TEXT, action_id TEXT, action TEXT, decision TEXT, note TEXT, prev_hash TEXT NOT NULL, hash TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS mappings(
  client TEXT NOT NULL, dataset TEXT NOT NULL, mapping_json TEXT NOT NULL, updated TEXT NOT NULL,
  PRIMARY KEY(client, dataset));
"""


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


@contextmanager
def conn(path: str | None = None):
    path = path or DB_PATH
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)
    c = sqlite3.connect(path, timeout=15)
    c.row_factory = sqlite3.Row
    try:
        with _LOCK:
            c.executescript(SCHEMA)
            yield c
            c.commit()
    finally:
        c.close()


# ------------------------------------------------------------------ clients
def upsert_client(name: str, sector: str = "", path=None) -> None:
    with conn(path) as c:
        c.execute("INSERT OR IGNORE INTO clients(name, sector, created) VALUES(?,?,?)", (name, sector, _now()))
        c.execute("UPDATE clients SET sector=? WHERE name=?", (sector, name))


def list_clients(path=None) -> list[str]:
    with conn(path) as c:
        return [r["name"] for r in c.execute("SELECT name FROM clients ORDER BY name")]


# --------------------------------------------------------------------- runs
def save_run(client: str, data_basis: str, fingerprint: str, summary: dict, cfg: dict,
             per_finding: dict, path=None) -> int:
    payload = {"summary": {k: (None if v == float("inf") else v) for k, v in summary.items()},
               "per_finding": per_finding}
    with conn(path) as c:
        cur = c.execute(
            "INSERT INTO runs(client, ts, data_basis, fingerprint, identified, addressable, summary_json, cfg_json)"
            " VALUES(?,?,?,?,?,?,?,?)",
            (client, _now(), data_basis, fingerprint, summary.get("identified_annual"),
             summary.get("addressable_annual"), json.dumps(payload, default=str),
             json.dumps(cfg, default=str, sort_keys=True)))
        return int(cur.lastrowid)


def list_runs(client: str, limit: int = 50, path=None) -> list[dict]:
    with conn(path) as c:
        rows = c.execute("SELECT * FROM runs WHERE client=? ORDER BY id DESC LIMIT ?", (client, limit)).fetchall()
    out = []
    for r in rows:
        d = dict(r)
        d["payload"] = json.loads(d.pop("summary_json") or "{}")
        out.append(d)
    return out


# -------------------------------------------------------------------- audit
def _row_hash(prev: str, ts, client, reviewer, role, action_id, action, decision, note) -> str:
    body = json.dumps([prev, ts, client, reviewer, role, action_id, action, decision, note],
                      ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def append_audit(client: str, reviewer: str, role: str, action_id: str, action: str,
                 decision: str, note: str = "", path=None) -> str:
    with conn(path) as c:
        last = c.execute("SELECT hash FROM audit ORDER BY id DESC LIMIT 1").fetchone()
        prev = last["hash"] if last else GENESIS
        ts = _now()
        h = _row_hash(prev, ts, client, reviewer, role, action_id, action, decision, note)
        c.execute("INSERT INTO audit(ts, client, reviewer, role, action_id, action, decision, note, prev_hash, hash)"
                  " VALUES(?,?,?,?,?,?,?,?,?,?)",
                  (ts, client, reviewer, role, action_id, action, decision, note, prev, h))
        return h


def list_audit(client: str | None = None, path=None) -> list[dict]:
    with conn(path) as c:
        if client:
            rows = c.execute("SELECT * FROM audit WHERE client=? ORDER BY id", (client,)).fetchall()
        else:
            rows = c.execute("SELECT * FROM audit ORDER BY id").fetchall()
    return [dict(r) for r in rows]


def decisions_for(client: str, path=None) -> dict[str, str]:
    """Latest decision per action id for this client."""
    out: dict[str, str] = {}
    for r in list_audit(client, path):
        if r["decision"] in ("Approve", "Reject", "Defer"):
            out[r["action_id"]] = r["decision"]
    return out


def verify_chain(path=None) -> tuple[bool, str]:
    """Recompute every hash across ALL clients. Returns (ok, message)."""
    rows = list_audit(None, path)
    prev = GENESIS
    for r in rows:
        if r["prev_hash"] != prev:
            return False, f"Chain broken at row {r['id']}: previous-hash mismatch (a row was removed or reordered)."
        h = _row_hash(prev, r["ts"], r["client"], r["reviewer"], r["role"], r["action_id"],
                      r["action"], r["decision"], r["note"])
        if h != r["hash"]:
            return False, f"Row {r['id']} was altered after it was written."
        prev = r["hash"]
    return True, f"Audit chain intact: {len(rows)} entries verified. Head hash {prev[:16]}…"


# ----------------------------------------------------------------- mappings
def save_mapping(client: str, dataset: str, mapping: dict, path=None) -> None:
    with conn(path) as c:
        c.execute("INSERT INTO mappings(client, dataset, mapping_json, updated) VALUES(?,?,?,?) "
                  "ON CONFLICT(client, dataset) DO UPDATE SET mapping_json=excluded.mapping_json, updated=excluded.updated",
                  (client, dataset, json.dumps(mapping, sort_keys=True), _now()))


def load_mapping(client: str, dataset: str, path=None) -> dict:
    with conn(path) as c:
        r = c.execute("SELECT mapping_json FROM mappings WHERE client=? AND dataset=?", (client, dataset)).fetchone()
    return json.loads(r["mapping_json"]) if r else {}
