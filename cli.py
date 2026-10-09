"""
Command line: scheduled monitoring and demos.

  python -m archenex.cli demo                      # run the synthetic demo and print the headline
  python -m archenex.cli monitor --config connections.json --client "Acme Pvt Ltd" [--webhook URL] [--send]

`monitor` pulls fresh data through the connectors, re-runs every rule, saves the run, compares with
the previous run and (optionally) posts alerts to a Slack/Teams webhook. Schedule it with cron or the
GitHub Actions workflow in docs/DEPLOY.md.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

from . import detectors as dt
from . import pipeline
from .connectors import build_connectors
from .dispatch import send


def _cfg(path: str | None) -> dict:
    cfg = json.loads(json.dumps(dt.DEFAULT_CONFIG))
    if path:
        cfg.update(json.load(open(path)))
    return cfg


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="archenex")
    sub = ap.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("demo")
    m = sub.add_parser("monitor")
    m.add_argument("--config", required=True, help="connections JSON (see connections.example.json)")
    m.add_argument("--client", required=True)
    m.add_argument("--assumptions", help="optional JSON overriding default assumptions")
    m.add_argument("--webhook", default=os.environ.get("ARCHENEX_WEBHOOK"))
    m.add_argument("--webhook-kind", default="slack", choices=["slack", "teams", "generic"])
    m.add_argument("--send", action="store_true", help="actually post alerts (default is dry-run)")
    a = ap.parse_args(argv)

    if a.cmd == "demo":
        from .demo_data import make_demo
        cfg = _cfg(None)
        res = pipeline.analyse_and_save("Demo (synthetic)", make_demo(), cfg, "SYNTHETIC DEMO DATA")
        s = res["summary"]
        print(f"Identified {dt.inr(s['identified_annual'])} / yr · addressable {dt.inr(s['addressable_annual'])} "
              f"· {s['rows_flagged']:,} items flagged")
        for f in res["findings"]:
            print(f"  - {f.title}: {dt.inr(f.annualised_inr)}")
        return 0

    cfg = _cfg(a.assumptions)
    conns = build_connectors(open(a.config).read())
    data, notes = pipeline.ingest(conns, a.client)
    for n in notes:
        print(n)
    if not data:
        print("No data loaded; nothing to analyse.")
        return 2
    res = pipeline.analyse_and_save(a.client, data, cfg, "Live connectors")
    alerts = pipeline.compare_with_previous(a.client, res["findings"], cfg)
    s = res["summary"]
    print(f"Run {res['run_id']}: identified {dt.inr(s['identified_annual'])} / yr, addressable "
          f"{dt.inr(s['addressable_annual'])}.")
    for al in alerts:
        print("ALERT", al)
    if alerts:
        action = {"title": f"ArcheNex monitor: {len(alerts)} change(s) for {a.client}", "owner": "CFO office",
                  "detail": "\n".join(alerts), "impact_inr_annual": s["addressable_annual"]}
        out = send(action, a.client, "monitor", a.webhook, a.webhook_kind, dry_run=not a.send)
        print("Alert delivery:", "sent" if out.get("sent") else "dry-run (use --send with a webhook)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
