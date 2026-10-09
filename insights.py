"""
Deterministic insight engine.

Turns raw findings into the "so what" a CFO / COO actually reads: where the money is
concentrated, whether it is getting better or worse, and which places show up in several
rules at once (the cross-silo insights that no single system can produce).

Every number is computed from the flagged rows; nothing here is invented or random.
"""
from __future__ import annotations

import pandas as pd

from detectors import Finding, inr


def _weekly(ev: pd.DataFrame) -> pd.Series:
    if ev.empty:
        return pd.Series(dtype=float)
    d = pd.to_datetime(ev["date"])
    return ev.groupby(d.dt.to_period("W").dt.start_time)["impact_inr"].sum().sort_index()


def trend(f: Finding) -> dict | None:
    """Compare the last 4 full weeks with the 4 weeks before. None if the window is too short."""
    w = _weekly(f.evidence)
    if len(w) < 9:
        return None
    w = w.iloc[:-1]                         # drop the (usually partial) last week
    last, prev = w.iloc[-4:].sum(), w.iloc[-8:-4].sum()
    if prev <= 0:
        return None
    return {"last4": float(last), "prev4": float(prev), "change_pct": float((last / prev - 1) * 100)}


def concentration(f: Finding, col: str) -> dict | None:
    ev = f.evidence
    if ev.empty or col not in ev.columns:
        return None
    g = ev.groupby(col)["impact_inr"].sum().sort_values(ascending=False)
    tot = g.sum()
    if tot <= 0:
        return None
    cum = g.cumsum() / tot
    n80 = int((cum < 0.8).sum() + 1)
    return {"top": str(g.index[0]), "top_share_pct": float(g.iloc[0] / tot * 100),
            "n_items": int(len(g)), "n_for_80pct": n80, "top3": [(str(k), float(v)) for k, v in g.head(3).items()]}


_DIM = {"idle_staging": "cell", "ghost_attendance": "cell", "overtime_underutil": "cell",
        "milestone_delay": "client", "orphaned_saas": "app", "payroll_after_exit": "department",
        "duplicate_payments": "vendor", "overtime_cap_breach": "cell", "flight_risk": "department"}
_DIM_NAME = {"cell": "cell", "client": "client", "app": "application", "department": "department",
             "vendor": "vendor"}


def per_finding(findings: list[Finding], cfg: dict) -> list[dict]:
    out = []
    for f in findings:
        if not len(f.evidence):
            continue
        dim = _DIM.get(f.key, "where")
        conc = concentration(f, dim)
        tr = trend(f)
        bits = []
        if conc:
            bits.append(f"{conc['top_share_pct']:.0f}% of the cost sits in one {_DIM_NAME.get(dim, dim)} "
                        f"({conc['top']}); {conc['n_for_80pct']} of {conc['n_items']} account for 80%.")
        if tr:
            word = "up" if tr["change_pct"] > 5 else "down" if tr["change_pct"] < -5 else "flat"
            bits.append(f"Last 4 weeks are {word} {abs(tr['change_pct']):.0f}% against the 4 weeks before "
                        f"({inr(tr['last4'])} vs {inr(tr['prev4'])}).")
        out.append({
            "key": f.key, "title": f.title, "tier": f.tier, "owner": f.owner,
            "annual": f.annualised_inr, "addressable": f.addressable(cfg),
            "concentration": conc, "trend": tr,
            "text": " ".join(bits) if bits else f"{f.rows_flagged} items flagged.",
        })
    return sorted(out, key=lambda x: x["annual"], reverse=True)


def compound_hotspots(findings: list[Finding], top: int = 5) -> pd.DataFrame:
    """Cells that carry cost in more than one rule: the cross-silo insight."""
    frames = []
    for f in findings:
        ev = f.evidence
        if "cell" in ev.columns and len(ev):
            g = ev.groupby("cell")["impact_inr"].sum().rename(f.key)
            frames.append(g)
    if len(frames) < 2:
        return pd.DataFrame()
    m = pd.concat(frames, axis=1).fillna(0.0)
    m["rules_hit"] = (m > 0).sum(axis=1)
    m["total_inr"] = m.drop(columns="rules_hit").sum(axis=1)
    m = m[m.rules_hit >= 2].sort_values("total_inr", ascending=False).head(top)
    return m.reset_index().rename(columns={"index": "cell"})


def headline_insights(findings: list[Finding], summary: dict, cfg: dict) -> list[dict]:
    """Ranked list of plain-English insights, each with the number and the decision it triggers."""
    items: list[dict] = []
    pf = per_finding(findings, cfg)
    if pf:
        top = pf[0]
        items.append({
            "headline": f"{top['title'].split(' (')[0]} is the biggest leak at {inr(top['annual'])} a year.",
            "so_what": top["text"], "owner": top["owner"] or "Function head", "key": top["key"]})

    hot = compound_hotspots([f for f in findings if f.tier == "primary"])
    if len(hot):
        r = hot.iloc[0]
        rules = [c for c in hot.columns if c not in ("cell", "rules_hit", "total_inr") and r[c] > 0]
        items.append({
            "headline": f"{r['cell']} shows up in {int(r['rules_hit'])} separate rules ({inr(r['total_inr'])} in the window).",
            "so_what": ("No single system shows this: the same cell is idle, paying overtime and "
                        f"carrying attendance gaps at once. Rules hit: {', '.join(rules)}."),
            "owner": "Plant Head", "key": "compound"})

    idle = next((f for f in findings if f.key == "idle_staging" and len(f.evidence)), None)
    ot = next((f for f in findings if f.key == "overtime_underutil" and len(f.evidence)), None)
    if idle is not None and ot is not None:
        both = set(idle.evidence["cell"]) & set(ot.evidence["cell"])
        if both:
            items.append({
                "headline": f"{len(both)} cells pay for idle crews AND overtime in the same period.",
                "so_what": ("Crews wait on material in one shift while overtime is booked in another. "
                            "Rebalancing shift rosters is cheaper than either fix alone."),
                "owner": "Plant Head + Supply Chain", "key": "idle_plus_ot"})

    sec = [f for f in findings if f.tier == "secondary" and len(f.evidence)]
    for f in sec:
        items.append({
            "headline": f"Secondary view: {f.rows_flagged} people on the retention watch-list "
                        f"({inr(f.annualised_inr)} expected replacement cost).",
            "so_what": "Not counted in the headline. Use it to prioritise stay conversations.",
            "owner": f.owner, "key": f.key})

    one = summary.get("one_time_cash_release", 0.0)
    if one > 0:
        items.append({
            "headline": f"{inr(one)} of signed-off milestones are still unbilled.",
            "so_what": "One-time cash release, kept out of the annual savings number on purpose.",
            "owner": "Finance + Project Delivery", "key": "unbilled"})
    return items


def scenario(findings: list[Finding], cfg: dict, overrides: dict[str, float]) -> dict:
    """What-if on realisation rates. overrides: {finding_key: realisation_pct}."""
    base = new = 0.0
    for f in findings:
        if f.tier != "primary":
            continue
        base += f.addressable(cfg)
        pct = overrides.get(f.key, cfg["realisation_pct"].get(f.key, 0.0))
        new += f.annualised_inr * pct / 100.0
    fee = float(cfg["annual_fee_inr"])
    return {"base_addressable": base, "scenario_addressable": new, "delta": new - base,
            "roi_multiple": new / fee if fee else 0.0}
