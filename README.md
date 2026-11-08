# Human Mobility – JogjaPulse (D.I. Yogyakarta, Dec 2021 – Apr 2022)

## Data sources (2)
1. **JogjaPulse** – Zenodo 10.5281/zenodo.23157460 (CC BY 4.0): 500 m daily presence, kapanewon hourly presence, home-based OD flows, population validation.
2. **Open-Meteo Archive API** (daily rainfall/temperature, Yogyakarta) **+ Indonesian national holidays/cuti bersama** (SKB 3 Menteri, hard-coded in `01_etl.py`).

## Run
```
pip install -r requirements.txt
# put the Zenodo CSVs in data/raw/  (already downloaded)
python code/01_etl.py        # clean, normalise, join sources -> data/processed/*.csv
python code/02_analysis.py   # statistics + figures -> outputs/figures, outputs/findings.txt
python code/03_build_pbip.py "C:\path\to\data\processed"   # regenerate Power BI project
```

## Power BI
Open `powerbi/JogjaPulse.pbip` in Power BI Desktop (File > Options > Preview features > *Power BI Project (.pbip)* if asked).
Then **Home > Transform data > Edit parameters > DataFolder** = full path to `data/processed`, and Refresh.
To get a single `.pbix`: File > Save as .pbix. 5 pages: Overview, Spatial Hotspots, Sub-district Profiles, Origin-Destination, Weather & Holidays. DAX measures are in table `_Measures`.

## Key caveats handled
- Device sample shrinks ~9x (Dec→Apr) → all comparisons use shares or a detrended *activity index* (day / 15-day rolling median).
- `n_maids` is distinct count (non-additive) → summed values are called *device-hours*, not people.
- Missing rows = <5 devices (k-anonymity), not zero. OD Mar–Apr is flagged reduced quality and excluded from OD statistics.
