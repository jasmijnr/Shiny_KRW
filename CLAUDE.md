# Shiny_WKP – instructions for agents

Storytelling R Shiny app on Dutch WFD (KRW) surface water status, later compared with other EU countries.
Read `README.md` for the document index before starting. Vision: `docs/vision/storytelling_app.md`.

## Ground rules
- **Document everything you learn or produce in `docs/`** so other agents can pick it up:
  data facts → `docs/data/`, external sources/APIs → `docs/sources/`, analyses → `docs/analysis/`,
  design/vision → `docs/vision/`. Add a line to `docs/log.md` (date, who/what, files) for every work session.
  Update `README.md` when you add a document.
- Analysis scripts go in `analysis/` (re-runnable, docstring at top explaining inputs/outputs), outputs in `analysis/output/`.
- Do not modify or delete the raw downloads (`WKP_download_*`, `*.zip`, `Literatuur/`). Treat them as read-only.
- Final app code is **R** (tidyverse style, see the `r-style` skill if available). Prefer R for new analysis too.

## Tooling on this machine (checked 2026-11-11)
- IDE: Positron (`C:\Users\jas_m\AppData\Local\Programs\Positron`).
- R 4.4.2, **not on PATH**: call `"/c/Program Files (x86)/R/R-4.4.2/bin/Rscript.exe" script.R` (Bash) or
  `& "C:\Program Files (x86)\R\R-4.4.2\bin\Rscript.exe" script.R` (PowerShell). Run R code from a script file:
  `Rscript -e` breaks on `&` in URLs under Windows. User library: `C:/Users/jas_m/AppData/Local/R/win-library/4.4`.
  An old R 4.1.3 is also installed; ignore it. CRAN repo is unset (`@CRAN@`): pass `repos = "https://cloud.r-project.org"`.
- Installed and verified (loadNamespace) 2026-11-11, user library: tidyverse, sf (GDAL 3.10.1, PROJ 9.5.1, reads the WFS),
  bslib, plotly, shiny, duckdb, arrow, leaflet, mapgl, echarts4r, ggiraph, reactable, gt, httr2, ellmer, targets, golem,
  rhino, testthat, shinytest2, quarto, renv, ggalluvial, ggbump, gganimate, rmapshaper, knitr 1.51, rmarkdown 2.31.
- **CRAN no longer builds new Windows binaries for R 4.4** → binaries lag behind source (e.g. xfun 0.57 vs 0.62).
  **Rtools is not installed**, so packages with compiled code can only come as (older) binaries. Pure-R packages can be
  installed from source. `ggbump` is archived on CRAN: installed 0.1.0 from the CRAN Archive.
- Pitfall seen: old `knitr`/`rmarkdown` in the system library called `xfun::attr` (removed in newer xfun) → targets/quarto
  failed to load until knitr/rmarkdown were updated in the user library. If a package fails with "not exported by
  namespace", update its dependants first. 59 user-library packages still have newer binaries available (not updated).
- Consider upgrading to the current R release + Rtools if more version conflicts appear.
- Python 3.15 (`python -I`), standard library only (no pandas).
- Quarto 1.11.9 bundled with Positron: `C:\Users\jas_m\AppData\Local\Programs\Positron\resources\app\quarto\bin\quarto.exe`.
- Write docs in English; data values/column names stay Dutch as in the source.
- Be factual: state what you verified vs. inferred. No invented URLs or numbers.

## Data conventions (details: `docs/data/inventory.md`)
- CSVs: UTF-8 with BOM, `;` separator, `.` decimal. In R: `readr::read_delim(f, delim = ";", locale = locale(encoding = "UTF-8"))`.
- Join water bodies on `toupper(WaterlichaamCode)`; element on `KRWkwaliteitselementCode`; year on `Rapportagejaar`.
- Goal (GES/GEP) for EKR elements = lower bound of class `goed` in the doelen file.
- Use the condensed assessment (`toestandsoordelen-beknopt`) for the app; the full `toestandsoordelen` files are up to
  150 MB per year → use duckdb/arrow and select columns.
- Geometry: WFS `https://geo.rijkswaterstaat.nl/services/ogc/wkp/wkp/wfs` (current SGBP3 only), see `docs/sources/wfs_rws.md`.

## Orchestration
The lead agent delegates well-scoped, simpler tasks (data profiling, source research, doc writing, small scripts) to
subagents on cheaper models (Sonnet/Haiku; **never Fable**, per the user). Each brief must name input files, output files
and the doc to update. The lead agent verifies subagent results (rerun scripts, spot-check claims) before reporting.
