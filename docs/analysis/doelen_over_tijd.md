# Dutch WFD (KRW) goals for surface water bodies over time

Analysis of how the ecological goals per water body x quality element changed between the distinct goal sets published 2013-2025.
Script: `analysis/doelen_over_tijd.py` (Python 3, standard library only; re-runnable, ~20 s). All numbers below come from
`analysis/output/report_tables.txt`; tidy outputs are `analysis/output/doelen_ekr_long.csv`, `doelen_changes_summary.csv` and `q4_link_table.csv`.

## 1. Data and method

**Goal sets.** Each yearly file (2013-2025) holds one goal set. Consecutive files with identical goal content (code, element, class, symbols, bounds
of the analysed elements) are merged; a set is labelled by the first file year in which it appears.

| Set label | Files | Declared as | Remark |
|---|---|---|---|
| 2013 | 2013 | set of 2012, correction of the 2009 set | |
| 2014 | 2014 | set of 2013 for SGBP2 | |
| **2015** | 2015-2017 | 2014 correction of the 2013 set | **baseline "SGBP2" set** |
| 2018 | 2018-2019 | same description as 2015 | differs from 2015 only by one added body (4 EKR goals) |
| 2020 | 2020 | SGBP3 (set of 2020) | |
| **2021** | 2021-2022 | SGBP3 (set of 2021) | |
| 2023 | 2023 | SGBP3 (set of 2023) | |
| 2024 | 2024 | SGBP3 (set of 2024) | |
| **2025** | 2025 | SGBP3 (set of 2025) | latest |

Note: when the full file content (including O2/pH/T rows, watertype codes, names) is hashed, files 2015, 2016 and 2017 look different
(re-typed O2/T bounds, watertype codes changed in 2017), but the goals of the analysed elements are identical. The set identity therefore uses only the analysed elements.

**Water body matching.** Code is upper-cased (9 of 1,210 distinct codes occur with different capitalisation). The OWL files contain **no** `VoorgangerCode`
and no `TypeWijzigingCode` values in any year (0 bodies), so predecessor links could not be used. Codes changed massively at two moments (2013->2014, 2018->2020; e.g.
`NL04_DEDEMSVAART` -> `NL04_DEDEMSVAARTA`). As fallback, a body without code match is linked to an unmatched body of the other set when normalised name + waterbeheerder is unique on both sides.
This is a heuristic, not an official link.

| Pair | New codes (code-only) | Old codes gone (code-only) | Recovered by name + beheerder | Still unmatched new | Still unmatched old |
|---|---|---|---|---|---|
| 2013->2014 | 241 | 233 | 195 | 46 | 38 |
| 2018->2020 | 265 | 236 | 208 | 57 | 28 |
| 2015->2021 | 265 | 235 | 199 | 66 | 36 |
| 2013->2025 | 428 | 389 | 305 | 123 | 84 |

Between 2020 and 2025 no codes changed at all. Whether the unmatched bodies are real splits/merges/new bodies cannot be determined from these files.

**Goal definition (Q1).** Per water body x element, the boundary between `goed` and `matig`:
- EKR elements (FYTOPL, MAFAUNA, OVWFLORA, VIS): lower bound of `goed` (`>=`). Higher = more ambitious.
- Ptot, Ntot (and Cl): upper bound of `goed` (`<=`). Lower = more ambitious. ZICHT (m): lower bound of `goed`, higher = more ambitious.
- Direction labels: *up* = more ambitious, *down* = less ambitious, *equal* = difference <= 1e-9.

**Verification.** Symbols on `goed` rows: EKR 25,661/25,661 rows are `>=` ... `<=`, the EKR upper bound is always 1 (symbol `<=`). Ptot/Ntot are `>=0` ... `<=`. ZICHT has an open upper bound. Only four classes exist
(`slecht, ontoereikend, matig, goed`; no `zeer goed` rows, also not for natural bodies), so for natural bodies the goal (0.6) is the GES boundary and for HMWB/artificial bodies it is the GEP boundary.
Per goal set the checks give (counts of body x element goals, latest set 2025 in brackets):

| Check | Result |
|---|---|
| EKR, `goed` lower bound present, symbol `>=`, within 0..1 | passes for all but listed below |
| EKR class lower bounds monotonic | 1-2 failures per set: `NL34M101` MAFAUNA (2013/14, goed 0.10 < matig 0.11) and `NL43_16` OVWFLORA (2020, matig 0.167 vs ontoereikend 0.83, evident typo; goal 0.25) |
| EKR `matig` upper bound = `goed` lower bound | 18 gaps in set 2014 (VIS, e.g. matig up to 0.35 but goed from 0.25), 2 in 2015/2018, none from 2020 |
| Ptot | clean in all sets (but 38 Ptot goals vanish in 2025, see anomalies) |
| Ntot | 1 body without `goed` row (2013), 1 gap (`NL99_BRA_02_3E` 2.6 vs 2.3, 2014-2018) |
| **Cl** | **not a simple "lower is better" element**: ~52-56 goals per set have a `goed` class that is a range (e.g. >=300 and <=3000) with duplicate `matig` rows and non-monotonic bounds; ~18-29 have no upper bound (open). The upper bound of `goed` is therefore only a rough goal for Cl; Cl results are reported but should not be interpreted as ambition. |

The definition is thus confirmed for EKR, Ptot, Ntot and ZICHT; it is **not** valid for a minority (~7%) of Cl goals.

## 2. Changes between goal sets (Q2)

EKR elements pooled (FYTOPL+MAFAUNA+OVWFLORA+VIS), body x element goals present in both sets matched (code or name), unit EKR:

| From -> to | In both | Up | Down | Equal | Appeared (new body / new element) | Disappeared (body gone / element gone) | Median change of changed goals (p10 / p90) |
|---|---|---|---|---|---|---|---|
| 2013 -> 2014 | 2,316 | 207 | 567 | 1,542 | 163 / 24 | 136 / 12 | -0.095 (-0.20 / +0.09) |
| 2014 -> 2015 | 2,503 | 29 | 141 | 2,333 | 3 / 2 | 0 / 0 | -0.10 (-0.35 / +0.02) |
| 2015 -> 2018 | 2,508 | 0 | 0 | 2,508 | 4 / 0 | 0 / 0 | - |
| **2018 -> 2020 (SGBP2 -> SGBP3)** | 2,405 | 421 | 902 | 1,082 | 212 / 14 | 100 / 7 | -0.06 (-0.25 / +0.15) |
| 2020 -> 2021 | 2,631 | 48 | 29 | 2,554 | 0 / 1 | 0 / 0 | +0.02 (-0.10 / +0.02) |
| 2021 -> 2023 | 2,632 | 35 | 84 | 2,513 | 0 / 0 | 0 / 0 | -0.10 (-0.35 / +0.10) |
| 2023 -> 2024 | 2,632 | 1 | 2 | 2,629 | 0 / 4 | 0 / 0 | -0.05 |
| 2024 -> 2025 | 2,635 | 5 | 4 | 2,626 | 0 / 0 | 0 / 1 | +0.05 (-0.11 / +0.06) |
| **2015 -> 2021** | 2,369 | 458 | 920 | 991 | 248 / 15 | 132 / 7 | -0.05 (-0.24 / +0.15); up median +0.10, down median -0.10 |
| **2021 -> 2025** | 2,631 | 37 | 86 | 2,508 | 0 / 4 | 0 / 1 | -0.10 (-0.35 / +0.10) |
| 2015 -> 2025 | 2,369 | 449 | 969 | 951 | 248 / 18 | 132 / 7 | -0.08 (-0.25 / +0.15) |

Headline: the SGBP2 -> SGBP3 transition is the big change: of 2,369 EKR goals matched between the 2015 and 2021 sets, **39% were lowered, 19% raised, 42% unchanged**; the median lowering is 0.10 EKR
(typically one 0.05-0.10 step), the median raise +0.10. After 2021 the sets are almost stable, except a revision in the 2023 set (84 lowered, 35 raised).
Within SGBP3 the 2021 -> 2023 lowerings are concentrated in OVWFLORA (35 of 37 changed goals are lowered, median -0.25) and MAFAUNA (18 lowered); VIS goes the other way (27 raised, +0.10).
Note that "appeared/disappeared" mostly reflects unmatched renamed bodies (see table above), not real new/removed goals.

**By element, 2015 -> 2021 (matched):**

| Element | In both | Up | Down | Equal | Median change (changed) |
|---|---|---|---|---|---|
| FYTOPL | 368 | 62 | 90 | 216 | -0.05 |
| MAFAUNA | 674 | 99 | 294 | 281 | -0.10 |
| OVWFLORA | 668 | 149 | 292 | 227 | -0.05 |
| VIS | 659 | 148 | 244 | 267 | -0.05 |
| Ptot (mg/l P) | 656 | 40 | 109 | 507 | median relative change of changed goals +45% (higher limit = more lenient) |
| Ntot (mg/l N) | 659 | 57 | 73 | 529 | +4% |
| ZICHT (m) | 362 | 21 | 36 | 305 | -0.20 m |

(For Ptot/Ntot, "Down" = a higher, less strict concentration limit. 109 of 149 changed Ptot goals became less strict.) Cl omitted from interpretation (see anomalies).

**By KRW status, EKR, 2015 -> 2021:** natural 56 goals (10 up, 0 down, 46 equal; median raise +0.055, i.e. a few natural goals that were below 0.60 in the 2015 set, or are new values such as `NL11_4_1`; not further analysed); HMWB (Sterk veranderd) 854 (196 up / 328 down / 330 equal); artificial (Kunstmatig) 1,459 (252 up / 592 down / 615 equal).
2021 -> 2025: natural 56/56 equal; HMWB 7 up / 24 down; artificial 30 up / 62 down.
Status transitions of the same code: 6 bodies 2018 -> 2020 (5 HMWB -> artificial, 1 artificial -> HMWB).

**By waterbeheerder, EKR, 2015 -> 2021 (matched goals; % down = share lowered among changed goals).** Strong lowerers: Hollandse Delta 86 down / 0 up (median -0.20), De Stichtse Rijnlanden 57/2 (97% down), Rijnland 85/5 (94%), Hunze en Aa's 37/3 (92%),
De Dommel 45/6, Fryslan 57/12, Schieland en Krimpenerwaard 50/11. Net raisers: Drents Overijsselse Delta 51 up / 9 down (median +0.10), Amstel Gooi en Vecht 61/31, Rijn en IJssel 43/17, Hollands Noorderkwartier 68/65 (balanced, median +0.05),
Scheldestromen 36/20. Zeeuws-Vlaanderen's 32 goals cannot be matched to 2021 (no equivalent codes/names). The full table (all waterbeheerders, all pairs, all elements) is `doelen_changes_summary.csv`
(dimension = `beheerder` / `krw_status` / `all`).

**Chemical/other (2015 -> 2021, matched):** Ptot 40 stricter / 109 more lenient (HMWB median +27%, artificial +60% among changed); Ntot 57 / 73; ZICHT 21 / 36. 2021 -> 2023: 38 Ptot limits tightened (median -2.4 mg/l, i.e. from very lenient values). 2023 -> 2024: Ntot 34 tighter / 7 looser.
2024 -> 2025: **38 Ptot goals disappear** (all Zeeland `NL42_*` bodies; Ptot count 724 -> 686); cause unknown.

## 3. EKR goals vs 0.6 (Q3)

**Natural water bodies.** In the 2015 set all 38 natural EKR goals equal exactly 0.60. In 2021 and 2025, 53 of 56 equal 0.60; three goals of one body (`NL11_4_1`: FYTOPL 0.69, MAFAUNA 0.61, OVWFLORA 0.71) are above 0.60. No natural goal is below 0.60 in any set.
Natural-body count rises from 35 (2013) to 56 goals (2020+), so 0.6 is effectively a fixed rule for natural bodies with one deviation (unexplained in the data).

**HMWB / artificial bodies.**

| Set | HMWB+artificial EKR goals | Below 0.60 | % below | Median goal | Bodies with >=1 goal < 0.6 |
|---|---|---|---|---|---|
| 2013 | 2,429 | 969 | 39.9% | 0.60 | - |
| 2014 | 2,465 | 1,190 | 48.3% | 0.60 | - |
| **2015 (SGBP2)** | 2,470 | 1,272 | 51.5% | 0.55 | 520 of 697 |
| 2018 | 2,474 | 1,275 | 51.5% | 0.55 | - |
| 2020 | 2,575 | 1,692 | 65.7% | 0.50 | - |
| **2021** | 2,576 | 1,702 | 66.1% | 0.50 | 664 of 721 |
| **2025** | 2,579 | 1,708 | 66.2% | 0.50 | 664 of 721 |

Shortfall below 0.6 (set 2025, goals < 0.6): median 0.15 (MAFAUNA, OVWFLORA HMWB), 0.20 (OVWFLORA artificial), 0.30 (VIS HMWB; p90 0.45). Lowest goals are 0.01-0.10 (OVWFLORA, VIS, FYTOPL artificial).
72 non-natural goals are above 0.6 (up to 0.80; 22 goals of 0.80).

Histogram of EKR goals, HMWB / artificial (number of goals):

| Bin | 2015 HMWB | 2015 artificial | 2025 HMWB | 2025 artificial |
|---|---|---|---|---|
| [0, 0.2) | 29 | 31 | 54 | 57 |
| [0.2, 0.3) | 66 | 47 | 65 | 82 |
| [0.3, 0.4) | 139 | 93 | 145 | 210 |
| [0.4, 0.5) | 247 | 152 | 233 | 335 |
| [0.5, 0.6) | 212 | 256 | 230 | 297 |
| = 0.60 | 257 | 939 | 186 | 613 |
| > 0.60 | 0 | 2 | 5 | 67 |

Median goal per element, non-natural, set 2015 -> 2025: FYTOPL 0.60 -> 0.60, MAFAUNA 0.60 -> 0.50, OVWFLORA 0.55 -> 0.45, VIS 0.50 -> 0.48.
Share of HMWB goals below 0.6 per element in 2025: VIS 89%, OVWFLORA 81%, MAFAUNA 78%, FYTOPL 37%; artificial: OVWFLORA 80%, MAFAUNA 67%, VIS 47%, FYTOPL 39%. Common values 0.6, 0.5, 0.45, 0.4, 0.55, 0.3 (steps of 0.05).

## 4. Does the goal follow the status? (Q4)

**Data.** Numeric EKR (`BepalendKental`) exists in the condensed assessment files for 2009 (period 2003-2008) and from 2020 onward (2020: period 2009-2019; 2021: 2010-2020; ...). The 2014-2019 files contain only classes (BepalendKental empty/0).
Primary "earlier measured" status = 2020 file (period 2009-2019, 2,300 numeric values), compared with the goal change from the 2015 set (SGBP2) to the 2021 set (SGBP3). The 2020 assessment was published in the same year as the first SGBP3 set, so it is plausible (not proven) that it was available when the new goals were set.
Matched 2,172 of 2,369 goals. Numbers below concern HMWB + artificial (natural bodies: 47 goals, none lowered).

| Goal change 2015->2021 | n | Median old goal | Median new goal | Median measured EKR | % measured >= old goal | % measured >= new goal |
|---|---|---|---|---|---|---|
| Lowered | 866 | 0.60 | 0.40 | 0.37 | 8% | 37% |
| Unchanged | 892 | 0.60 | 0.60 | 0.54 | 51% | 51% |
| Raised | 367 | 0.40 | 0.50 | 0.45 | 69% | 34% |

| Old goal vs measured EKR | n | % lowered | % raised |
|---|---|---|---|
| measured below old goal ("failing") | 1,352 | 59.0% | 8.4% |
| measured at/above old goal ("meeting") | 773 | 8.8% | 32.9% |

By gap (measured minus old goal): [-inf, -0.30): 75% lowered (n=145); [-0.30, -0.15): 75% (446); [-0.15, -0.05): 55% (512); [-0.05, 0]: 28% (303); > 0: 8% (719).
Spearman correlation between measured EKR (2009-2019) and the goal change: **0.35** (95% bootstrap CI 0.31-0.39; n=2,125); per element 0.27 (VIS) to 0.43 (OVWFLORA). Using the 2019 class (1-5) instead: 0.48; the 2021 assessment file: 0.36; the 2003-2008 assessment: only 0.11 (n=637).
Among lowered HMWB/artificial goals the new goal is median 0.03 above the measured EKR (p10 -0.08, p90 +0.14); 37% of new goals are at or below the measured value.
441 goals were not lowered although measured EKR was below the goal.

**Interpretation (careful).**
- Goals were adjusted in both directions and the direction is clearly associated with the measured status: bodies far below the old goal were mostly lowered, bodies at/above the old goal were rarely lowered and often raised. This is consistent with "goal follows status".
- It is not proof of causation and not the only explanation. Possible alternatives: (a) re-derivation of GEP with updated measures/maatlatten (which would also correlate with status, because the potential is partly determined by what is achievable), (b) new/changed EKR classification methods between SGBP2 and SGBP3 which change both measured values and goals, (c) bodies that fail and are heavily modified are exactly those with a legitimate lower potential.
- The relationship is moderate (Spearman ~0.35-0.48), not deterministic: ~33% of failing goals were left unchanged, and 63% of lowered goals still lie above the measured value. The association is weaker for name-matched renamed bodies (Spearman 0.15 vs 0.41 for unchanged codes), so mismatches in the name-based linking may also dilute it.
- The 2003-2008 measurements show a much weaker link (0.11) with the SGBP2 -> SGBP3 change; the old measurements are only available for a subset (n=637) and refer to a far earlier period.
- Data cannot show intent or procedure (the motivation files `toestandbeoordeling-motivering` were not analysed).

## 5. Anomalies and caveats

- No `VoorgangerCode`/`TypeWijzigingCode` in the OWL files for any year; renamed codes (2013->2014, 2018->2020) were linked heuristically by name + waterbeheerder. 123 (2013->2025) / 66 (2015->2021) new and 84 / 36 old bodies remain unmatched.
- Cl goals have a mixed/range structure in ~7% of Cl goals (duplicate `matig` rows, `goed` with a non-zero lower bound, non-monotonic upper bounds, open upper bounds). "Upper bound of `goed`" is not a valid goal for these; Cl deltas such as +100 or -2,800 mg/l in the CSV are artefacts of this.
- EKR boundaries: 18 gaps in set 2014 (matig upper > goed lower; goal taken as goed lower bound), `NL43_16` OVWFLORA (2020) clearly mistyped (0.83/0.167), `NL34M101` MAFAUNA.
- Ptot goals for 38 Zeeland bodies are absent in the 2025 set, and `Nanorg` (68 rows) was not analysed.
- Three natural-body goals (0.69/0.61/0.71 for `NL11_4_1`) deviate from 0.60.
- Set labels equal first file year; the 2018 set differs from 2015 by one added body, not by any changed goal.
- Goals per water body may count several water bodies with the same name within one waterbeheerder (name matching required uniqueness on both sides).
- Natural bodies are few (35-56 goals) so natural-body statistics are small-n.
- Numeric measured EKR for 2014-2019 does not exist in the files; "earlier measured" is therefore the 2009-2019 mean (2020 file). Measured values and goal derivation may use different methods/versions.
- The chain "SGBP2 2014 correction -> SGBP3 2021 -> 2025" is covered by 2015 -> 2021 and 2021 -> 2025; all other pairs and group splits are in `doelen_changes_summary.csv`.

## 6. Visualisation ideas for a storytelling Shiny app

1. **Slope chart of goals per set.** For a selected water body or beheerder: one line per water body x element from SGBP2 (2015 set) to SGBP3 (2021/2025), coloured by direction (lowered/raised/equal), with the 0.60 line highlighted; filter on element and KRW status.
2. **Distribution shift (ridgeline/histogram).** Density of EKR goals per element for HMWB and artificial bodies in 2015 vs 2021/2025, showing the pile at 0.60 shrinking (51.5% -> 66% of goals below 0.6; 0.60 count 1,196 -> 799) and the new tail down to 0.1.
3. **"Goal vs earlier measured EKR" scatter.** x = measured EKR 2009-2019, y = change in goal (or new goal), colour by element, with the 1:1 line and the old goal as horizontal reference; a toggle shows lowering rate per gap bin (75% lowered when >0.15 below the goal, 8% when above).
4. **Waterbeheerder small multiples / diverging bars.** Per waterbeheerder the number of lowered vs raised goals (Hollandse Delta 86 down / 0 up, Drents Overijsselse Delta 51 up / 9 down), clickable to a map or a table of bodies.
5. **Timeline of goal sets.** A stepped timeline 2013-2025 with the nine sets, marking SGBP2 -> SGBP3 (2018 -> 2020) as the turning point and the smaller 2023 revision; heat tile per element x set of the share of goals changed.
6. (Bonus) **Goal staircase per body**: bar showing goal value with the classes (slecht ... goed) and the measured EKR marker, so users see which side of the GEP/GES line each body is on, before and after the change.
