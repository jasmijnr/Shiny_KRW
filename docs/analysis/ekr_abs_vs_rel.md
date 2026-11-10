# EKR absolute vs. relative-to-goal (reporting year 2025)

Script: `analysis/ekr_abs_vs_rel.py` · Output: `analysis/output/ekr_abs_vs_rel_2025.csv` (`;`-separated)

## Question
If you rank water bodies on **absolute EKR** for a biological element, and then on **EKR relative to their own goal**
(`ratio = EKR / goal`), how different is the picture? Hypothesis (user): lowered goals for heavily modified / artificial
water bodies (goal derived from current state + "feasible" measures) make many bodies look good relative to their goal while
they are ecologically poor in absolute terms.

## Method
- EKR = `BepalendKental` from `WKP_KRW-toestandsoordelen-beknopt_Nederland_2025_*.csv` where `HoedanigheidCode == 'EKR'`.
- Goal = `OndergrensWaarde` of class `goed` in `WKP_KRW-doelen_Nederland_2025_*.csv` (the goed/matig boundary = GES/GEP).
- Join on upper-cased `WaterlichaamCode` + `KRWkwaliteitselementCode`. 2,596 of 2,596 EKR values matched a goal.
- Ranks computed per element; Spearman rho between absolute and relative rank.

## Results

| Element | n | Median goal natural | Median goal HMWB/artificial (min) | Reach goal | …of which EKR < 0.6 | Median rank shift | Spearman rho |
|---|---|---|---|---|---|---|---|
| Fytoplankton | 426 | 0.60 | 0.60 (0.10) | 218 | 57 | 43 | 0.78 |
| Macrofauna | 730 | 0.60 | 0.50 (0.10) | 341 | **205** | 118 | **0.55** |
| Overige waterflora | 728 | 0.60 | 0.45 (0.01) | 304 | **231** | 108 | 0.63 |
| Vis | 712 | 0.60 | 0.50 (0.05) | 333 | 125 | 73 | 0.76 |

Headline: for macrofauna and other aquatic flora, **60–76% of the water bodies that "reach their goal" would not reach the
natural 0.6 boundary**. The rank correlation between absolute and goal-relative ranking is only 0.55–0.63 for those elements,
so the two orderings tell genuinely different stories. Some goals are extremely low (0.01 for waterflora).

## Caveats
- EKR scales are intercalibrated so that 0.6 is the good/moderate boundary for natural types; comparing absolute EKR across
  water types is meaningful in that sense, but the underlying metrics differ per type (R-, M-, K-, O-types).
- Some HMWB/artificial bodies are assessed on adapted scales; check whether the EKR in the assessment is already on the
  adapted scale before claiming "would fail 0.6" in the app. Mark this as an open question in the story text.
- One year only (2025). Goal history is analysed in `docs/analysis/doelen_over_tijd.md`.

## Visualisation (planned)
Two linked panels with the same bars: (1) sorted by absolute EKR with a 0.6 reference line and each body's own goal as a tick;
(2) re-sorted by `ratio` with a line at 1.0. Animated transition between the two (e.g. `ggplot2` + `gganimate`, or
`echarts4r`/`plotly` with a toggle), colour by KRW status (natural / heavily modified / artificial). A slope/bump chart
connecting rank_abs to rank_rel is the static alternative.
