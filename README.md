# ArcheNex Enterprise Agent (v3)

Finds money leaking between a mid-size company's plant, HR and finance systems, proves every rupee
back to the flagged rows, and turns each finding into an owner-assigned action that a person approves.

**Positioning:** ArcheNex is *not* an ERP. It is the intelligence and action layer that sits on top of the
client's SAP / Tally / Zoho / Darwinbox / Keka and joins the data those systems keep apart. See
`docs/COMMERCIAL_PLAYBOOK.md`.

## What is new in v3
| Area | v2 | v3 |
|---|---|---|
| Data in | 4 fixed CSV templates | 7 datasets; **any column names** via a mapping screen that remembers per client; read-only **SQL** and **REST** connectors; folder/file connector |
| Rules | 5 | **9** (adds salary-after-exit, duplicate vendor payments, overtime above weekly cap, retention watch-list as a *secondary* view) |
| Insights | totals | concentration, 4-week trend, compound hotspots (cells hit by several rules), what-if scenarios |
| Charts | bars | waterfall, Sankey (system → rule → owner), treemap, Pareto, heatmap, stacked weekly trend, bubble and scatter plots; same charts in the PDF |
| Agent | recommend + approve | + **Copilot** (tool-using, grounded in the calculations, proposes but cannot execute), approved actions dispatched to Slack/Teams/webhook, scheduled **monitor** that alerts on new or worsening leaks |
| Trust | session log | SQLite audit trail, **hash-chained** (tamper-evident), role-based sign-in (viewer / reviewer / admin), raw client rows never stored |
| Ship | Streamlit only | Dockerfile, docker-compose, CI tests (35), example secrets and connections files |

## Update your GitHub repo (no coding)
1. Unzip the download. You get a folder `archenex-enterprise-agent`.
2. Open your repo on github.com → **Add file → Upload files**.
3. Drag in **everything inside the folder** (files *and* the folders `archenex`, `docs`, `tests`, `scripts`,
   `templates`, `data`, `.streamlit`, `.github`). Chrome and Edge accept folders; if yours does not, use
   **GitHub Desktop** (free) and copy the files over.
4. Delete the old `agent_model.py`, `detectors.py`, `report.py`, `demo_data.py` from the repo root (v3 keeps these
   inside the `archenex` folder). On github.com: open the file → `...` → **Delete file** → Commit.
5. Click **Commit changes**. Streamlit redeploys in 1-3 minutes. If it errors: **Manage app** → read the log.

## Settings (Streamlit → app → Settings → Secrets)
See `.streamlit/secrets.toml.example`. Nothing is required: with no secrets the app runs in **open demo mode**
on synthetic data. Add `[users.name]` entries for sign-in, `ANTHROPIC_API_KEY` for the Copilot and AI brief,
`WEBHOOK_URL` to push approved actions to Slack/Teams.

## Run on your own computer
```
pip install -r requirements.txt
streamlit run app.py
python -m archenex.cli demo          # headline numbers in the terminal
python -m pytest -q                  # 35 tests
```

## Using it with a real client (pilot)
1. Sidebar → **Data source → Upload files** (or **Live connectors**).
2. **0. Connect & Data** → upload their exports in whatever format they have → confirm the column mapping once → *Remember*.
3. Review **1. Executive Cockpit**, **2. Deep Dives**, then **4. Action Queue** with the client's CFO/COO.
4. **8. Report & Verify** → build the PDF → both sides sign.
5. **7. History** → save each run; schedule `archenex.cli monitor` for the subscription phase.

## What is NOT built yet (say this to clients)
Vendor-specific API connectors (the REST connector is generic; endpoints must be filled from each vendor's docs and
tested with the client), single sign-on, multi-node database, penetration test / ISO 27001, write-back to ERP/HRIS.
See `docs/SECURITY.md` and `docs/ROADMAP.md`.
