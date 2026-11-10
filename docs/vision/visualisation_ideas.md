# Visualisation ideas (long list, 2026-11-10)

Brainstorm made after reviewing existing viewers (`existing_dashboards.md`). All buildable from the local CSVs
(+ WFS geometry). The storytelling story lines in `storytelling_app.md` take priority; use this list to pick chart forms.
Lead agent's original top 3: **#1 alluvial of class changes**, **#4 + #6 bullet charts with what-if slider**,
**#7 status matrix linked to map** (cover time, goals and comparison – none of the existing dashboards does).
The user's own idea (absolute vs goal-relative EKR bars, see `docs/analysis/ekr_abs_vs_rel.md`) is now a core chapter.

## A. Change over time
1. **Alluvial / Sankey of class transitions** between reporting years (e.g. 2019 → 2022 → 2025) per element
   (`ggalluvial`, `networkD3`, `echarts4r`).
2. **Bump chart of most-failing substances** over the years (`ggbump`).
3. **Dumbbell plot year A → year B** per water body or beheerder (distance moved towards goal).

## B. Distance to goal (join doelen × oordelen)
4. **Bullet chart against class bounds**: measured value on the body's own scale with zeer goed…slecht bands from `doelen`.
5. **Normalised gap** (`value / goed-matig boundary`) for all elements → one lollipop/radar per water body.
6. **What-if slider**: e.g. "Ptot −20%" → how many bodies move to goed (reactive recomputation against goal bounds).

## C. Comparing water bodies
7. **Status matrix / heatmap**: rows = water bodies, columns = elements, colour = class; sortable/clustered by type or
   beheerder (`heatmaply`, `reactable`), linked to the map.
8. **Peer benchmark**: beeswarm/ridgeline of EKR per watertype, selected body highlighted (`ggbeeswarm`, `ggridges`).
9. **Scorecard per beheerder** with sparklines (`gt` + `gtExtras`, `reactablefmtr`).
10. **Geofacet grid of waterschappen** (`geofacet`): small multiples in rough geographic layout, no geometry needed.

## D. Explaining the verdict
11. **One-out-all-out decomposition**: which element determines failure; how many bodies would pass without element X.
12. **Nutrients vs biology**: mosaic plot / logistic regression of fosfor class vs fytoplankton class (`ggmosaic`, `broom`).
13. **Co-failing substances** (`ComplexUpset`).

## E. Text & data quality
14. **Text mining of motivering** (`tidytext`): terms, tf-idf, themes (e.g. background metal concentrations, beheeroordeel).
15. **Data gaps & age of verdict**: map/timeline of "Niet toetsbaar / Niet beoordeeld" and assessment periods.
16. **Water body genealogy**: splits/merges between plan periods (`visNetwork`/`ggraph`). Note: `VoorgangerCode` is empty
    → links must be reconstructed (name match or spatial overlay).

## Shiny techniques to showcase
- Linked views (`crosstalk`, `plotly`, `leafletProxy`/`mapgl`), drill-down NL → beheerder → water body → element.
- Bivariate choropleth ecology × chemistry (`biscale`).
- `duckdb`/`arrow` over the ~1.4 GB full assessment CSVs.
- Parameterised Quarto report per water body (download).
- URL bookmarking, `bslib` theming, Shiny modules, `shinytest2`, golem/rhino structure.
- Scrollytelling (chapter-based narrative), AI-generated texts (`ellmer`), animated re-sorting (`gganimate`/`echarts4r`).
