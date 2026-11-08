"""ETL: JogjaPulse (Zenodo) + Open-Meteo weather + Indonesian public holidays -> tidy tables for analysis & Power BI.
Run:  python code/01_etl.py   (from project root)
"""
import json, urllib.request
from pathlib import Path
import numpy as np, pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW, OUT = ROOT / "data/raw", ROOT / "data/processed"
OUT.mkdir(parents=True, exist_ok=True)

# ---------- SOURCE 1: JogjaPulse (Zenodo 10.5281/zenodo.23157460) ----------
hourly = pd.read_csv(RAW / "presence_kapanewon_hourly.csv", parse_dates=["date"])
cell = pd.read_csv(RAW / "presence_cell500m_daily.csv", parse_dates=["date"])
od = pd.read_csv(RAW / "od_home_visits_kapanewon_monthly.csv")
orig = pd.read_csv(RAW / "od_origin_homes_monthly.csv")
pop = pd.read_csv(RAW / "home_maids_vs_population_kapanewon.csv")

# ---------- SOURCE 2: Open-Meteo archive API (daily weather, Yogyakarta) + national holidays ----------
wcache = RAW / "weather_open_meteo.csv"
if not wcache.exists():
    url = ("https://archive-api.open-meteo.com/v1/archive?latitude=-7.8&longitude=110.37"
           "&start_date=2021-12-01&end_date=2022-04-30"
           "&daily=precipitation_sum,temperature_2m_mean,temperature_2m_max,rain_sum"
           "&timezone=Asia%2FBangkok")
    d = json.load(urllib.request.urlopen(url, timeout=60))["daily"]
    pd.DataFrame(d).rename(columns={"time": "date"}).to_csv(wcache, index=False)
weather = pd.read_csv(wcache, parse_dates=["date"])

# Indonesian national holidays / cuti bersama (SKB 3 Menteri 2021 & 2022), Dec 2021 - Apr 2022
holidays = pd.DataFrame([
    ("2021-12-24", "Cuti Bersama Natal"), ("2021-12-25", "Natal"),
    ("2022-01-01", "Tahun Baru Masehi"), ("2022-02-01", "Tahun Baru Imlek"),
    ("2022-02-28", "Isra Mi'raj"), ("2022-03-03", "Nyepi"), ("2022-04-15", "Wafat Isa Almasih"),
], columns=["date", "holiday_name"]).assign(date=lambda x: pd.to_datetime(x.date))

# ---------- dim_date ----------
dates = pd.DataFrame({"date": pd.date_range("2021-12-01", "2022-04-30")})
dates["weekday_num"] = dates.date.dt.dayofweek
dates["weekday"] = dates.date.dt.day_name()
dates["month"] = dates.date.dt.strftime("%Y-%m")
dates["is_weekend"] = dates.weekday_num >= 5
dates = dates.merge(holidays, on="date", how="left").merge(weather, on="date", how="left")
dates["is_holiday"] = dates.holiday_name.notna()
dates["day_type"] = np.select([dates.is_holiday, dates.is_weekend], ["Holiday", "Weekend"], "Weekday")
dates["rain_class"] = pd.cut(dates.precipitation_sum, [-1, 1, 10, 30, 1e9], labels=["Dry (<1mm)", "Light (1-10)", "Moderate (10-30)", "Heavy (>30)"]).astype(str)
dates["anomaly_flag"] = dates.date.isin(pd.to_datetime(["2022-01-01", "2022-02-16", "2022-03-08"]))  # README sample breaks / outage

# ---------- hourly: normalise for the changing device sample (README sec. 6) ----------
hourly["dow"] = hourly.date.dt.dayofweek
# total device-hours in each (date,hour) over all kapanewon -> share of the region's activity
tot = hourly.groupby(["date", "hour"], as_index=False).n_maids.sum().rename(columns={"n_maids": "region_maids"})
hourly = hourly.merge(tot, on=["date", "hour"])
hourly["share"] = hourly.n_maids / hourly.region_maids
hourly["pings_per_maid"] = hourly.n_pings / hourly.n_maids

daily_k = (hourly.groupby(["kapanewon_code", "kapanewon", "kab_kota", "date"], as_index=False)
           .agg(device_hours=("n_maids", "sum"), pings=("n_pings", "sum"), hours_published=("hour", "nunique")))
dtot = daily_k.groupby("date").device_hours.transform("sum")
daily_k["share"] = daily_k.device_hours / dtot

daily = (hourly.groupby("date", as_index=False)
         .agg(device_hours=("n_maids", "sum"), pings=("n_pings", "sum")))
daily["pings_per_device_hour"] = daily.pings / daily.device_hours
# detrended activity index = day / centred 15-day rolling median (removes sample-composition drift)
daily = daily.merge(dates, on="date")
daily["baseline"] = daily.device_hours.rolling(15, center=True, min_periods=5).median()
daily["activity_index"] = daily.device_hours / daily.baseline
# distinct devices per day is not additive; proxy = max over hours of the region sum is also biased -> use device-hours

# ---------- kapanewon profile / day-night ----------
# Own-normalised 24h profile (mean n_maids per hour / mean over 24h). Suppressed slots (<5 devices) are missing,
# so only kapanewon with >=60% of all hour slots published are typed; the rest are "Insufficient data (suppressed)".
hw = hourly.merge(dates[["date", "is_weekend", "is_holiday"]], on="date")
hw = hw[~hw.is_weekend & ~hw.is_holiday]
prof = hw.groupby(["kapanewon_code", "hour"]).n_maids.mean().unstack()
cover = hourly.groupby("kapanewon_code").size() / (151 * 24)
prof_n = prof.div(prof.mean(axis=1), axis=0)
day = prof_n.loc[:, 9:17].mean(axis=1); night = prof_n.loc[:, 0:5].mean(axis=1)
kap = hourly[["kapanewon_code", "kapanewon", "kab_kota"]].drop_duplicates().set_index("kapanewon_code")
kap["slot_coverage"] = cover
kap["day_night_ratio"] = day / night
kap["peak_hour"] = prof_n.idxmax(axis=1)
kap = kap.reset_index()
kap = kap.merge(pop.rename(columns={"KAB_KOTA": "kab_kota", "KEC_KAPN": "kapanewon"}), on=["kab_kota", "kapanewon"], how="left")

from sklearn.cluster import KMeans
ok = kap.slot_coverage >= 0.60
X = prof_n.loc[kap[ok].kapanewon_code].values
km = KMeans(3, n_init=20, random_state=7).fit(X)
kap.loc[ok, "cluster_raw"] = km.labels_
order = kap[ok].groupby("cluster_raw").day_night_ratio.mean().sort_values().index.tolist()
names = ["Night-heavy / round-the-clock", "Mixed residential-commercial", "Daytime activity centre"]
kap["functional_type"] = kap.cluster_raw.map(dict(zip(order, names))).fillna("Insufficient data (suppressed)")
kap.to_csv(OUT / "dim_kapanewon.csv", index=False)
prof_n.reset_index().melt("kapanewon_code", var_name="hour", value_name="rel_activity").to_csv(OUT / "profile_kapanewon_hour.csv", index=False)

# ---------- cells ----------
ctot = cell.groupby("date").n_maids.transform("sum")
cell["share"] = cell.n_maids / ctot
dim_cell = cell.groupby(["cell_id", "centroid_lon", "centroid_lat"], as_index=False).agg(
    mean_share=("share", "mean"), days_published=("date", "nunique"), total_device_days=("n_maids", "sum"))
cell = cell.merge(dates[["date", "day_type"]], on="date")
dt = cell.groupby(["cell_id", "day_type"]).share.mean().unstack()
dim_cell = dim_cell.merge(dt.add_prefix("share_"), left_on="cell_id", right_index=True, how="left")
dim_cell["holiday_uplift"] = dim_cell.share_Holiday / dim_cell.share_Weekday
dim_cell["weekend_uplift"] = dim_cell.share_Weekend / dim_cell.share_Weekday
dim_cell["rank"] = dim_cell.mean_share.rank(ascending=False, method="first").astype(int)
dim_cell.to_csv(OUT / "dim_cell.csv", index=False)
cell[["cell_id", "date", "n_maids", "share"]].to_csv(OUT / "fact_cell_daily.csv", index=False)

# ---------- OD ----------
od = od.merge(orig[["month", "origin_code", "n_homed_maids_daytime"]], on=["month", "origin_code"], how="left")
od["visit_share"] = od.n_maids / od.n_homed_maids_daytime
od["is_internal"] = od.origin_code == od.dest_code
od.to_csv(OUT / "fact_od.csv", index=False)
orig.to_csv(OUT / "fact_origin_homes.csv", index=False)

# ---------- write ----------
dates.to_csv(OUT / "dim_date.csv", index=False)
daily.to_csv(OUT / "fact_daily.csv", index=False)
daily_k.to_csv(OUT / "fact_daily_kapanewon.csv", index=False)
hourly.drop(columns=["kab_code", "dow"]).to_csv(OUT / "fact_hourly.csv", index=False)
print({p.name: len(pd.read_csv(p)) for p in sorted(OUT.glob("*.csv"))})
