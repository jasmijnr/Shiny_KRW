# Shiny_WKP

Exploration and (later) an R Shiny storytelling app about the state of Dutch WFD (KRW) surface waters, with
comparisons to other EU countries. Agent instructions: `CLAUDE.md`.

## Document index
| Document | Content |
|---|---|
| `docs/vision/storytelling_app.md` | Vision, story lines, proposed chapters, AI-text design, tech direction, open decisions |
| `docs/vision/existing_dashboards.md` | Review of WKP viewers and Haskoning Shiny dashboards; the gap we target |
| `docs/vision/visualisation_ideas.md` | Long list of chart ideas, top 3, Shiny techniques to showcase |
| `docs/data/inventory.md` | Local CSV downloads: files, grain, columns, goal sets, join keys |
| `docs/sources/wfs_rws.md` | RWS/IHW WFS for geometries and state layers, recipes in R |
| `docs/sources/eu_wise_data.md` | EEA WISE WFD data for NL/Italy comparison (subagent research) |
| `docs/analysis/ekr_abs_vs_rel.md` | Absolute EKR vs EKR relative to goal, 2025 |
| `docs/analysis/doelen_over_tijd.md` | How goals changed across goal sets 2012–2025 (subagent analysis) |
| `docs/log.md` | Work log |

## Folders
- `WKP_download_*` – raw WKP downloads (read-only)
- `Literatuur/` – background literature
- `analysis/` – exploratory scripts (Python, standard library):
  `ekr_abs_vs_rel.py` → `output/ekr_abs_vs_rel_2025.csv`;
  `doelen_over_tijd.py` → `output/doelen_ekr_long.csv`, `doelen_changes_summary.csv`, `q4_link_table.csv`, `report_tables.txt`
- `docs/` – documentation for humans and agents
