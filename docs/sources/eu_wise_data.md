# EU WISE WFD data for NL vs IT comparison

Research date: 2026-11-10. Legend: **[V]** = verified by actually fetching (WebFetch) in this session; **[D]** = taken from official documentation/web pages read (or search-result summaries), not tested by a query; **[I]** = inferred / needs checking.

## Summary

- The EU-level WFD data are the **WISE WFD Database** (EEA, DAT-124), fed by Article 13 / RBMP reporting (1st 2010, 2nd 2016, 3rd 2022 cycles). Tables are served through **Discodata** (`[WISE_WFD].[latest].[SWB_SurfaceWaterBody]` etc.). The table name is confirmed on the WISE Freshwater chart page [V]. The EEA dataset metadata gives **no licence** [V]; the WISE Freshwater site states the **EEA standard re-use policy** (free re-use incl. commercial, with acknowledgement) [V].
- **Discodata SQL returned HTTP 403 from this machine** (WebFetch and curl; Azure gateway) [V]. It is not confirmed that it works from R; it may block non-browser clients or this network. I did not try to circumvent it. Test from the user's own R session first.
- **EEA ArcGIS REST services (WISE_WFD folder) work anonymously and support attribute queries, group-by statistics and geometry** [V]. This is the only programmatic route verified end-to-end, and it already holds water-body-level status per cycle (2010/2016/2022) plus quality elements, pressures and geometry.
- Water-body-level data available: category, natural/HMWB/AWB, type code, ecological status/potential class, chemical status class (also without uPBT), assessment year, confidence, expected achievement date, **19 quality-element classes**, significant pressures/impacts, exemption types, failing priority substances [V for ArcGIS field lists and XSD page].
- **Not available at EU level: actual EQR values, class boundaries / GES-GEP targets per water body, monitoring values.** Only class codes (1-5, Unknown). The schema has no EQR elements [V].
- Water body counts in 3rd-cycle ArcGIS layers [V]: **NL 741** (234 river line + 492 lake + 6 transitional + 9 coastal; 0 river polygons) vs **IT 7,763** (6,876 river line + 347 lake + 147 transitional + 393 coastal). IT matches ISPRA's ">7,700". Ratio about 10x.
- Lake ecological status, ArcGIS [V]: NL 324 code 3, 116 code 4, 50 code 5, 2 unknown (none code 1 or 2). IT: 1 code 1, 125 code 2, 136 code 3, 9 code 4, 2 code 5, 74 unknown. (Mapping 1=high ... 5=bad is [I], consistent with the schema's "class codes 1-5".)
- Italy: ISPRA says unknown ecological status fell from 18% (2nd) to 10% (3rd cycle); 43.6% good or better ecological, just over 75% good chemical (ISPRA report 427/2026) [D, from search summaries]. Richer national data: ISPRA INSPIRE WFS (CC BY 4.0, per search summary) [D]; no documented SINTAI API found.
- Cross-country comparison should use length/area-weighted shares, per category, with "unknown" shown explicitly, and NL's large HMWB/AWB share in view.

## Data sources

| Name | Content | Format | Access URL | Licence |
|---|---|---|---|---|
| WISE WFD Database (DAT-124), tables "WISE_WFD latest" | Art. 13 RBMP reporting: SWB, GWB, RBD, status, pressures, impacts, exemptions, per cycle | Discodata SQL/JSON/CSV | Catalogue https://sdi.eea.europa.eu/catalogue/srv/api/records/dc1b1cdf-5fa0-4535-8c89-10cc051e00db ; page https://www.eea.europa.eu/data-and-maps/data/wise-wfd-3 ; Discodata https://discodata.eea.europa.eu/ [V pages] | Not stated in metadata [V]; WISE Freshwater: EEA standard re-use policy [V] |
| Discodata SQL API | e.g. `[WISE_WFD].[latest].[SWB_SurfaceWaterBody]` | JSON via `/sql?query=` | `https://discodata.eea.europa.eu/sql?query=...` (403 from here) | EEA re-use policy |
| WISE WFD reference spatial datasets 2022 (v1.9, Sept 2025, public) | RBD, sub-units, SWB, GWB, monitoring sites, QE; 3rd RBMP delineations, 2019-2025 | GeoPackage; ESRI REST; WMS | Datahub https://www.eea.europa.eu/en/datahub/datahubitem-view/73ab1aa2-2f69-4881-941d-4429875ca715 ; GPKG https://sdi.eea.europa.eu/data/effd82dc-31cb-4bb6-8d8b-572322c124a2 ; tech report https://sdi.eea.europa.eu/catalogue/api/records/effd82dc-31cb-4bb6-8d8b-572322c124a2/attachments/WISE_WFD_ReferenceSpatialDataSets_2025-09%20v1.9.pdf [V page; GPKG size unknown, check before downloading] | Not stated [V] |
| WISE WFD reference spatial datasets 2016 (2nd RBMP) | Same for 2nd cycle, v1.9, 2016-2025 | GeoPackage, REST, WMS | https://www.eea.europa.eu/data-and-maps/data/wise-wfd-spatial/surface-water-body [V page] | Not stated |
| EEA ArcGIS REST, folder WISE_WFD | 27 MapServers incl. WFD2010_/WFD2016_/WFD2022_ SurfaceWaterBody_WM, SurfaceWaterBodyCentreline_WM, QualityElements_WM, SurfaceWaterBody_swSignificantPressureType_WM, WFD2022_SurfaceWaterBody_AWBHMWB_WM, MonitoringSite, RiverBasinDistrict, ProtectedArea | Esri JSON / GeoJSON via `/query` | https://water.discomap.eea.europa.eu/arcgis/rest/services/WISE_WFD (marine.discomap.eea.europa.eu serves the same) [V] | Not stated |
| WFD reporting guidance + XSD 2022 | Data model SWB_2022.xsd, SWMET, RBMPPoM; Access template | PDF, XSD, .accdb | https://cdr.eionet.europa.eu/help/WFD/WFD_715_2022 ; https://dd.eionet.europa.eu/schema/WFD2022/SWB_2022.xsd/view [V] | n/a |
| Possible bulk zip `wise-wfd-database_v01_r04.zip` (~299 MB, Dec 2022) | Unknown contents; probably superseded | zip | Seen only in a search snippet; URL not confirmed [I]. Do not rely on it. | ? |
| ISPRA WFD INSPIRE WFS (Italy) | River network / SWB 2016-2022 | WFS (GeoServer at sdi.isprambiente.it/geoserver) | INSPIRE record `ispra_rm:Meta_2016WFD:WFS` on inspire-geoportal.ec.europa.eu (my fetch failed: expired TLS certificate) [D] | CC BY 4.0 per metadata [D] |
| ISPRA report 427/2026 "Lo stato delle acque in Italia" | National synthesis of 3rd cycle, pressures, exemptions, measures | PDF (~17 MB) | https://www.isprambiente.gov.it/files2026/pubblicazioni/rapporti/rapporto-427_26.pdf [V page link] | ISPRA site terms (unchecked) |
| EEA "Europe's state of water 2024" | EU synthesis: 37% good/high ecological, 29% good chemical (80% excluding uPBT) | HTML/PDF | https://www.eea.europa.eu/en/analysis/publications/europes-state-of-water-2024 [V] | EEA |

## Access recipes

### 1. Discodata (NOT verified: HTTP 403 from here)
Attempted `https://discodata.eea.europa.eu/sql?query=select count(*) ... from [WISE_WFD].[latest].[SWB_SurfaceWaterBody] where countryCode in ('IT','NL') group by countryCode` -> **403 Forbidden** (WebFetch and curl; Microsoft Azure Application Gateway). Try from R on the user's machine:

```r
library(httr2)
q <- "select countryCode, count(*) as n
      from [WISE_WFD].[latest].[SWB_SurfaceWaterBody]
      where countryCode in ('IT','NL') group by countryCode"
resp <- request("https://discodata.eea.europa.eu/sql") |>
  req_url_query(query = q) |>
  req_perform() |>
  resp_body_json()
dplyr::bind_rows(resp$results)   # JSON shape {"results":[...]} is from memory [I]
```
Notes [I]: Discodata uses T-SQL (`select top N`); paging via `&p=<page>&nrOfHits=<n>`; column names probably mirror the XSD (`countryCode`, `euSurfaceWaterBodyCode`, `swEcologicalStatusOrPotentialValue`, `cYear` ...) but are not verified. Inspect with `select top 1 *`. Filter on `cYear`/cycle to separate cycles.

### 2. ArcGIS REST (VERIFIED)
Layer ids in `WFD2022_SurfaceWaterBody_WM/MapServer` [V]: 2 river line, 3 river polygon, 4 lake, 5 transitional, 6 coastal (0,1 are groups; 7+ are chemical status layers).

Count (returned `{"count":347}` for IT lakes, 492 for NL) [V]:
```
https://marine.discomap.eea.europa.eu/arcgis/rest/services/WISE_WFD/WFD2022_SurfaceWaterBody_WM/MapServer/4/query?where=countryCode%3D%27IT%27&returnCountOnly=true&f=json
```
Group-by statistics (worked) [V]:
```
.../MapServer/4/query?where=countryCode in ('IT','NL')&groupByFieldsForStatistics=countryCode,swEcologicalStatusOrPotentialValue&outStatistics=[{"statisticType":"count","onStatisticField":"OBJECTID","outStatisticFieldName":"n"}]&f=json
```
Attributes without geometry (worked; response flags `exceededTransferLimit`, so page with `resultOffset`/`resultRecordCount`) [V]:
```
.../MapServer/4/query?where=countryCode='NL'&outFields=euSurfaceWaterBodyCode,surfaceWaterBodyName,naturalAWBHMWB,surfaceWaterBodyTypeCode,swEcologicalStatusOrPotentialValue,swChemicalStatusValue&returnGeometry=false&resultRecordCount=1000&resultOffset=0&f=json
```
maxRecordCount is 2000 [V]. R sketch (not run):
```r
library(httr2); library(sf)
base <- "https://marine.discomap.eea.europa.eu/arcgis/rest/services/WISE_WFD/WFD2022_SurfaceWaterBody_WM/MapServer"
get_page <- function(layer, where, offset = 0, geom = FALSE) {
  request(paste0(base, "/", layer, "/query")) |>
    req_url_query(where = where, outFields = "*", returnGeometry = tolower(geom),
                  outSR = 4326, resultOffset = offset, resultRecordCount = 1000, f = "geojson") |>
    req_perform() |> resp_body_string()
}
# loop until fewer than 1000 features come back; parse with sf::read_sf(json_string)
```
The Italian river layer has 6,876 lines: page it, or restrict by `euRBDCode`.

### 3. GeoPackage download (offline use)
Public v1.9 GPKG: https://sdi.eea.europa.eu/data/effd82dc-31cb-4bb6-8d8b-572322c124a2 [link from Datahub page; size and layer names not checked, may exceed 50 MB so do not put it in the project]. Read with `sf::st_layers()` then `sf::read_sf(layer=)`, or duckdb with the spatial extension (`ST_Read`).

### 4. Related services
- Quality elements: `WFD2022_QualityElements_WM` (layers 2-6, one per water body category) [V].
- Pressures: `WFD2022_SurfaceWaterBody_swSignificantPressureType_WM` (layers per pressure group P1, P2, P2-2 ...; field `swSignificantPressureType`) [V].
- HMWB/AWB: `WFD2022_SurfaceWaterBody_AWBHMWB_WM` exists [V], fields not read.
- Same services exist for `WFD2016_` and `WFD2010_` [V list]; their field lists were not checked.

## Fields available vs not available

### Available
ArcGIS `WFD2022_SurfaceWaterBody_WM` fields [V]: cYear, countryCode, euRBDCode, euSubUnitCode, euSurfaceWaterBodyCode, surfaceWaterBodyName, cArea, cLength, hasDescriptiveData, surfaceWaterBodyCategory, naturalAWBHMWB, reservoir, surfaceWaterBodyTypeCode, surfaceWaterBodyTransboundary, NCSWaterBodyType, swEcologicalStatusOrPotentialValue, swEcologicalAssessmentYear, swEcologicalAssessmentConfidence, swEcologicalStatusOrPotentialExpectedAchievementDate, swChemicalStatusValue, swChemicalAssessmentYear, swChemicalAssessmentConfidence, swChemicalMonitoringResults, swChemicalStatusExpectedAchievementDate, swChemicalStatusValueWithoutUPBT.

Full reporting schema SWB_2022.xsd [V]: in addition hmwbWaterUse, hmwbPhysicalAlteration, surfaceWaterBodyIntercalibrationType, swMixingZones, swSignificantPressureType/Other, swSignificantImpactType/Other, swChemicalStatusGrouping. Child tables: FailingRBSP; SWEcologicalExemptionType (+ swEcologicalExemptionPressure); **QualityElement, exactly 19 per water body** (qeCode, qeStatusOrPotentialValue, qeStatusOrPotentialChange, qeStatusOrPotentialComparability, qeMonitoringResults, qeMonitoringPeriod, qeGrouping, qeEcologicalExemptionType); SWPrioritySubstance (+ SWChemicalExemptionType); SWAssociatedProtectedArea. Programme of measures sits in the RBMPPoM schema (RBD / measure level) [D, not inspected].

Quality element columns in the ArcGIS QE service [V]: QE1 (biological) with QE1_1, QE1_2 (+ QE1_2_1..4), QE1_3, QE1_4; QE2 (hydromorphology) QE2_1..3; QE3 (physico-chemical) QE3_1 (+ QE3_1_1..QE3_1_6_2) and QE3_3. The mapping to names (QE1_1 phytoplankton, QE1_2 other aquatic flora = macrophytes/phytobenthos, QE1_3 benthic invertebrates, QE1_4 fish) follows the WFD Annex V / WISE codelist and is [I]; confirm with `qeCodeAndphysChemParameterRelationship.xlsx` at https://cdr.eionet.europa.eu/help/WFD/WFD_715_2022/Guidance%20documents/qeCodeAndphysChemParameterRelationship.xlsx

Status codes: 1-5 plus "Unknown" observed in `swEcologicalStatusOrPotentialValue` [V]. Meaning 1=High, 2=Good, 3=Moderate, 4=Poor, 5=Bad is [I]; verify with the codelist. Potential vs status for HMWB/AWB uses the same field.

Types: national `surfaceWaterBodyTypeCode` (NL examples M7b, M14, M30 [V]). There is no broad-type field in the layer. `surfaceWaterBodyIntercalibrationType` exists in the schema (completeness unknown) [V schema]. Meaning of `NCSWaterBodyType` unclear [I].

### NOT available at EU level
- **Actual EQR values** per quality element or water body: not in the schema, only classes. NL EKR values from WKP have no EU counterpart.
- **Class boundaries / GES-GEP targets / reference conditions per water body**: no fields. Method descriptions are in separate national method reporting (SWMET), not harmonised numbers [D/I].
- **Monitoring values / time series** (that is WISE SoE Water Quality / Waterbase, a different dataset, station based).
- Concentrations per priority substance: only which substances cause failure.
- Magnitude of pressures: only presence/type of significant pressure.
- Broad (common) type: must be derived from national type via a mapping you build.

## Italy notes
- Surface water bodies (3rd cycle, EEA ArcGIS) [V]: 7,763 = 6,876 river (line) + 347 lake + 147 transitional + 393 coastal. ISPRA: more than 7,700 [D].
- Lakes: 74 of 347 unknown ecological status (21%), vs NL 2 of 492 [V]. Rivers, transitional and coastal not yet queried: rerun the group-by on layers 2, 5, 6.
- ISPRA: unknown ecological status 18% (2nd) to 10% (3rd cycle); unknown chemical status strongly reduced; 43.6% good or better ecological; about 75% good chemical [D, search summaries; not checked in the PDF].
- Commission assessment of Italy's 3rd RBMPs: SWD(2025) 18 (4 Feb 2025) [D]; contents not read.
- Italy is organised in river basin districts with regional ARPA agencies monitoring, so methods and intensity vary regionally [I, general knowledge].
- National sources: ISPRA report 427/2026 (PDF; no machine-readable annex found) [V]; ISPRA indicators https://indicatoriambientali.isprambiente.it [D]; ISPRA INSPIRE WFS (CC BY 4.0) [D]. SINTAI and regional ARPA portals: **no documented public API found**; treat as unknown. No endpoints are invented here.

## Comparability caveats NL vs IT
- Delineation: NL about 741 large bodies (canals, lakes, large rivers) vs IT about 7,760 small ones (many river segments). Counts are not comparable; weight by `cLength` (rivers) and `cArea` (lakes, coastal, transitional). Both countries' rivers are line features in this layer.
- HMWB/AWB: NL has a very high share (the 3 sample lake records returned were all artificial [V]); status is then ecological *potential* with different targets. Compare natural vs HMWB/AWB separately.
- Methods: national class boundaries, intercalibration only for some quality elements and types, one-out-all-out, and extrapolation/grouping (`qeGrouping`, `swEcologicalAssessmentConfidence`) differ by country [D].
- Unknown status: large in IT, small in NL. Always show it.
- Chemical status: ubiquitous PBT substances (mercury, PBDE) cause nearly universal failure; use `swChemicalStatusValueWithoutUPBT` too. EEA: 29% good with uPBT vs 80% without [V].
- Cycle changes: methods changed between cycles; trends are weak. `qeStatusOrPotentialComparability` flags this [D].
- Coverage: the EEA chart only includes countries that have reported electronically for the 3rd cycle (23 EU countries listed) [V]; State of water 2024 used 19 Member States for WFD [V]. EEA shows counts by country; whether it weights by length/area is [I].
- Existing EEA visualisations (do not duplicate): "surface water bodies ecological status or potential by country" (1st-3rd RBMP) https://water.europa.eu/freshwater/europe-freshwater/visualization/surface-water-bodies-ecological-status-or-potential-by-country [V]; "ecological status map by RBD" https://water.europa.eu/freshwater/europe-freshwater/maps/ecological-status-map-by-rbd [D, URL from search]; country profiles https://water.europa.eu/freshwater/countries/wfd/italy [V] with charts on chemical status, natural/HMWB/AWB, pressures, protected areas. Gap: BQE-level comparison, length/area-weighted shares, type-specific comparison, narrative.

## Suggested comparisons (defensible)
1. Share in good-or-high ecological status/potential per category (river, lake, transitional, coastal), weighted by length/area, with unknown as its own bar; counts as sensitivity check.
2. Natural vs HMWB/AWB share per country, and status within each group.
3. Share unknown plus assessment confidence distribution (data-quality story).
4. Failing share per biological quality element (phytoplankton, macrophytes/phytobenthos, invertebrates, fish) within the same category/type; shows what drives failure.
5. Chemical status with and without uPBT.
6. Significant pressure groups: share of water bodies affected (agriculture, hydromorphology, point sources), presented as reported presence, not magnitude.
7. Exemptions (Art 4.4/4.5): share of failing bodies with exemption type and expected achievement date.
8. Cycle 2 to 3 shift at aggregate level, with caveat.
9. Map using the spatial layers, aggregated to RBD for readability.
Avoid: comparing EQR values or class boundaries across countries; ranking countries on raw share good.

## Open questions
- Does Discodata work from R / the user's network (403 here)? Real column names and status codelist (`select top 1 *`).
- Is there an official bulk export of the WISE_WFD tables (zip/SQLite)? `wise-wfd-database_v01_r04.zip` is unconfirmed. GPKG size unknown.
- Which `cYear` values occur in the ArcGIS layers (counts matched ISPRA, so likely 3rd cycle only).
- Code meanings (1-5 mapping, potential vs status, "Unknown" vs null); 19 QE codes to names; broad-type mapping.
- IT/NL status for rivers, transitional and coastal; fields of the AWBHMWB service.
- Licence: no explicit licence on the dataset records; confirm the EEA re-use policy wording.
- ISPRA WFS endpoint URL and layers (record fetch failed on an expired certificate); Italian regional/ARPA portals and any APIs.
- Whether measures (PoM) can be linked to water bodies in Discodata.
