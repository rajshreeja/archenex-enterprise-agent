"""
Hand-off of APPROVED actions to the owning team (Slack / Teams / generic webhook).

Safe by default: dry-run unless a webhook is configured AND the caller passes dry_run=False.
This sends a message to a human. It never writes to HRIS, payroll or ERP.
"""
from __future__ import annotations

import json

from .detectors import inr


def build_payload(action: dict, client: str, reviewer: str, kind: str = "slack") -> dict:
    line = (f"*{action['title']}*\nOwner: {action['owner']} · Est. impact {inr(action.get('impact_inr_annual', 0))}/yr\n"
            f"{action['detail']}\n_Approved by {reviewer or 'reviewer'} for {client} via ArcheNex._")
    if kind == "teams":
        return {"@type": "MessageCard", "@context": "https://schema.org/extensions",
                "summary": action["title"], "themeColor": "1E3A8A", "text": line.replace("*", "**")}
    if kind == "generic":
        return {"client": client, "approved_by": reviewer, "action": action}
    return {"text": line}


def send(action: dict, client: str, reviewer: str, webhook_url: str | None, kind: str = "slack",
         dry_run: bool = True) -> dict:
    payload = build_payload(action, client, reviewer, kind)
    if dry_run or not webhook_url:
        return {"sent": False, "dry_run": True, "payload": payload}
    from .connectors.rest_connector import check_url
    check_url(webhook_url)
    import requests
    r = requests.post(webhook_url, data=json.dumps(payload), headers={"Content-Type": "application/json"}, timeout=15)
    return {"sent": r.ok, "status": r.status_code, "dry_run": False, "payload": payload}
