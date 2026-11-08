# Aggregated mobile-device presence and origin–destination data for the Special Region of Yogyakarta (DIY), Indonesia, December 2021 – April 2022

This record contains aggregated, privacy-protected counts of mobile devices (presence per grid cell and sub-district, and home-based origin–destination flows between sub-districts) derived from GPS location data in the Special Region of Yogyakarta (Daerah Istimewa Yogyakarta, DIY), Indonesia, from 1 December 2021 to 30 April 2022 (151 days). No device identifiers, individual trajectories or individual locations are included.

- **Version:** [1.0]
- **Citation:** [Widyawan (2026). JogjaPulse: An Aggregated Spatio-Temporal Mobility
Dataset for Yogyakarta, Indonesia. Zenodo. [https://doi.org/10.5281/zenodo.23157460]]
- **Associated article:** [Scientific Data article, DOI]
- **License:** [e.g. CC BY 4.0]
- **Contact:** [Ariansyah, bigdata@ugm.ac.id]

---

## 1. Source data (summary)

The aggregates were computed from 44,384,826 GPS location records ("pings") of 594,223 mobile devices, collected by a commercial location-data aggregator from mobile applications in which users had enabled location permissions, and provided to Universitas Gadjah Mada by the aggregator under a research collaboration agreement. Devices are identified in the source data by mobile advertising identifiers (MAIDs). The source data are not part of this record (see Section 7). Full details are given in the associated article.

## 2. Files

| File | Content | Rows | Size |
|---|---|---|---|
| `presence_cell500m_daily.csv` | Distinct devices per 500 m grid cell per day | 183,548 | 11.3 MB |
| `presence_kapanewon_hourly.csv` | Distinct devices and pings per kapanewon (sub-district) per hour | 230,418 | 12.2 MB |
| `home_maids_vs_population_kapanewon.csv` | Devices by estimated home kapanewon vs. official population | 78 | < 0.1 MB |
| `validation_night_presence_kapanewon.csv` | Night-time presence per kapanewon used for technical validation | 156 | < 0.1 MB |
| `tier1_summary.csv` | Row counts and suppression statistics of the two presence products | 2 | < 0.1 MB |
| `od_home_visits_kapanewon_monthly.csv` | Home-based visitation flows between kapanewon per month (origin–destination) | 9,894 | 0.8 MB |
| `od_origin_homes_monthly.csv` | Devices with a home in each origin kapanewon per month (OD denominators) | 390 | < 0.1 MB |
| `od_summary.csv` | Row counts and suppression statistics of the OD product | 1 | < 0.1 MB |
| `README.md` | This file | – | – |

All files are UTF-8 encoded, comma-separated, with a header row. Dates are `YYYY-MM-DD`.

## 3. Common definitions

| Term | Definition |
|---|---|
| **Device / MAID** | A mobile device, identified in the source data by its mobile advertising identifier. One device is not necessarily one person. |
| **Ping** | One GPS location record of a device. |
| **Presence** | A device is present in a spatial unit during a time period if it has at least one ping inside that unit during that period. |
| **`n_maids`** | Number of **distinct** devices present. Distinct counts are **not additive**: a device present in two cells (or two hours) is counted once in each. Do not sum `n_maids` across cells, kapanewon, hours or days to obtain totals. |
| **`n_pings`** | Number of pings. Additive. Ping frequency varies between devices and applications, so `n_pings` measures data volume rather than the number of people. |
| **Time zone** | All dates and hours are local time, Western Indonesia Time (WIB, UTC+7). |
| **Spatial extent** | Only pings inside the administrative boundary of DIY are counted (99.98% of source pings). |

## 4. File descriptions

### 4.1 `presence_cell500m_daily.csv`

Distinct devices per 500 m × 500 m grid cell per day. 5,715 distinct cells, 151 days.

| Column | Type | Description |
|---|---|---|
| `cell_id` | string | Cell identifier `E{i}_N{j}`, where `i = floor(easting / 500)` and `j = floor(northing / 500)` in UTM zone 49S (EPSG:32749). Example: `E790_N18255`. |
| `x_min_utm` | integer | Easting of the cell's lower-left corner, metres, EPSG:32749 (`= i × 500`). |
| `y_min_utm` | integer | Northing of the cell's lower-left corner, metres, EPSG:32749 (`= j × 500`). |
| `centroid_lon` | float | Longitude of the cell centre, WGS84 (EPSG:4326), 6 decimals. |
| `centroid_lat` | float | Latitude of the cell centre, WGS84 (EPSG:4326), 6 decimals. |
| `date` | date | Calendar day (WIB). |
| `n_maids` | integer | Distinct devices present in the cell on that day (≥ 5, see Section 5). |

The cell polygon spans `[x_min_utm, x_min_utm + 500) × [y_min_utm, y_min_utm + 500)` in EPSG:32749. This file intentionally contains no ping counts (see Section 5).

### 4.2 `presence_kapanewon_hourly.csv`

Distinct devices and pings per kapanewon (sub-district, 78 units) per hour.

| Column | Type | Description |
|---|---|---|
| `kab_code` | string | Regency/city (kabupaten/kota) code, e.g. `34.01`. |
| `kab_kota` | string | Regency/city name: KULON PROGO, BANTUL, GUNUNGKIDUL, SLEMAN, YOGYAKARTA. |
| `kapanewon_code` | string | Kapanewon code, e.g. `34.01.01`. |
| `kapanewon` | string | Kapanewon name. |
| `date` | date | Calendar day (WIB). |
| `hour` | integer | Hour of day, 0–23 (WIB); `8` means 08:00–08:59. |
| `n_maids` | integer | Distinct devices present in the kapanewon during that hour (≥ 5). |
| `n_pings` | integer | Pings recorded in the kapanewon during that hour. |

Codes, names and boundaries follow the 2023 kalurahan boundary data of the DIY Provincial Government Geoportal (Geoportal Pemerintah DIY), dissolved to kapanewon level.

### 4.3 `home_maids_vs_population_kapanewon.csv`

Number of devices by estimated home kapanewon, compared with official population. Used for the spatial representativeness validation in the associated article.

| Column | Type | Description |
|---|---|---|
| `KAB_KOTA` | string | Regency/city name. |
| `KEC_KAPN` | string | Kapanewon name. |
| `n_users` | integer | Devices whose estimated home location (most frequent night-time location, [night hours / method as described in the article]) lies in the kapanewon, December 2021 – April 2022. |
| `pop_actual` | float | Population of the kapanewon according to [BPS source, reference year]. |
| `ratio` | float | `n_users / pop_actual`. |

### 4.4 `validation_night_presence_kapanewon.csv`

Night-time presence per kapanewon computed from `presence_kapanewon_hourly.csv`, used to validate the released product against population data.

| Column | Type | Description |
|---|---|---|
| `period` | string | `Dec 2021 - Apr 2022` or `Dec 2021 - Jan 2022`. |
| `kab_kota`, `kapanewon` | string | As in 4.2. |
| `night_presence` | float | Mean hourly `n_maids` over published rows for hours 00–05 WIB in the period. |
| `slots_published_pct` | float | Percentage of night hour slots (days × 6 hours) in the period that are published, i.e. not suppressed. |
| `n_users`, `pop_actual` | | As in 4.3. |

### 4.5 `tier1_summary.csv`

| Column | Description |
|---|---|
| `pings_inside_diy_pct` | Percentage of source pings inside the DIY boundary. |
| `product` | `A_cell500m_daily` (4.1) or `B_kapanewon_hourly` (4.2). |
| `k` | Suppression threshold. |
| `rows_total` | Rows before suppression. |
| `rows_published` | Rows after suppression. |
| `rows_suppressed_pct` | Percentage of rows suppressed. |
| `maid_presence_suppressed_pct` | Percentage of the sum of `n_maids` contained in suppressed rows. |
| `n_cells_published` | Distinct cells (A) or kapanewon (B) with at least one published row. |

### 4.6 `od_home_visits_kapanewon_monthly.csv`

Home-based visitation flows: number of distinct devices whose monthly home is in origin kapanewon *i* and that were observed in destination kapanewon *j* during daytime in the same month. These are **visitor counts, not trip counts**: a device visiting *j* once or every day of the month counts once.

- **Monthly home:** for each device and month, the kapanewon with the most distinct nights with at least one ping between 22:00 and 05:59 WIB (ties broken by the number of night pings). Pings before 06:00 are assigned to the previous night. A home requires at least **2 distinct nights** in the month; devices without a home are excluded.
- **Destination:** any kapanewon in which the device has at least one ping between 08:00 and 17:59 WIB in the same month.
- Rows with *i* = *j* are included: devices observed in their own home kapanewon during daytime.

| Column | Type | Description |
|---|---|---|
| `month` | string | `YYYY-MM`, December 2021 – April 2022. |
| `origin_kab_code`, `origin_kab_kota` | string | Regency/city of the origin (home) kapanewon. |
| `origin_code`, `origin_kapanewon` | string | Origin (home) kapanewon code and name. |
| `dest_kab_code`, `dest_kab_kota` | string | Regency/city of the destination kapanewon. |
| `dest_code`, `dest_kapanewon` | string | Destination kapanewon code and name. |
| `n_maids` | integer | Distinct devices with home in the origin observed in the destination during daytime (≥ 5). |
| `reduced_quality` | boolean | `True` for March and April 2022 (see Section 6). |

### 4.7 `od_origin_homes_monthly.csv`

Denominators for the OD product, e.g. to compute the share of devices from origin *i* that visited *j* (`n_maids / n_homed_maids_daytime`).

| Column | Type | Description |
|---|---|---|
| `month` | string | `YYYY-MM`. |
| `origin_kab_code`, `origin_kab_kota`, `origin_code`, `origin_kapanewon` | string | As in 4.6. |
| `n_homed_maids` | integer | Devices with their monthly home in the kapanewon (definition as in 4.6; ≥ 5). |
| `n_homed_maids_daytime` | integer | Of these, devices observed at least once between 08:00 and 17:59 WIB in the month. Blank if fewer than 5. |
| `reduced_quality` | boolean | `True` for March and April 2022. |

Note that this monthly home definition differs from the full-period home definition used in `home_maids_vs_population_kapanewon.csv` (4.3).

### 4.8 `od_summary.csv`

| Column | Description |
|---|---|
| `k`, `min_nights` | Suppression threshold and minimum nights for a home. |
| `od_rows_total`, `od_rows_published`, `od_rows_suppressed_pct` | OD rows before and after suppression. |
| `inter_zonal_flow_kept_pct` | Share of the sum of `n_maids` over inter-zonal pairs (*i* ≠ *j*) contained in published rows. |
| `origin_rows_published` | Rows in `od_origin_homes_monthly.csv`. |

## 5. Privacy protection

- **Aggregation only.** No device identifiers, trajectories or individual locations are released.
- **Small-count suppression (k = 5).** Rows with fewer than 5 distinct devices are removed from both presence products. A missing row therefore means "fewer than 5 devices", **not zero**.
  - Cell × day: 64.6% of rows removed, containing 6.6% of total device presence.
  - Kapanewon × hour: 15.9% of rows removed, containing 0.7% of total device presence.
  - OD (kapanewon × kapanewon × month): 48.6% of rows removed, containing 4.7% of the inter-zonal flow. The origin denominators are suppressed with the same threshold.
- **Protection against differencing.** Additive counts (`n_pings`) are published only in the kapanewon product. The cell and OD products contain only distinct device counts, which are not additive across cells, destinations or time, so suppressed values cannot be recovered by subtracting published values from totals.
- **Why individual-level data are not released.** A unicity analysis following de Montjoye et al. [7] showed that 96.4% of devices remain unique given four spatio-temporal points even after coarsening locations to 500 m and time to 30 minutes.

## 6. Known limitations (read before use)

1. **The number of observed devices is not constant.** Mean distinct devices per day fall from about 87,000 (December 2021) to about 9,000 (April 2022), with abrupt drops on **1 January 2022** and **16 February 2022** and a gradual decline afterwards. These changes reflect the composition of the device sample in the source data, not changes in population mobility. **Normalise counts** (e.g. by the total number of devices observed on the same day or hour) before comparing across time.
2. **More suppression later in the period and in rural areas.** Because of (1), a larger share of rows is suppressed in March–April 2022, and suppression is concentrated in sparsely populated areas (e.g. Gunungkidul, Kulon Progo). Missing rows are not zeros.
3. **Anomalous days.** 8 March 2022 shows a one-day drop in device counts, likely a data delivery issue.
4. **Devices ≠ people.** The sample covers devices with location-enabled applications linked to the aggregator; it is not a random sample of the population. Representativeness varies by area (see Section 8), e.g. Gondomanan (central Yogyakarta City) has more observed devices than residents, likely due to visitors and tourism.
5. **Hourly night-time values in rural kapanewon** are based on few published rows (as low as 3.2% of night slots) and should be interpreted with caution.
6. **OD flows in March–April 2022 are of reduced quality** (`reduced_quality = True`). Devices with a monthly home drop from about 122,000 (December 2021) to about 14,000 (April 2022), fewer pairs pass suppression, and the flows no longer follow a clear gravity relationship (Section 8). Use them with caution, or restrict quantitative analyses to December 2021 – February 2022.
7. **OD flows capture observed visits, not all trips.** Because devices are recorded mainly when an application is in use, short or brief visits are under-represented, and a destination requires only one daytime ping. Monthly homes based on few nights may occasionally be misassigned.

## 7. Access to individual-level data

The individual-level source data are not publicly available because of third-party licensing restrictions and re-identification risk. [Describe controlled-access arrangement if any, or "They are not available for redistribution."]

## 8. Technical validation (summary)

- **Home location vs. population:** devices by estimated home kapanewon correlate with official population across kapanewon (`home_maids_vs_population_kapanewon.csv`; see the article for statistics).
- **Released product vs. population:** mean night-time presence (00–05 WIB) per kapanewon from `presence_kapanewon_hourly.csv` correlates with official population (Pearson r = 0.83 on linear scale and 0.70 on log–log scale, n = 77, excluding Gondomanan; log–log r = 0.60 including it) and with home-located devices (log–log r = 0.98).
- **Monthly homes (OD origins) vs. population:** devices per origin kapanewon correlate with official population in December 2021 – February 2022 (Pearson r = 0.82–0.87 linear, 0.68–0.74 log–log, n = 77, excluding Gondomanan), weaker in March–April 2022 (r = 0.51–0.69 linear).
- **OD plausibility:** for December 2021 – February 2022, published inter-zonal flows follow a gravity relationship, log *T*ij ~ log *H*i + log *P*j − γ log *d*ij, with origin homes *H*i, destination population *P*j and centroid distance *d*ij (R² = 0.45–0.58, distance-decay exponent γ = 0.78–0.94), and are largely reciprocal (Pearson r of log flows *i*→*j* vs *j*→*i* = 0.79–0.82). In March–April 2022, R² ≤ 0.28 and γ ≤ 0.37.
- **Temporal patterns:** activity follows a plausible diurnal cycle (minimum around 03:00, rise from 05:00, plateau 11:00–20:00 WIB) and is slightly lower on weekends, particularly Sundays.

## 9. Potential uses

The two presence products are complementary: `presence_cell500m_daily.csv` gives fine spatial detail at daily resolution, and `presence_kapanewon_hourly.csv` gives hourly resolution for coarser administrative units. Because the number of observed devices changes over time (Section 6), comparisons across dates should use normalised values (e.g. shares of the daily total) rather than raw counts.

**Cell × day (`n_maids`)**
- **Dynamic population mapping:** day-to-day distribution of people as a complement to static census data [1].
- **Disaster exposure:** number of people present in hazard zones (e.g. the slopes of Mount Merapi, the southern coast, the Opak fault zone) on given days [2].
- **Tourism and crowding:** visitor concentrations at tourist destinations (e.g. Malioboro, Gunungkidul beaches) on holidays compared with ordinary days [3].
- **Public service planning:** siting services according to where people are present rather than where they are registered.

**Kapanewon × hour (`n_maids`, `n_pings`)**
- **Daytime vs. night-time population and commuting:** identifying employment/education centres and residential areas.
- **Functional or land-use classification:** clustering the 24-hour presence profile of each kapanewon [4].
- **Time-varying exposure:** hazard exposure that differs between day and night.
- **Activity intensity:** `n_pings / n_maids` per hour as an indicator of device activity.

**Home-based OD flows (`n_maids`, monthly)**
- **Catchment areas and interaction between sub-districts:** which areas attract visitors from which residential areas, e.g. for public transport and service planning.
- **Spatial interaction modelling:** calibrating or testing gravity- and radiation-type models for a medium-sized metropolitan region.
- A comparable home-to-destination flow design has been used for SafeGraph-based flows in the United States [5].

Comparable aggregated mobility datasets have been published in *Scientific Data* [5, 6].

**References**

1. Deville, P. et al. Dynamic population mapping using mobile phone data. *PNAS* **111**, 15888–15893 (2014). https://doi.org/10.1073/pnas.1408439111
2. Bengtsson, L., Lu, X., Thorson, A., Garfield, R. & von Schreeb, J. Improved response to disasters and outbreaks by tracking population movements with mobile phone network data: a post-earthquake geospatial study in Haiti. *PLoS Med.* **8**, e1001083 (2011). https://doi.org/10.1371/journal.pmed.1001083
3. Ahas, R., Aasa, A., Roose, A., Mark, Ü. & Silm, S. Evaluating passive mobile positioning data for tourism surveys: an Estonian case study. *Tourism Manage.* **29**, 469–486 (2008).
4. Pei, T. et al. A new insight into land use classification based on aggregated mobile phone data. *Int. J. Geogr. Inf. Sci.* **28**, 1988–2007 (2014). https://doi.org/10.1080/13658816.2014.913794
5. Kang, Y. et al. Multiscale dynamic human mobility flow dataset in the U.S. during the COVID-19 epidemic. *Sci. Data* **7**, 390 (2020). https://doi.org/10.1038/s41597-020-00734-5
6. Pappalardo, L. et al. A dataset to assess mobility changes in Chile following local quarantines. *Sci. Data* **10**, 6 (2023). https://doi.org/10.1038/s41597-022-01893-3
7. de Montjoye, Y.-A., Hidalgo, C. A., Verleysen, M. & Blondel, V. D. Unique in the crowd: the privacy bounds of human mobility. *Sci. Rep.* **3**, 1376 (2013). https://doi.org/10.1038/srep01376

## 10. Code

The code used to produce these files (Apache Spark / Apache Sedona and Python) is available at [repository URL / Zenodo DOI]:

- `make_kapanewon_wkt.py`: kapanewon boundaries from the Geoportal DIY kalurahan data
- `tier1_presence.py`: presence aggregation and suppression
- `validate_tier1.py`: night-time presence validation
- `tier1_od.py`: monthly homes, home-based OD flows and suppression
- `od_feasibility.py`, `od_feasibility_analysis.py`: OD feasibility, home-vs-population and gravity-model validation

## 11. Acknowledgements and funding

[...]
