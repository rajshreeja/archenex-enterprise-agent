"""
Orchestration: connectors -> mapping -> detectors -> insights -> saved run.
Used by the app, the CLI and the tests, so all three behave identically.
"""
from __future__ import annotations

import json

import pandas as pd

from . import detectors as dt
from . import insights as ins
from . import mapping as mp
from . import store
from .connectors import Connector


def ingest(connectors: dict[str, Connector], client: str, db_path=None) -> tuple[dict, list[str]]:
    """Pull every dataset any connector offers, map columns, return (data, notes)."""
    data, notes = {}, []
    for cname, cn in connectors.items():
        for ds in cn.datasets():
            if ds not in dt.REQUIRED:
                notes.append(f"{cname}: ignored unknown dataset '{ds}'.")
                continue
            try:
                raw = cn.fetch(ds)
                saved = store.load_mapping(client, ds, db_path)
                df, m, missing = mp.auto_ingest(ds, raw, saved)
                if df is None:
                    notes.append(f"{cname}/{ds}: needs column mapping for {', '.join(missing)}.")
                    continue
                store.save_mapping(client, ds, m, db_path)
                data[ds] = df
                notes.append(f"{cname}/{ds}: {len(df):,} rows loaded.")
            except Exception as e:
                notes.append(f"{cname}/{ds}: FAILED {type(e).__name__}: {e}")
    return data, notes


def per_finding_snapshot(findings, cfg) -> dict:
    return {f.key: {"annual": round(f.annualised_inr, 2), "addressable": round(f.addressable(cfg), 2),
                    "flagged": int(f.rows_flagged), "tier": f.tier} for f in findings}


def analyse_and_save(client: str, data: dict, cfg: dict, data_basis: str, sector: str = "", db_path=None):
    findings, notes = dt.run_all(data, cfg)
    summary = dt.summarise(findings, cfg)
    fp, _ = dt.build_fingerprint(client, data_basis, data, cfg, findings)
    store.upsert_client(client, sector, db_path)
    run_id = store.save_run(client, data_basis, fp, summary, cfg, per_finding_snapshot(findings, cfg), db_path)
    return {"findings": findings, "notes": notes, "summary": summary, "fingerprint": fp, "run_id": run_id}


def compare_with_previous(client: str, findings, cfg, db_path=None, threshold_pct: float = 10.0) -> list[str]:
    """Alerts for the monitor: new rules firing or rules that worsened since the previous run."""
    runs = store.list_runs(client, 2, db_path)
    if len(runs) < 2:
        return []
    prev = runs[1]["payload"].get("per_finding", {})
    alerts = []
    for f in findings:
        old = prev.get(f.key)
        if old is None and f.rows_flagged:
            alerts.append(f"NEW: {f.title} now flags {f.rows_flagged} items ({dt.inr(f.annualised_inr)}/yr).")
        elif old and old["annual"] > 0:
            chg = (f.annualised_inr / old["annual"] - 1) * 100
            if chg >= threshold_pct:
                alerts.append(f"WORSE: {f.title} up {chg:.0f}% to {dt.inr(f.annualised_inr)}/yr.")
    return alerts
