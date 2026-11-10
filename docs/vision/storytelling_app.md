# Vision: storytelling KRW app

Status: exploration (2026-11-10). Owner: Jasmijn Rost. Implementation language: **R / Shiny**.

## Goal
Not "yet another dashboard" (see `docs/vision/existing_dashboards.md`) but an app that **explains** the state of Dutch
(later European) surface waters and **generates insight**, in a scrollytelling / narrative style. It should show off
R and Shiny skills (modules, linked views, maps, reactive what-if, generated text, testing).

## Story lines (from the user, 2026-11-10)
1. **NL vs Italy (later other EU countries).** Cross-country comparison from EEA WISE data.
   Research: `docs/sources/eu_wise_data.md`.
2. **Narrative per water body or group**, with AI-generated text that explains status, drivers and trend to a lay reader.
3. **How do goals change over time?** More precise goals, lowered goals, or raised goals thanks to measures?
   Analysis: `docs/analysis/doelen_over_tijd.md`.
4. **Absolute EKR vs. EKR relative to goal.** Same bars, two orderings: ecological quality vs. "goal reached".
   Hypothesis / user's rationale: goals for HMWB/artificial bodies may be lowered based on the *current* situation, and
   raised only by the effect of *future measures*. In principle "future measures" should mean all possible measures, but in
   practice only easy and not-too-expensive measures are counted. That removes a lot of ambition; ranking relative to the
   goal therefore gives a very different (rosier) picture than ranking on absolute EKR.
   Related question from the user: are goals over time getting *more precise*, *lower*, or *higher* (thanks to compounded
   effects of measures)?
   First result: `docs/analysis/ekr_abs_vs_rel.md` (strong support: 60–76% of macrofauna/waterflora "goal reached"
   bodies are below EKR 0.6).

## Key findings so far
- Goals: SGBP2 (2015 set) → SGBP3 (2021 set): of 2,369 matched EKR goals 39% lowered, 19% raised, 42% unchanged; the
  2021→2025 sets are nearly stable. HMWB/artificial goals below 0.6: 51.5% → 66.2%. Lowered goals correlate moderately with
  earlier low measured EKR (Spearman 0.35; 59% of failing goals lowered vs 9% of passing). Association, not proof.
- Absolute vs relative EKR: 60–76% of macrofauna/waterflora bodies that reach their goal are below EKR 0.6.
- EU: WISE (EEA ArcGIS REST) has status classes per quality element for NL (741 WB) and IT (7,763 WB) but no EQR values or
  goals → the EKR/goal story is NL-only; the EU chapter compares classes, unknown shares, HMWB share, exemptions.

## Proposed chapters (draft)
1. *Where are we?* National picture 2025, map + headline numbers.
2. *Goal or ecology?* Absolute vs relative ranking (animated re-sort), with the 0.6 line and own-goal ticks.
3. *Moving goalposts.* Goal changes between SGBP2 → SGBP3 → 2025 (slope charts, distribution shift, goal vs earlier EKR).
4. *What drives the verdict?* One-out-all-out decomposition: which element determines failure.
5. *Your water body.* Search/click a water body → generated narrative + charts (bullet chart against class bounds, trend).
6. *Europe.* NL vs IT (status shares by broad type, unknown status share, HMWB share, exemptions).

## AI-generated texts – design notes
- Generate **offline** (batch script) per water body/group and store in a table (`data/texts/*.parquet`) with model id,
  prompt version and date; the app reads stored text (fast, reproducible, reviewable). Optional live "ask about this water
  body" button via the Claude API with `ellmer` in R.
- Ground every text in structured facts passed in the prompt (status per element, EKR, goal, trend, motivering text);
  instruct the model to use only those facts; show "AI-generated" label and the facts table next to it.
- Model: current Claude model (Sonnet tier is enough for batch narratives).

## Data access decisions
- Geometry: user prefers WFS over the downloadmodule (https://wkp.rws.nl/downloadmodule, which also offers shapefiles).
  The RWS WFS works but has only the current SGBP3 geometry; use the downloadmodule only for historical geometries.
  The user offered to download all 2025 data from the downloadmodule; judged not needed yet (CSVs + WFS suffice).
- EU data: EEA WISE ArcGIS REST (see `docs/sources/eu_wise_data.md`). Status classes only, no EQR values or goals.
- Chart-form long list: `docs/vision/visualisation_ideas.md`.

## Technical direction (proposal, not decided)
- Data prep in R (`targets` pipeline): CSV → tidy parquet in `data/processed/`; heavy files via `duckdb`/`arrow`.
- Geometry from WFS (`docs/sources/wfs_rws.md`), cached as GeoPackage.
- App: `bslib` + Shiny modules (golem or rhino), maps `mapgl` or `leaflet`, charts `ggplot2`/`ggiraph` or `echarts4r`,
  tables `reactable`; scrollytelling via `scrollytell`/custom JS or Quarto + Shiny.
- Tests: `testthat` + `shinytest2`.

## Open decisions
- R 4.4.2 + Positron available; app package set installed 2026-11-11 (see `CLAUDE.md` → Tooling).
- golem vs rhino (both installed), leaflet vs mapgl, ggiraph vs echarts4r: not chosen yet.
- Hosting (shinyapps.io / Posit Connect / own server).
- Language of the app (NL, EN, or both).
- Which EU countries after Italy.
