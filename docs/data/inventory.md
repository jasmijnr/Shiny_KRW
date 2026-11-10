# Local data inventory (downloaded 2026-11-10 from wkp.rws.nl)

All CSVs: UTF-8 **with BOM**, `;` separator, `.` decimal, CRLF. One file per reporting year (`Rapportagejaar`).
The `.zip` files in the root are identical to the extracted folders; use the folders.
PDFs next to the CSVs are IHW metadata (attribute descriptions, licence CC-BY 4.0).

| Folder / file pattern | Years | Grain | Size | Notes |
|---|---|---|---|---|
| `WKP_download_OWL_*/WKP_KRW-oppervlaktewaterlichamen_Nederland_<Y>_*.csv` | 2009, 2013–2025 | 1 row per water body (~745) | ~180 kB | Master table: district, provincie, beheerder, status, categorie, watertype, length/area, `VoorgangerCode`, `TypeWijziging*` |
| `WKP_download_doelen_*/WKP_KRW-doelen_Nederland_<Y>_*.csv` | 2013–2025 | water body × element × class | ~7–8 MB | Class bounds (`Ondergrens*`, `Bovengrens*`). One goal set per file (see below) |
| `WKP_download_oordelen_*/WKP_KRW-toestandsoordelen-beknopt_Nederland_<Y>_*.csv` | 2009, 2014–2025 | water body × element | 20–35 MB | Final verdict per element: `Classificatie`, `BepalendKental` (EKR / concentration), unit, period. **Best source for the app** |
| `WKP_download_oordelen_*/WKP_KRW-toestandsoordelen_Nederland_<Y>_*.csv` | 2009, 2015–2025 | all test results | up to 150 MB | Per monitoring type, aggregation method, norm group, n measurements. 2014 = header only. Use duckdb/arrow |
| `WKP_download_oordelen_*/WKP_KRW-toestandbeoordeling-motivering_Nederland_<Y>_*.csv` | 2015–2025 | water body | small | Free text: `MotiveringEcologie`, `MotiveringChemie`, `Toelichting`, drinking water verdicts. 2009/2014 empty. Good input for AI texts |
| `Literatuur/protocol-monitoring-en-toestandsbeoordeling-krw-errata-verwerkt-2021.pdf` | – | – | 3.5 MB | RWS protocol for monitoring & status assessment |

## Goal sets per doelen file
| File year | Goal set |
|---|---|
| 2013 | 2009 set, corrected 2012 (SGBP1) |
| 2014 | set 2013 for SGBP2 |
| 2015–2019 | 2014 correction of 2013 set |
| 2020 | set 2020 for SGBP3 |
| 2021–2022 | set 2021 for SGBP3 |
| 2023 / 2024 / 2025 | yearly updated SGBP3 sets |

## Join keys
- Water body: `WaterlichaamCode` (normalise with `toupper()`; case differs, e.g. `NL02L10a`). Codes changed massively at
  2013→2014 and 2018→2020 (none 2020→2025). **`VoorgangerCode` is empty in every OWL file and in the WFS** (verified), so
  predecessor links must be reconstructed, e.g. by unique name + beheerder (see `docs/analysis/doelen_over_tijd.md`,
  ~199 of 235 vanished codes recovered for 2015→2021) or by spatial overlap of old and new geometries.
- Element: `KRWkwaliteitselementCode` (biology in EKR: `FYTOPL`, `MAFAUNA`, `OVWFLORA`, `VIS`; nutrients `Ptot`, `Ntot`; etc.).
- Year: `Rapportagejaar`.
- `ProvincieCode`/`ProvincieNaam` may contain multiple values separated by ` | `.

## Coverage 2025
742 water bodies in OWL, 741 with goals, 745 with verdicts (small mismatches to investigate).

## Geometry
Not in the CSVs. Use the WFS: see `docs/sources/wfs_rws.md`.
