"""Analytics + static figures. Run after 01_etl.py. Findings are printed and saved to outputs/findings.txt"""
from pathlib import Path
import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
P, FIG = ROOT / "data/processed", ROOT / "outputs/figures"
FIG.mkdir(parents=True, exist_ok=True)
plt.rcParams.update({"figure.dpi": 130, "axes.spines.top": False, "axes.spines.right": False, "font.size": 10})
C = "#2a6f97"; C2 = "#e07a1f"
log = []
def say(*a):
    s = " ".join(str(x) for x in a); print(s); log.append(s)

daily = pd.read_csv(P / "fact_daily.csv", parse_dates=["date"])
hourly = pd.read_csv(P / "fact_hourly.csv", parse_dates=["date"])
kap = pd.read_csv(P / "dim_kapanewon.csv")
cell = pd.read_csv(P / "dim_cell.csv")
od = pd.read_csv(P / "fact_od.csv")
dk = pd.read_csv(P / "fact_daily_kapanewon.csv", parse_dates=["date"])

# 1 --- sample drift (why normalisation is needed) + anomalies
fig, ax = plt.subplots(figsize=(9, 3.6))
ax.plot(daily.date, daily.device_hours, color=C, label="Device-hours / day (raw)")
ax.plot(daily.date, daily.baseline, color=C2, lw=1.5, label="15-day median baseline")
for d, t in [("2022-01-01", "1 Jan"), ("2022-02-16", "16 Feb"), ("2022-03-08", "8 Mar")]:
    ax.axvline(pd.Timestamp(d), color="grey", ls=":"); ax.text(pd.Timestamp(d), ax.get_ylim()[1]*.95, t, fontsize=8, rotation=90, va="top")
ax.set_title("Observed device sample shrinks ~10x -> raw counts must be normalised"); ax.legend(frameon=False); fig.tight_layout()
fig.savefig(FIG / "01_sample_drift.png"); plt.close(fig)
m = daily.groupby("month").device_hours.mean()
say(f"[1] Mean daily device-hours: {m.iloc[0]:,.0f} (Dec) -> {m.iloc[-1]:,.0f} (Apr), x{m.iloc[0]/m.iloc[-1]:.1f} decline")

# 2 --- hourly rhythm by day type (share of the day, so unaffected by sample size)
h = hourly.merge(daily[["date", "day_type", "precipitation_sum"]], on="date")
hd = h.groupby(["date", "hour", "day_type"], as_index=False).n_maids.sum()
hd["p"] = hd.n_maids / hd.groupby("date").n_maids.transform("sum")
prof = hd.groupby(["day_type", "hour"]).p.mean().unstack(0)
fig, ax = plt.subplots(figsize=(8, 3.8))
for c, col in zip(["Weekday", "Weekend", "Holiday"], [C, C2, "#6a994e"]):
    ax.plot(prof.index, prof[c] * 100, marker="o", ms=3, label=c, color=col)
ax.set_xlabel("Hour (WIB)"); ax.set_ylabel("% of day's device-hours"); ax.set_title("Diurnal mobility rhythm by day type"); ax.legend(frameon=False); fig.tight_layout()
fig.savefig(FIG / "02_hourly_profile.png"); plt.close(fig)
say(f"[2] Peak hour weekday={prof.Weekday.idxmax()}h, weekend={prof.Weekend.idxmax()}h, trough={prof.Weekday.idxmin()}h")

# 3 --- day type effect on detrended activity index (Mann-Whitney)
d = daily[~daily.anomaly_flag & daily.activity_index.notna()]
g = d.groupby("day_type").activity_index.agg(["mean", "std", "count"])
say("[3] Activity index (1.0 = local baseline):\n" + g.round(3).to_string())
wk, we = d[d.day_type == "Weekday"].activity_index, d[d.day_type != "Weekday"].activity_index
u = stats.mannwhitneyu(wk, we)
say(f"    weekday vs weekend/holiday Mann-Whitney p={u.pvalue:.2e}; diff={(we.mean()/wk.mean()-1)*100:.1f}%")
dow = d.groupby("weekday").activity_index.mean().reindex(["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"])
fig, ax = plt.subplots(figsize=(7, 3.5)); ax.bar(dow.index.str[:3], dow.values, color=[C]*5+[C2]*2)
ax.axhline(1, color="k", lw=.8); ax.set_ylim(.85, 1.1); ax.set_title("Activity index by weekday (1 = baseline)"); fig.tight_layout()
fig.savefig(FIG / "03_weekday_index.png"); plt.close(fig)

# 4 --- weather
dd = d.dropna(subset=["precipitation_sum"])
r, p = stats.spearmanr(dd.precipitation_sum, dd.activity_index)
dw = dd[dd.day_type == "Weekday"]; rw, pw = stats.spearmanr(dw.precipitation_sum, dw.activity_index)
say(f"[4] Rain vs activity index Spearman rho={r:.3f} (p={p:.3f}); weekdays only rho={rw:.3f} (p={pw:.3f})")
rc = dw.groupby("rain_class").activity_index.agg(["mean", "count"]); say(rc.round(3).to_string())
fig, ax = plt.subplots(1, 2, figsize=(10, 3.6))
ax[0].scatter(dw.precipitation_sum, dw.activity_index, c=C, s=14, alpha=.7); ax[0].set_xlabel("Daily rainfall (mm)"); ax[0].set_ylabel("Activity index"); ax[0].set_title("Rain vs activity (weekdays)")
order = ["Dry (<1mm)", "Light (1-10)", "Moderate (10-30)", "Heavy (>30)"]
dw.boxplot("activity_index", by="rain_class", positions=None, ax=ax[1], grid=False) if False else None
ax[1].boxplot([dw[dw.rain_class == o].activity_index for o in order if (dw.rain_class == o).any()], tick_labels=[o for o in order if (dw.rain_class == o).any()])
ax[1].set_title("By rain class"); plt.setp(ax[1].get_xticklabels(), fontsize=8); fig.tight_layout()
fig.savefig(FIG / "04_weather.png"); plt.close(fig)

# 5 --- functional typology of kapanewon
fig, ax = plt.subplots(figsize=(8, 4.2))
prof_k = pd.read_csv(P / "profile_kapanewon_hour.csv").merge(kap[["kapanewon_code", "functional_type"]], on="kapanewon_code")
pk = prof_k[prof_k.functional_type != "Insufficient data (suppressed)"].groupby(["functional_type", "hour"]).rel_activity.mean().unstack(0)
pk.plot(ax=ax); ax.set_ylabel("relative activity (1 = daily mean)"); ax.set_title("24-h profile by functional type (k-means, k=4)"); ax.legend(frameon=False, fontsize=8); fig.tight_layout()
fig.savefig(FIG / "05_functional_types.png"); plt.close(fig)
say("[5] Functional types:\n" + kap.groupby("functional_type").agg(n=("kapanewon", "count"), dn_ratio=("day_night_ratio", "mean"), members=("kapanewon", lambda s: ", ".join(s.head(8)))).round(2).to_string())
top = kap[kap.slot_coverage >= 0.60].sort_values("day_night_ratio", ascending=False)
fig, ax = plt.subplots(figsize=(7, 5)); t = pd.concat([top.head(10), top.tail(10)])
ax.barh(t.kapanewon, t.day_night_ratio, color=[C2]*10 + [C]*10); ax.axvline(1, color="k", lw=.8); ax.invert_yaxis(); ax.set_title("Day/night presence ratio: top & bottom 10 kapanewon"); fig.tight_layout()
fig.savefig(FIG / "06_day_night.png"); plt.close(fig)

# 6 --- representativeness
kk = kap.dropna(subset=["pop_actual"]); kk2 = kk[kk.kapanewon != "GONDOMANAN"]
r1, _ = stats.pearsonr(np.log(kk2.n_users), np.log(kk2.pop_actual))
fig, ax = plt.subplots(figsize=(5.5, 4.5)); ax.scatter(kk.pop_actual, kk.n_users, c=C, s=18)
for _, rr in kk.nlargest(2, "ratio").iterrows(): ax.annotate(rr.kapanewon, (rr.pop_actual, rr.n_users), fontsize=7)
ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlabel("BPS population"); ax.set_ylabel("Devices by home kapanewon"); ax.set_title(f"Representativeness (log-log r={r1:.2f}, excl. Gondomanan)"); fig.tight_layout()
fig.savefig(FIG / "07_representativeness.png"); plt.close(fig)
say(f"[6] Devices vs population log-log r={r1:.2f}; mean device penetration={kk.ratio.median():.1%} (median)")

# 7 --- hotspots (cells)
topc = cell.nlargest(15, "mean_share")
fig, ax = plt.subplots(1, 2, figsize=(11, 5))
sc = ax[0].scatter(cell.centroid_lon, cell.centroid_lat, c=np.log10(cell.mean_share), s=5, cmap="viridis"); ax[0].set_aspect("equal"); ax[0].set_title("500 m cell presence (log10 mean daily share)"); plt.colorbar(sc, ax=ax[0], shrink=.7)
ok = cell[cell.days_published >= 40].dropna(subset=["weekend_uplift"]); up = ok.nlargest(300, "weekend_uplift")
ax[1].scatter(cell.centroid_lon, cell.centroid_lat, c="#dddddd", s=3); s2 = ax[1].scatter(up.centroid_lon, up.centroid_lat, c=up.weekend_uplift, cmap="YlOrRd", s=14); ax[1].set_aspect("equal"); ax[1].set_title("Top 300 cells by weekend/weekday uplift\n(leisure & tourism candidates)"); plt.colorbar(s2, ax=ax[1], shrink=.7)
fig.tight_layout(); fig.savefig(FIG / "08_cell_hotspots.png"); plt.close(fig)
say("[7] Top 5 cells by mean daily share:\n" + topc.head(5)[["cell_id", "centroid_lat", "centroid_lon", "mean_share"]].to_string(index=False))
say("    Top 5 weekend-uplift cells (>=40 days):\n" + up.head(5)[["cell_id", "centroid_lat", "centroid_lon", "weekend_uplift"]].round(3).to_string(index=False))

# 8 --- OD (Dec-Feb only; Mar-Apr flagged reduced quality)
o = od[~od.reduced_quality]
inter = o[~o.is_internal]
flow = inter.groupby(["origin_kapanewon", "dest_kapanewon"]).visit_share.mean().sort_values(ascending=False)
say("[8] Top inter-kapanewon flows (mean visit share, Dec-Feb):\n" + flow.head(8).round(3).to_string())
outb = o.groupby("origin_kapanewon").apply(lambda x: x[~x.is_internal].n_maids.sum() / x.groupby("month").n_maids.sum().mean() if False else x[~x.is_internal].n_maids.sum(), include_groups=False)
inb = inter.groupby("dest_kapanewon").n_maids.sum(); outf = inter.groupby("origin_kapanewon").n_maids.sum()
net = pd.concat([inb.rename("in"), outf.rename("out")], axis=1).fillna(0); net["net"] = net["in"] - net["out"]; net["ratio"] = net["in"] / net["out"]
say("    Top attractors (in/out):\n" + net.sort_values("ratio", ascending=False).head(6).round(2).to_string())
net.to_csv(P / "od_net_balance.csv")
piv = inter.groupby(["origin_kab_kota", "dest_kab_kota"]).n_maids.sum().unstack().fillna(0); piv = piv.div(piv.sum(axis=1), axis=0)
fig, ax = plt.subplots(figsize=(6, 4.6)); im = ax.imshow(piv.values, cmap="Blues"); ax.set_xticks(range(len(piv.columns)), piv.columns, rotation=40, ha="right", fontsize=8); ax.set_yticks(range(len(piv.index)), piv.index, fontsize=8)
for i in range(piv.shape[0]):
    for j in range(piv.shape[1]): ax.text(j, i, f"{piv.values[i,j]:.0%}", ha="center", va="center", fontsize=8, color="white" if piv.values[i,j] > .5 else "k")
ax.set_title("Where residents travel: origin -> destination\n(share of inter-kapanewon visits, Dec-Feb)"); ax.set_xlabel("Destination"); ax.set_ylabel("Origin"); fig.tight_layout()
fig.savefig(FIG / "09_od_regency_matrix.png"); plt.close(fig)
piv.to_csv(P / "od_regency_matrix.csv")
# mobility reach: share of homed devices who visit another kapanewon
reach = o.groupby(["month", "origin_kapanewon"]).apply(lambda x: x[~x.is_internal].n_maids.sum(), include_groups=False).rename("out_visits").reset_index()
cm = o.groupby("month").apply(lambda x: x[~x.is_internal].n_maids.sum() / x.drop_duplicates("origin_code").n_homed_maids_daytime.sum(), include_groups=False)
say("    Mean #other-kapanewon destinations visited per device ~ (visits/home devices):\n" + cm.round(2).to_string())
# distance-free gravity-style check: log flow ~ log origin homes + log destination 'pull'
hm = pd.read_csv(P / "fact_origin_homes.csv"); hm = hm[~hm.reduced_quality].groupby("origin_code").n_homed_maids.mean()
ff = inter.groupby(["origin_code", "dest_code"]).n_maids.mean().reset_index(); ff["H"] = ff.origin_code.map(hm); ff["Pj"] = ff.dest_code.map(hm)
ff = ff.dropna(); X = np.c_[np.ones(len(ff)), np.log(ff.H), np.log(ff.Pj)]; y = np.log(ff.n_maids)
b, *_ = np.linalg.lstsq(X, y, rcond=None); r2 = 1 - ((y - X @ b) ** 2).sum() / ((y - y.mean()) ** 2).sum()
say(f"    Gravity-style regression log T ~ log H_i + log H_j: b_i={b[1]:.2f}, b_j={b[2]:.2f}, R2={r2:.2f}")

# 9 --- combined sources: weather x location (rain sensitivity by kapanewon)
dkw = dk.merge(daily[["date", "precipitation_sum", "day_type", "anomaly_flag"]], on="date"); dkw = dkw[(dkw.day_type == "Weekday") & ~dkw.anomaly_flag]
dkw["idx"] = dkw.share / dkw.groupby("kapanewon_code").share.transform(lambda s: s.rolling(15, center=True, min_periods=5).median())
res = []
for kc, x in dkw.groupby("kapanewon"):
    x = x.dropna(subset=["idx"])
    if len(x) > 40: rho, pv = stats.spearmanr(x.precipitation_sum, x.idx); res.append((kc, rho, pv))
rs = pd.DataFrame(res, columns=["kapanewon", "rho", "p"]).sort_values("rho"); rs.to_csv(P / "rain_sensitivity_kapanewon.csv", index=False)
say(f"[9] Rain sensitivity of local share (weekdays): most negative: {rs.head(3).kapanewon.tolist()}, most positive: {rs.tail(3).kapanewon.tolist()}; sig(p<.05)={int((rs.p<.05).sum())}/{len(rs)}")

(ROOT / "outputs/findings.txt").write_text("\n".join(log))
