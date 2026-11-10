# RWS / IHW WFS (Waterkwaliteitsportaal geodata)

Verified on 2026-11-10 with GetCapabilities / DescribeFeatureType / GetFeature.

- Endpoint: `https://geo.rijkswaterstaat.nl/services/ogc/wkp/wkp/wfs` (GeoServer; WFS 1.0.0, 1.1.0, 2.0.0)
- WMS (used by wkp.rws.nl/geoviewer): `https://geo.rijkswaterstaat.nl/services/ogc/wkp/wkp/wms`
- Output formats include `application/json` (GeoJSON), GML2/3, `SHAPE-ZIP`, CSV, KML. Paging supported (`count`, `startIndex`).
- Coordinates come back in **RD New (EPSG:28992)** by default; request `srsName=EPSG:4326` for Leaflet/MapLibre, or transform in R.

## Feature types
| Layer | Content |
|---|---|
| `wkp:KRWoppervlaktewaterlichamen` | Surface water bodies: `lokaleCode`, `internationaleCode`, `naam`, `versie`, `versieBegindatum/Einddatum`, `voorgangerCode`, `typeWijziging`, status, categorie, watertype, beheerder, `geometrie`, `geometrieCentroid` |
| `wkp:KRWoppervlaktewaterlichamen_toestand_ecologie` | Geometry + ecological state per element (feature id e.g. `…ecologie.NL02L1.FYTOPL`) |
| `wkp:KRWoppervlaktewaterlichamen_toestand_chemie` | Geometry + chemical state |
| `wkp:KRWoppervlaktewaterlichamen_toestand_stoffen` | Geometry + state per substance |
| `wkp:KRWstroomgebieddistricten`, `wkp:KRWdeelstroomgebieddistricten` | River basin (sub)districts |
| `wkp:KRWmonitoringlocaties_ow`, `wkp:KRWmonitoringlocaties_gw` | Monitoring locations |
| `wkp:KRWgrondwaterlichamen*` | Groundwater bodies and their state |
| `wkp:KRWdrinkwater`, `wkp:KRWschelpdierwater`, `wkp:LEWmeetobjecten`, `wkp:factsheets_*` | Other |

## Recipes
```
# all surface water bodies as GeoJSON in WGS84
https://geo.rijkswaterstaat.nl/services/ogc/wkp/wkp/wfs?service=WFS&version=2.0.0&request=GetFeature
  &typeNames=wkp:KRWoppervlaktewaterlichamen&outputFormat=application/json&srsName=EPSG:4326
```
```r
library(sf)
url <- paste0("https://geo.rijkswaterstaat.nl/services/ogc/wkp/wkp/wfs?service=WFS&version=2.0.0",
              "&request=GetFeature&typeNames=wkp:KRWoppervlaktewaterlichamen",
              "&outputFormat=application/json&srsName=EPSG:4326")
owl <- sf::st_read(url, quiet = TRUE)
owl <- owl |> dplyr::mutate(wl_code = toupper(lokaleCode))   # join key to CSVs (WaterlichaamCode)
```
Cache the result locally (e.g. `data/geo/owl.gpkg`) and simplify geometry (`rmapshaper::ms_simplify`) for the app;
do not query the WFS at every app start.

## Coverage (checked 2026-11-10)
- `KRWoppervlaktewaterlichamen` returns **745 features, all `versie = 2024` (valid 2024-01-01 – 2024-12-31)**: only the
  current SGBP3 geometry, no history. That is enough for maps of SGBP3 years (2022–2025).
- For maps of SGBP1/SGBP2 water bodies (codes that no longer exist), historical shapefiles from the
  downloadmodule (https://wkp.rws.nl/downloadmodule) are needed. `voorgangerCode`/`typeWijziging` are empty for all 745
  features, so old→new links must come from name matching or spatial overlay with historical shapefiles.
