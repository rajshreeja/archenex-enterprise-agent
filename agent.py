"""
ArcheNex agent layer.

Design principle: DETECT with transparent rules, RECOMMEND actions, and let a HUMAN
approve every one. Every decision is logged. ArcheNex never changes payroll, ERP or
HRIS data on its own in this version; execution stays with the client's teams until
write-back connectors are deliberately enabled.
"""
from __future__ import annotations

import json
import os
import re

import pandas as pd

from detectors import Finding, inr


def _factor(f: Finding) -> float:
    """Scale factor from in-window cost to annual cost."""
    return f.annualised_inr / f.observed_inr if f.observed_inr > 0 else 0.0


def recommend_actions(findings: list[Finding], cfg: dict) -> list[dict]:
    actions: list[dict] = []
    by_key = {f.key: f for f in findings}

    f = by_key.get("idle_staging")
    if f is not None and len(f.evidence):
        g = (f.evidence.groupby(["cell", "shift"])
             .agg(cost=("impact_inr", "sum"), hours=("idle_hours", "sum"), events=("impact_inr", "size"))
             .sort_values("cost", ascending=False).head(3).reset_index())
        for i, r in g.iterrows():
            actions.append({
                "id": f"idle_staging-{i}", "detector": f.key, "owner": "Plant Head / Supply Chain",
                "title": f"Fix material staging at {r.cell}, Shift {r['shift']}",
                "detail": (f"{r.events} staging stoppages totalling {r.hours:.0f} idle hours cost about "
                           f"{inr(r.cost)} in labour in the data window. Review the material feed "
                           "schedule and redeploy crews during staging gaps."),
                "impact_inr_annual": float(r.cost * _factor(f)),
            })

    f = by_key.get("ghost_attendance")
    if f is not None and len(f.evidence):
        g = (f.evidence.groupby("cell")
             .agg(cost=("impact_inr", "sum"), n=("impact_inr", "size"))
             .sort_values("cost", ascending=False).head(3).reset_index())
        for i, r in g.iterrows():
            actions.append({
                "id": f"ghost_attendance-{i}", "detector": f.key, "owner": "HR Operations + Plant HR",
                "title": f"Reconcile paid shifts with no gate swipe in {r.cell}",
                "detail": (f"{r.n} paid shifts ({inr(r.cost)} in the window) have no gate-in record. "
                           "Check against biometric device logs and manual regularisations before "
                           "any payroll action."),
                "impact_inr_annual": float(r.cost * _factor(f)),
            })

    f = by_key.get("overtime_underutil")
    if f is not None and len(f.evidence):
        g = (f.evidence.groupby("cell")
             .agg(cost=("impact_inr", "sum"), n=("impact_inr", "size"), util=("utilisation_pct", "mean"))
             .sort_values("cost", ascending=False).head(3).reset_index())
        for i, r in g.iterrows():
            actions.append({
                "id": f"overtime_underutil-{i}", "detector": f.key, "owner": "Plant Head + Finance",
                "title": f"Review overtime approvals in {r.cell}",
                "detail": (f"{r.n} overtime entries ({inr(r.cost)}) were paid while the cell averaged "
                           f"{r.util:.0f}% utilisation. Tighten approval rules or confirm the backlog "
                           "justification."),
                "impact_inr_annual": float(r.cost * _factor(f)),
            })

    f = by_key.get("milestone_delay")
    if f is not None and len(f.evidence):
        top = f.evidence.sort_values("value_inr", ascending=False).head(5)
        for i, (_, r) in enumerate(top.iterrows()):
            actions.append({
                "id": f"milestone_delay-{i}", "detector": f.key, "owner": "Finance + Project Delivery",
                "title": f"Invoice or escalate {r.project} ({r.client})",
                "detail": (f"Signed off {r.date}; {r.status.lower()} after {r.lag_days} days; "
                           f"milestone value {inr(r.value_inr)}. Raise the invoice or escalate "
                           "the blocked approval."),
                "impact_inr_annual": float(r.impact_inr * _factor(f)),
            })

    f = by_key.get("orphaned_saas")
    if f is not None and len(f.evidence):
        g = (f.evidence.groupby("app")
             .agg(cost=("impact_inr", "sum"), n=("impact_inr", "size"))
             .sort_values("cost", ascending=False).head(3).reset_index())
        for i, r in g.iterrows():
            actions.append({
                "id": f"orphaned_saas-{i}", "detector": f.key, "owner": "IT + Finance",
                "title": f"Reclaim {r.n} unused {r.app} licences",
                "detail": (f"{r.n} seats are inactive or belong to exited employees, costing "
                           f"{inr(r.cost)} a year. Confirm they are not shared accounts, then reclaim."),
                "impact_inr_annual": float(r.cost),
            })

    f = by_key.get("payroll_after_exit")
    if f is not None and len(f.evidence):
        g = (f.evidence.groupby("department")
             .agg(cost=("impact_inr", "sum"), n=("impact_inr", "size"))
             .sort_values("cost", ascending=False).head(3).reset_index())
        for i, r in g.iterrows():
            actions.append({
                "id": f"payroll_after_exit-{i}", "detector": f.key, "owner": "HR Operations + Payroll",
                "title": f"Verify salary paid after exit in {r.department}",
                "detail": (f"{r.n} payroll lines ({inr(r.cost)} in the window) fall after the employee's exit "
                           "month. Check full-and-final settlement status, stop any open payments and "
                           "recover genuine overpayments."),
                "impact_inr_annual": float(r.cost * _factor(f)),
            })

    f = by_key.get("duplicate_payments")
    if f is not None and len(f.evidence):
        g = (f.evidence.groupby("vendor")
             .agg(cost=("impact_inr", "sum"), n=("impact_inr", "size"))
             .sort_values("cost", ascending=False).head(3).reset_index())
        for i, r in g.iterrows():
            actions.append({
                "id": f"duplicate_payments-{i}", "detector": f.key, "owner": "Accounts Payable + Procurement",
                "title": f"Recover suspected duplicate payments to {r.vendor}",
                "detail": (f"{r.n} invoices ({inr(r.cost)}) repeat an earlier payment. Confirm with the vendor "
                           "statement, request a credit note or refund, and add a duplicate check at entry."),
                "impact_inr_annual": float(r.cost * _factor(f)),
            })

    f = by_key.get("overtime_cap_breach")
    if f is not None and len(f.evidence):
        g = (f.evidence.groupby("cell")
             .agg(cost=("impact_inr", "sum"), n=("impact_inr", "size"))
             .sort_values("cost", ascending=False).head(3).reset_index())
        for i, r in g.iterrows():
            actions.append({
                "id": f"overtime_cap_breach-{i}", "detector": f.key, "owner": "Plant Head + HR Operations",
                "title": f"Cap and re-plan weekly overtime in {r.cell}",
                "detail": (f"{r.n} employee-weeks exceeded the overtime cap ({inr(r.cost)} above cap). "
                           "Spread the load across more people or fix the backlog source; also a fatigue and "
                           "safety signal."),
                "impact_inr_annual": float(r.cost * _factor(f)),
            })

    f = by_key.get("flight_risk")
    if f is not None and len(f.evidence):
        g = (f.evidence.groupby("department")
             .agg(cost=("impact_inr", "sum"), n=("impact_inr", "size"))
             .sort_values("cost", ascending=False).head(2).reset_index())
        for i, r in g.iterrows():
            actions.append({
                "id": f"flight_risk-{i}", "detector": f.key, "owner": "HR Business Partners",
                "title": f"Hold stay conversations in {r.department} (secondary)",
                "detail": (f"{r.n} people score high on the retention watch-list; expected replacement cost "
                           f"is about {inr(r.cost)}. Prioritise career and pay conversations for top performers."),
                "impact_inr_annual": float(r.cost),
            })

    return sorted(actions, key=lambda a: a["impact_inr_annual"], reverse=True)


def audit_trail_df(log: list[dict]) -> pd.DataFrame:
    cols = ["timestamp", "reviewer", "action_id", "action", "decision"]
    return pd.DataFrame(log, columns=cols) if log else pd.DataFrame(columns=cols)


def summary_text(findings: list[Finding], summary: dict) -> str:
    """Aggregated numbers only (no employee IDs or e-mails): safe to send to an LLM."""
    lines = [f"Total identified annual leakage: {inr(summary['identified_annual'])}",
             f"Realistically addressable: {inr(summary['addressable_annual'])}"]
    for f in findings:
        tag = " (secondary, not in headline)" if f.tier != "primary" else ""
        lines.append(f"- {f.title}{tag}: {f.rows_flagged} items flagged, annualised {inr(f.annualised_inr)}. "
                     f"Method: {f.method}")
    return "\n".join(lines)


# ------------------------------------------------------------------ LLM layer
MODEL = os.environ.get("ARCHENEX_MODEL", "claude-sonnet-5-5")

_NUM = re.compile(r"\d[\d,]*\.?\d*")


def _numbers(text: str) -> set[str]:
    out = set()
    for m in _NUM.findall(text):
        m = m.replace(",", "").rstrip(".")
        if m:
            out.add(m)
            try:
                v = float(m)
                out.add(f"{v:.2f}".rstrip("0").rstrip("."))
                out.add(f"{v:.1f}".rstrip("0").rstrip("."))
                out.add(str(int(round(v))))
            except ValueError:
                pass
    return out


def check_grounding(answer: str, evidence_texts: list[str]) -> list[str]:
    """Figures in the answer that never appeared in any tool output. Best-effort guard rail."""
    allowed: set[str] = set()
    for t in evidence_texts:
        allowed |= _numbers(t)
    bad = []
    for n in _numbers(answer):
        try:
            v = float(n)
        except ValueError:
            continue
        if v <= 12 or n in allowed:          # small counts and years of ordinary prose are not checked
            continue
        if 1900 <= v <= 2100:
            continue
        bad.append(n)
    return sorted(set(bad), key=lambda x: float(x))


def ai_brief(text: str, api_key: str, client=None) -> str:
    """Optional: plain-English CFO brief written from AGGREGATED numbers only."""
    try:
        if client is None:
            import anthropic
            client = anthropic.Anthropic(api_key=api_key)
        msg = client.messages.create(
            model=MODEL, max_tokens=800,
            system=("You write concise briefings for a CFO. Use ONLY the numbers provided. Do not invent "
                    "figures, causes or benchmarks. Say that realisation rates are planning assumptions. "
                    "Finish with the 3 most valuable next steps."),
            messages=[{"role": "user", "content": text}])
        out = "".join(b.text for b in msg.content if getattr(b, "type", "") == "text")
        bad = check_grounding(out, [text])
        if bad:
            out += ("\n\n> Check before sharing: these figures do not appear in the source numbers: "
                    + ", ".join(bad))
        return out
    except Exception as e:
        return f"AI brief unavailable: {type(e).__name__}: {e}"


TOOLS = [
    {"name": "get_summary", "description": "Headline numbers: identified, addressable, ROI, one-time cash.",
     "input_schema": {"type": "object", "properties": {}}},
    {"name": "list_findings", "description": "List every rule with flagged count and annual rupee impact.",
     "input_schema": {"type": "object", "properties": {}}},
    {"name": "drill_down",
     "description": "Group one rule's flagged rows by a column and return the top contributors in rupees.",
     "input_schema": {"type": "object", "properties": {
         "finding_key": {"type": "string"}, "group_by": {"type": "string"},
         "top_n": {"type": "integer", "default": 5}}, "required": ["finding_key", "group_by"]}},
    {"name": "what_if",
     "description": "Recompute addressable savings if a rule's realisation percentage were different.",
     "input_schema": {"type": "object", "properties": {
         "finding_key": {"type": "string"}, "realisation_pct": {"type": "number"}},
         "required": ["finding_key", "realisation_pct"]}},
    {"name": "propose_action",
     "description": ("Propose a follow-up action for a named owner. This only QUEUES a proposal for a human to "
                     "approve; nothing is executed."),
     "input_schema": {"type": "object", "properties": {
         "title": {"type": "string"}, "owner": {"type": "string"}, "detail": {"type": "string"},
         "finding_key": {"type": "string"}}, "required": ["title", "owner", "detail"]}},
]

SYSTEM = ("You are ArcheNex Copilot, an analyst for a CFO / COO. Answer ONLY from tool results. "
          "Never invent a figure, benchmark or cause; if the data does not say, say so. Quote rupee figures "
          "exactly as returned. Findings are exceptions to review, not proof of wrongdoing. You may call "
          "propose_action to queue a suggestion, but you can never execute or approve anything. Keep answers "
          "short and decision-oriented.")


class Copilot:
    """Tool-using agent. Reads findings through tools; proposals need a human to approve them."""

    def __init__(self, findings, summary, cfg, api_key: str | None = None, client=None, max_turns: int = 6):
        self.findings, self.summary, self.cfg = findings, summary, cfg
        self.proposals: list[dict] = []
        self.evidence: list[str] = []
        self.max_turns = max_turns
        if client is None and api_key:
            import anthropic
            client = anthropic.Anthropic(api_key=api_key)
        self.client = client

    # ---- tools (deterministic, local) ----
    def call_tool(self, name: str, args: dict) -> dict:
        fs = {f.key: f for f in self.findings}
        if name == "get_summary":
            s = self.summary
            return {"identified_annual": inr(s["identified_annual"]), "addressable_annual": inr(s["addressable_annual"]),
                    "return_on_fee": f"{s['roi_multiple']:.1f}x", "one_time_cash_release": inr(s["one_time_cash_release"]),
                    "one_time_recovery": inr(s.get("one_time_recovery", 0.0)),
                    "secondary_identified": inr(s.get("secondary_identified", 0.0))}
        if name == "list_findings":
            return {"findings": [{"key": f.key, "title": f.title, "tier": f.tier, "flagged": f.rows_flagged,
                                  "annual": inr(f.annualised_inr), "addressable": inr(f.addressable(self.cfg)),
                                  "owner": f.owner} for f in self.findings]}
        if name == "drill_down":
            f = fs.get(args.get("finding_key"))
            if f is None:
                return {"error": f"unknown finding_key; use one of {sorted(fs)}"}
            col = args.get("group_by")
            if col not in f.evidence.columns:
                return {"error": f"group_by must be one of {list(f.evidence.columns)}"}
            g = (f.evidence.groupby(col)["impact_inr"].agg(["sum", "size"])
                 .sort_values("sum", ascending=False).head(int(args.get("top_n", 5))))
            scale = (f.annualised_inr / f.observed_inr) if f.observed_inr > 0 else 0.0
            return {"group_by": col, "rows": [{col: str(k), "items": int(r["size"]), "in_window": inr(r["sum"]),
                                               "annualised": inr(r["sum"] * scale)} for k, r in g.iterrows()]}
        if name == "what_if":
            from .insights import scenario
            r = scenario(self.findings, self.cfg, {args["finding_key"]: float(args["realisation_pct"])})
            return {"base_addressable": inr(r["base_addressable"]), "scenario_addressable": inr(r["scenario_addressable"]),
                    "change": inr(r["delta"]), "return_on_fee": f"{r['roi_multiple']:.1f}x"}
        if name == "propose_action":
            p = {"id": f"copilot-{len(self.proposals) + 1}", "detector": args.get("finding_key", "copilot"),
                 "owner": str(args.get("owner", ""))[:80], "title": str(args.get("title", ""))[:140],
                 "detail": str(args.get("detail", ""))[:600], "impact_inr_annual": 0.0, "source": "copilot"}
            self.proposals.append(p)
            return {"queued_for_human_approval": p["title"]}
        return {"error": f"unknown tool {name}"}

    # ---- loop ----
    def ask(self, question: str, history: list[dict] | None = None) -> dict:
        if self.client is None:
            return {"answer": "Copilot needs an ANTHROPIC_API_KEY (add it in Secrets).", "unverified": [], "tools_used": []}
        msgs = list(history or []) + [{"role": "user", "content": question}]
        used: list[str] = []
        try:
            for _ in range(self.max_turns):
                resp = self.client.messages.create(model=MODEL, max_tokens=900, system=SYSTEM,
                                                   tools=TOOLS, messages=msgs)
                if getattr(resp, "stop_reason", "") != "tool_use":
                    text = "".join(b.text for b in resp.content if getattr(b, "type", "") == "text")
                    return {"answer": text, "unverified": check_grounding(text, self.evidence), "tools_used": used}
                msgs.append({"role": "assistant", "content": resp.content})
                results = []
                for b in resp.content:
                    if getattr(b, "type", "") == "tool_use":
                        out = self.call_tool(b.name, dict(b.input or {}))
                        used.append(b.name)
                        s = json.dumps(out, default=str, ensure_ascii=False)
                        self.evidence.append(s)
                        results.append({"type": "tool_result", "tool_use_id": b.id, "content": s})
                msgs.append({"role": "user", "content": results})
            return {"answer": "Stopped after too many tool calls. Try a narrower question.", "unverified": [], "tools_used": used}
        except Exception as e:
            return {"answer": f"Copilot unavailable: {type(e).__name__}: {e}", "unverified": [], "tools_used": used}
