"""
Charts. Plotly figures for the interactive app, matplotlib twins for the PDF.
Everything is drawn from findings; no placeholder data.
"""
from __future__ import annotations

import io

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.graph_objects as go

from detectors import Finding

NAVY, BLUE, SLATE, RED, GREEN, AMBER = "#1e3a8a", "#2563eb", "#94a3b8", "#dc2626", "#16a34a", "#d97706"
_LAYOUT = dict(template="plotly_white", font=dict(family="Inter, Arial", size=12),
               margin=dict(l=10, r=10, t=44, b=10))


def short(f: Finding) -> str:
    return f.title.split(" (")[0]


def _prim(findings):
    return [f for f in findings if f.tier == "primary" and len(f.evidence)]


# ============================================================ plotly (interactive)
def waterfall(findings, cfg, summary) -> go.Figure:
    prim = [f for f in findings if f.tier == "primary"]
    ident = summary["identified_annual"] / 1e5
    unreal = (summary["identified_annual"] - summary["addressable_annual"]) / 1e5
    fee = summary["fee"] / 1e5
    net = summary["addressable_annual"] / 1e5 - fee
    fig = go.Figure(go.Waterfall(
        x=["Identified leakage", "Not recoverable", "Addressable", "Platform fee", "Net benefit"],
        measure=["absolute", "relative", "total", "relative", "total"],
        y=[ident, -unreal, 0, -fee, 0],
        text=[f"₹{ident:,.0f} L", f"-₹{unreal:,.0f} L", f"₹{ident - unreal:,.0f} L", f"-₹{fee:,.0f} L", f"₹{net:,.0f} L"],
        textposition="outside",
        increasing=dict(marker=dict(color=NAVY)), decreasing=dict(marker=dict(color=RED)),
        totals=dict(marker=dict(color=GREEN)), connector=dict(line=dict(color=SLATE))))
    fig.update_layout(title="From leakage to net benefit (₹ Lakhs / year)", showlegend=False, **_LAYOUT)
    return fig


def pareto(f: Finding, col: str, top: int = 12) -> go.Figure:
    g = f.evidence.groupby(col)["impact_inr"].sum().sort_values(ascending=False).head(top)
    cum = g.cumsum() / g.sum() * 100
    fig = go.Figure()
    fig.add_bar(x=g.index.astype(str), y=g.values / 1e5, name="₹ Lakhs", marker_color=NAVY)
    fig.add_scatter(x=g.index.astype(str), y=cum.values, name="Cumulative %", yaxis="y2",
                    mode="lines+markers", line=dict(color=AMBER))
    fig.update_layout(title=f"Pareto: {short(f)} by {col}", yaxis=dict(title="₹ Lakhs (in window)"),
                      yaxis2=dict(title="Cumulative %", overlaying="y", side="right", range=[0, 105]),
                      legend=dict(orientation="h", y=-0.2), **_LAYOUT)
    return fig


def heatmap(f: Finding) -> go.Figure | None:
    ev = f.evidence
    if ev.empty or not {"cell", "shift"} <= set(ev.columns):
        return None
    h = ev.pivot_table(index="cell", columns="shift", values="impact_inr", aggfunc="sum").fillna(0) / 1e5
    fig = go.Figure(go.Heatmap(z=h.values, x=[f"Shift {c}" for c in h.columns], y=h.index,
                               colorscale="Blues", text=np.round(h.values, 1), texttemplate="%{text}",
                               hovertemplate="%{y} / %{x}: ₹%{z:.1f} L<extra></extra>"))
    fig.update_layout(title="Hotspot map: cell × shift (₹ Lakhs in window)", **_LAYOUT)
    return fig


def weekly_trend(findings) -> go.Figure:
    fig = go.Figure()
    for f in _prim(findings):
        d = pd.to_datetime(f.evidence["date"])
        w = f.evidence.groupby(d.dt.to_period("W").dt.start_time)["impact_inr"].sum().sort_index() / 1e5
        if len(w) >= 3:
            fig.add_scatter(x=w.index, y=w.values, mode="lines", name=short(f), stackgroup="one")
    fig.update_layout(title="Weekly leakage by rule (₹ Lakhs, stacked)", legend=dict(orientation="h", y=-0.25),
                      **_LAYOUT)
    return fig


def sankey(findings, cfg) -> go.Figure:
    """Source system → rule → owning function, sized by annual addressable ₹."""
    prim = _prim(findings)
    srcs, rules, owners = [], [], []
    for f in prim:
        srcs.append(f.silos)
        rules.append(short(f))
        owners.append(f.owner or "Function head")
    labels = list(dict.fromkeys(srcs)) + rules + list(dict.fromkeys(owners))
    idx = {l: i for i, l in enumerate(labels)}
    s, t, v = [], [], []
    for f, src, rule, own in zip(prim, srcs, rules, owners):
        val = max(f.addressable(cfg), 1.0) / 1e5
        s += [idx[src], idx[rule]]
        t += [idx[rule], idx[own]]
        v += [val, val]
    fig = go.Figure(go.Sankey(
        node=dict(label=labels, pad=14, thickness=14, color=[NAVY] * len(labels)),
        link=dict(source=s, target=t, value=v, color="rgba(37,99,235,0.25)")))
    fig.update_layout(title="Where the money flows: system → rule → owner (₹ Lakhs addressable / year)",
                      **_LAYOUT)
    return fig


def treemap(findings, cfg) -> go.Figure:
    rows = []
    for f in _prim(findings):
        g = f.evidence.groupby("where")["impact_inr"].sum().sort_values(ascending=False).head(8)
        for k, v in g.items():
            rows.append((short(f), str(k), float(v)))
    d = pd.DataFrame(rows, columns=["rule", "loc", "v"])
    fig = go.Figure(go.Treemap(
        labels=list(d.rule.unique()) + list(d["loc"] + " · " + d["rule"]),
        parents=[""] * d.rule.nunique() + list(d.rule),
        values=[0] * d.rule.nunique() + list(d.v), branchvalues="remainder",
        marker=dict(colorscale="Blues")))
    fig.update_layout(title="Cost map: rule → location", **_LAYOUT)
    return fig


def milestone_bubble(f: Finding) -> go.Figure:
    ev = f.evidence
    fig = go.Figure(go.Scatter(
        x=ev.delay_days, y=ev.value_inr / 1e5, mode="markers",
        marker=dict(size=np.clip(ev.impact_inr / ev.impact_inr.max() * 40 + 6, 6, 46),
                    color=np.where(ev.status == "UNBILLED", RED, BLUE), opacity=0.65),
        text=ev.project + " · " + ev.client, hovertemplate="%{text}<br>%{x} days late<br>₹%{y:.1f} L<extra></extra>"))
    fig.update_layout(title="Milestones: value vs days late (red = still unbilled)",
                      xaxis_title="Days beyond grace period", yaxis_title="Milestone value (₹ Lakhs)", **_LAYOUT)
    return fig


def risk_scatter(f: Finding) -> go.Figure:
    ev = f.evidence
    fig = go.Figure(go.Scatter(
        x=ev.tenure_y, y=ev.pay_ratio, mode="markers",
        marker=dict(size=np.clip(ev.ctc_inr / 1e5 * 2, 5, 30), color=ev.score, colorscale="OrRd",
                    colorbar=dict(title="Score"), opacity=0.7),
        text=ev.employee_id, hovertemplate="%{text}<br>tenure %{x}y<br>pay vs dept median %{y}<extra></extra>"))
    fig.update_layout(title="Retention watch-list: tenure vs pay position (size = CTC)",
                      xaxis_title="Tenure (years)", yaxis_title="Pay ÷ department median", **_LAYOUT)
    return fig


def bar_by(f: Finding, col: str, color=NAVY) -> go.Figure:
    g = f.evidence.groupby(col)["impact_inr"].sum().sort_values() / 1e5
    fig = go.Figure(go.Bar(x=g.values, y=g.index.astype(str), orientation="h", marker_color=color))
    fig.update_layout(title=f"{short(f)} by {col} (₹ Lakhs in window)", **_LAYOUT)
    return fig


# ================================================================ matplotlib (PDF)
def _png(fig) -> io.BytesIO:
    plt.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=190)
    plt.close(fig)
    buf.seek(0)
    return buf


def _clean(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.tick_params(labelsize=7)


def mpl_rule_bars(findings, cfg) -> io.BytesIO:
    prim = [f for f in findings if f.tier == "primary"]
    names = [short(f) for f in prim]
    fig, ax = plt.subplots(figsize=(7.2, 3.0))
    y = np.arange(len(prim))
    ax.barh(y + 0.2, [f.annualised_inr / 1e5 for f in prim], 0.38, color=SLATE, label="Identified (annual)")
    ax.barh(y - 0.2, [f.addressable(cfg) / 1e5 for f in prim], 0.38, color=NAVY, label="Addressable (annual)")
    ax.set_yticks(y); ax.set_yticklabels(names, fontsize=7); ax.invert_yaxis()
    ax.set_xlabel("₹ Lakhs per year", fontsize=7); ax.legend(fontsize=7, frameon=False, loc="lower right")
    _clean(ax)
    return _png(fig)


def mpl_waterfall(summary) -> io.BytesIO:
    ident = summary["identified_annual"] / 1e5
    addr = summary["addressable_annual"] / 1e5
    fee = summary["fee"] / 1e5
    steps = [("Identified", 0, ident, NAVY), ("Not recoverable", addr, ident - addr, RED),
             ("Addressable", 0, addr, GREEN), ("Platform fee", addr - fee, fee, RED),
             ("Net benefit", 0, addr - fee, GREEN)]
    fig, ax = plt.subplots(figsize=(7.2, 2.8))
    for i, (lab, bottom, h, c) in enumerate(steps):
        ax.bar(i, h, bottom=bottom, color=c, width=0.6)
        ax.text(i, bottom + h + ident * 0.02, f"₹{h:,.0f} L", ha="center", fontsize=7)
    ax.set_xticks(range(len(steps))); ax.set_xticklabels([s[0] for s in steps], fontsize=7)
    ax.set_ylabel("₹ Lakhs / year", fontsize=7); _clean(ax)
    return _png(fig)


def mpl_pareto(f: Finding, col: str, top: int = 10) -> io.BytesIO:
    g = f.evidence.groupby(col)["impact_inr"].sum().sort_values(ascending=False).head(top)
    cum = g.cumsum() / g.sum() * 100
    fig, ax = plt.subplots(figsize=(7.2, 2.8))
    ax.bar(range(len(g)), g.values / 1e5, color=NAVY)
    ax.set_xticks(range(len(g))); ax.set_xticklabels([str(i)[:16] for i in g.index], rotation=30, ha="right", fontsize=7)
    ax.set_ylabel("₹ Lakhs (in window)", fontsize=7); _clean(ax)
    ax2 = ax.twinx(); ax2.plot(range(len(g)), cum.values, color=AMBER, marker="o", ms=3)
    ax2.set_ylim(0, 105); ax2.tick_params(labelsize=7); ax2.set_ylabel("Cumulative %", fontsize=7)
    ax2.spines["top"].set_visible(False)
    return _png(fig)


def mpl_heatmap(f: Finding) -> io.BytesIO | None:
    ev = f.evidence
    if ev.empty or not {"cell", "shift"} <= set(ev.columns):
        return None
    h = ev.pivot_table(index="cell", columns="shift", values="impact_inr", aggfunc="sum").fillna(0) / 1e5
    fig, ax = plt.subplots(figsize=(5.6, 2.8))
    im = ax.imshow(h.values, cmap="Blues", aspect="auto")
    ax.set_xticks(range(h.shape[1])); ax.set_xticklabels([f"Shift {c}" for c in h.columns], fontsize=7)
    ax.set_yticks(range(h.shape[0])); ax.set_yticklabels(h.index, fontsize=7)
    for i in range(h.shape[0]):
        for j in range(h.shape[1]):
            v = h.values[i, j]
            ax.text(j, i, f"{v:.1f}", ha="center", va="center", fontsize=7,
                    color="white" if v > h.values.max() * 0.55 else "black")
    fig.colorbar(im, ax=ax, label="₹ Lakhs", shrink=0.8)
    return _png(fig)


def mpl_trend(findings) -> io.BytesIO | None:
    prim = _prim(findings)
    fig, ax = plt.subplots(figsize=(7.2, 2.8))
    drawn = 0
    for f in prim:
        d = pd.to_datetime(f.evidence["date"])
        w = f.evidence.groupby(d.dt.to_period("W").dt.start_time)["impact_inr"].sum().sort_index() / 1e5
        if len(w) >= 3:
            ax.plot(w.index, w.values, lw=1.2, label=short(f)); drawn += 1
    if not drawn:
        plt.close(fig); return None
    ax.legend(fontsize=6, frameon=False, ncol=2); ax.set_ylabel("₹ Lakhs / week", fontsize=7); _clean(ax)
    fig.autofmt_xdate()
    return _png(fig)
