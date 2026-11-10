# Work log

## 2026-11-10
- Lead agent (Claude): inventoried local downloads (`docs/data/inventory.md`); reviewed WKP viewers and 7 Haskoning
  dashboards (`docs/vision/existing_dashboards.md`); verified RWS WFS (`docs/sources/wfs_rws.md`: 745 features, current
  version only); EKR absolute vs relative analysis 2025 (`analysis/ekr_abs_vs_rel.py`, `docs/analysis/ekr_abs_vs_rel.md`);
  wrote vision (`docs/vision/storytelling_app.md`), `CLAUDE.md`, `README.md`.
- Subagent (Sonnet): EU WISE / Italy data research → `docs/sources/eu_wise_data.md`.
- Subagent (Sonnet): goal changes over time → `analysis/doelen_over_tijd.py`, `docs/analysis/doelen_over_tijd.md`.
- Note: R not installed on this machine; exploration done in Python 3 (no pandas; csv module only).
- Lead agent verified subagent results: `VoorgangerCode` empty in all OWL files and WFS (docs corrected); reran
  `analysis/doelen_over_tijd.py` (exit 0, numbers match `docs/analysis/doelen_over_tijd.md`); EEA ArcGIS REST endpoint
  reachable. Discodata SQL API returned 403 to automated requests (untested from R).

## 2026-11-11
- Lead agent: tooling check. Positron installed; R 4.4.2 at `C:\Program Files (x86)\R\R-4.4.2` (not on PATH); Quarto 1.11.9
  bundled with Positron; Python 3.15 without pandas. `sf::st_read()` on the RWS WFS returns 745 features (EPSG:4326).
  Installed R packages: tidyverse, readr, dplyr, ggplot2, sf, bslib, plotly, jsonlite.
  Missing: shiny, duckdb, arrow, leaflet, mapgl, echarts4r, ggiraph, reactable, gt, httr2, ellmer, targets, golem, rhino,
  testthat, shinytest2, quarto, renv, ggalluvial, ggbump, gganimate, rmapshaper. Details in `CLAUDE.md` (Tooling).
- Lead agent: installed all of the above into the user library (CRAN binaries for R 4.4). Fixes needed: knitr/rmarkdown
  updated (old system-library versions broke targets/quarto via `xfun::attr`); ggbump 0.1.0 from CRAN Archive (source).
  All 22 + tidyverse/sf/bslib/plotly load. Rtools not installed; R 4.4 binaries on CRAN are frozen.
- Lead agent: documentation audit. Added `docs/vision/visualisation_ideas.md` (long list + top 3 + Shiny techniques);
  added the user's rationale on lowered goals and data-access decisions to `storytelling_app.md`; "never Fable" rule in
  `CLAUDE.md`.
