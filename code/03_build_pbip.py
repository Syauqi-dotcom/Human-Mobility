"""Generates the Power BI Project (PBIP): TMDL semantic model + PBIR report definition.
Run: python code/03_build_pbip.py [DATA_FOLDER]   -> powerbi/JogjaPulse.pbip
DATA_FOLDER = absolute path of data/processed as seen by Power BI Desktop (default: the folder on this machine).
"""
import json, sys, shutil, hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PB = ROOT / "powerbi"
DATA = sys.argv[1] if len(sys.argv) > 1 else str(ROOT / "data/processed")
if PB.exists(): shutil.rmtree(PB)
SM, RP = PB / "JogjaPulse.SemanticModel", PB / "JogjaPulse.Report"
(SM / "definition/tables").mkdir(parents=True); (RP / "definition/pages").mkdir(parents=True)
T = "\t"

# ------------------------------------------------------------------ semantic model
# table -> (csv, [(col, kind, format)])  kinds: s=string i=int64 d=double t=date b=boolean
TABLES = {
 "dim_date": ("dim_date.csv", [("date","t","yyyy-mm-dd"),("weekday","s",None),("weekday_num","i",None),("month","s",None),
    ("is_weekend","b",None),("is_holiday","b",None),("holiday_name","s",None),("day_type","s",None),
    ("precipitation_sum","d","0.0"),("temperature_2m_mean","d","0.0"),("temperature_2m_max","d","0.0"),("rain_class","s",None),("anomaly_flag","b",None)]),
 "dim_kapanewon": ("dim_kapanewon.csv", [("kapanewon_code","s",None),("kapanewon","s",None),("kab_kota","s",None),("slot_coverage","d","0%"),
    ("day_night_ratio","d","0.00"),("peak_hour","i",None),("n_users","i","#,0"),("pop_actual","d","#,0"),("ratio","d","0.0%"),("functional_type","s",None)]),
 "dim_cell": ("dim_cell.csv", [("cell_id","s",None),("centroid_lon","d","0.0000"),("centroid_lat","d","0.0000"),("mean_share","d","0.000%"),
    ("days_published","i",None),("share_Weekday","d","0.000%"),("share_Weekend","d","0.000%"),("share_Holiday","d","0.000%"),
    ("holiday_uplift","d","0.00"),("weekend_uplift","d","0.00"),("rank","i",None)]),
 "fact_hourly": ("fact_hourly.csv", [("kapanewon_code","s",None),("date","t","yyyy-mm-dd"),("hour","i",None),("n_maids","i","#,0"),("n_pings","i","#,0")]),
 "fact_daily": ("fact_daily.csv", [("date","t","yyyy-mm-dd"),("device_hours","i","#,0"),("pings","i","#,0"),("baseline","d","#,0"),("activity_index","d","0.000")]),
 "fact_cell_daily": ("fact_cell_daily.csv", [("cell_id","s",None),("date","t","yyyy-mm-dd"),("n_maids","i","#,0"),("share","d","0.000%")]),
 "fact_od": ("fact_od.csv", [("month","s",None),("origin_code","s",None),("dest_code","s",None),("origin_kab_kota","s",None),("dest_kab_kota","s",None),
    ("origin_kapanewon","s",None),("dest_kapanewon","s",None),("n_maids","i","#,0"),("reduced_quality","b",None),("n_homed_maids_daytime","i","#,0"),("visit_share","d","0.0%"),("is_internal","b",None)]),
}
DT = {"s":("string","type text"),"i":("int64","Int64.Type"),"d":("double","type number"),"t":("dateTime","type date"),"b":("boolean","type logical")}

def table_tmdl(name, csv, cols):
    sel = ", ".join(f'"{c}"' for c,_,_ in cols)
    tr = ", ".join(f'{{"{c}", {DT[k][1]}}}' for c,k,_ in cols)
    o = [f"table {name}", ""]
    for c,k,f in cols:
        o += [f"{T}column {c}", f"{T}{T}dataType: {DT[k][0]}"]
        if f: o.append(f"{T}{T}formatString: {f}")
        o += [f"{T}{T}summarizeBy: none", f"{T}{T}sourceColumn: {c}", ""]
    o += [f"{T}partition {name} = m", f"{T}{T}mode: import", f"{T}{T}source =", f"{T}{T}{T}let",
          f'{T}{T}{T}{T}Source = Csv.Document(File.Contents(DataFolder & "\\{csv}"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),',
          f"{T}{T}{T}{T}Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),",
          f"{T}{T}{T}{T}Selected = Table.SelectColumns(Promoted, {{{sel}}}),",
          f'{T}{T}{T}{T}Typed = Table.TransformColumnTypes(Selected, {{{tr}}}, "en-US")',
          f"{T}{T}{T}in", f"{T}{T}{T}{T}Typed", ""]
    return "\n".join(o)

for n,(csv,cols) in TABLES.items():
    (SM / f"definition/tables/{n}.tmdl").write_text(table_tmdl(n, csv, cols), encoding="utf-8")

MEASURES = [
 ("Device-Hours", "SUM(fact_hourly[n_maids])", "#,0", "Sum of hourly distinct-device counts (device-hours). NOT additive distinct devices."),
 ("Pings", "SUM(fact_hourly[n_pings])", "#,0", None),
 ("Pings per Device-Hour", "DIVIDE([Pings], [Device-Hours])", "0.00", None),
 ("Share of Region %", "DIVIDE([Device-Hours], CALCULATE([Device-Hours], ALL(dim_kapanewon)))", "0.0%", "Share of region-wide device-hours; neutralises the shrinking device sample."),
 ("Share of Day %", "DIVIDE([Device-Hours], CALCULATE([Device-Hours], ALL(fact_hourly[hour])))", "0.0%", "Hourly share of the day's activity."),
 ("Activity Index", "AVERAGE(fact_daily[activity_index])", "0.000", "Daily device-hours / 15-day rolling median (1.0 = local baseline)."),
 ("Avg Rainfall mm", "AVERAGE(dim_date[precipitation_sum])", "0.0", None),
 ("Avg Day/Night Ratio", "AVERAGE(dim_kapanewon[day_night_ratio])", "0.00", None),
 ("Cell Mean Share", "AVERAGE(fact_cell_daily[share])", "0.000%", None),
 ("OD Visitors", "SUM(fact_od[n_maids])", "#,0", None),
 ("OD Outbound", "CALCULATE([OD Visitors], fact_od[is_internal] = FALSE())", "#,0", "Inter-kapanewon visitors by home (origin) kapanewon."),
 ("OD Inbound", "CALCULATE([OD Visitors], fact_od[is_internal] = FALSE(), USERELATIONSHIP(fact_od[dest_code], dim_kapanewon[kapanewon_code]))", "#,0", "Inter-kapanewon visitors by destination kapanewon."),
 ("Attraction Ratio", "DIVIDE([OD Inbound], [OD Outbound])", "0.00", ">1 = net attractor of visitors."),
 ("Device Penetration %", "DIVIDE(SUM(dim_kapanewon[n_users]), SUM(dim_kapanewon[pop_actual]))", "0.0%", "Home-located devices / BPS population."),
]
m = ["table _Measures", ""]
for n,e,f,d in MEASURES:
    if d: m.append(f"{T}/// {d}")
    m += [f"{T}measure '{n}' = {e}", f"{T}{T}formatString: {f}", ""]
m += [f"{T}column Dummy", f"{T}{T}isHidden", f"{T}{T}dataType: int64", f"{T}{T}summarizeBy: none", f"{T}{T}sourceColumn: [Dummy]", "",
      f"{T}partition _Measures = calculated", f"{T}{T}mode: import", f"{T}{T}source = ROW(\"Dummy\", 1)", ""]
(SM / "definition/tables/_Measures.tmdl").write_text("\n".join(m), encoding="utf-8")

rel = [("fact_hourly.kapanewon_code","dim_kapanewon.kapanewon_code",1),("fact_hourly.date","dim_date.date",1),
       ("fact_daily.date","dim_date.date",1),("fact_cell_daily.cell_id","dim_cell.cell_id",1),("fact_cell_daily.date","dim_date.date",1),
       ("fact_od.origin_code","dim_kapanewon.kapanewon_code",1),("fact_od.dest_code","dim_kapanewon.kapanewon_code",0)]
r = []
for i,(a,b,act) in enumerate(rel):
    r += [f"relationship {hashlib.md5(a.encode()+b.encode()).hexdigest()}", f"{T}fromColumn: {a}", f"{T}toColumn: {b}"]
    if not act: r.append(f"{T}isActive: false")
    r.append("")
(SM / "definition/relationships.tmdl").write_text("\n".join(r), encoding="utf-8")
(SM / "definition/database.tmdl").write_text("database\n\tcompatibilityLevel: 1600\n", encoding="utf-8")
names = list(TABLES) + ["_Measures"]
model = ["model Model", f"{T}culture: en-US", f"{T}defaultPowerBIDataSourceVersion: powerBI_V3", f"{T}discourageImplicitMeasures", ""]
model += [f"ref table {n}" for n in names] + [""]
model += [f'expression DataFolder = "{DATA}" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]', ""]
(SM / "definition/model.tmdl").write_text("\n".join(model), encoding="utf-8")
(SM / "definition.pbism").write_text(json.dumps({"version": "4.0", "settings": {}}, indent=2))

# ------------------------------------------------------------------ report (PBIR)
SCH = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition"
MEAS = {n for n,*_ in MEASURES}
def fld(ent, prop):
    k = "Measure" if (ent == "_Measures" and prop in MEAS) else "Column"
    return {k: {"Expression": {"SourceRef": {"Entity": ent}}, "Property": prop}}
def proj(ent, prop, rename=None):
    p = {"field": fld(ent, prop), "queryRef": f"{ent}.{prop}", "nativeQueryRef": prop}
    return p
def M(n): return proj("_Measures", n)
def C(t, c): return proj(t, c)
def lit(s): return {"expr": {"Literal": {"Value": f"'{s}'"}}}
def lit_raw(v): return {"expr": {"Literal": {"Value": v}}}

pages = []; nvis = [0]
def page(title, visuals):
    pid = "p" + hashlib.md5(title.encode()).hexdigest()[:18]
    d = RP / f"definition/pages/{pid}"; (d / "visuals").mkdir(parents=True)
    (d / "page.json").write_text(json.dumps({"$schema": f"{SCH}/page/2.0.0/schema.json", "name": pid, "displayName": title,
        "displayOption": "FitToPage", "height": 720, "width": 1280}, indent=2))
    for i,v in enumerate(visuals):
        vid = "v" + hashlib.md5(f"{title}{i}".encode()).hexdigest()[:18]
        (d / f"visuals/{vid}").mkdir()
        (d / f"visuals/{vid}/visual.json").write_text(json.dumps(v(vid, i), indent=2))
    pages.append(pid)

def visual(vtype, x, y, w, h, title, roles, objects=None, sort=None):
    def build(name, z):
        q = {"queryState": {r: {"projections": ps} for r, ps in roles.items()}}
        if sort: q["sortDefinition"] = {"sort": [{"field": sort[0], "direction": sort[1]}], "isDefaultSort": True}
        vis = {"visualType": vtype, "query": q, "drillFilterOtherVisuals": True,
               "visualContainerObjects": {"title": [{"properties": {"show": lit_raw("true"), "text": lit(title)}}]} if title else {}}
        if objects: vis["objects"] = objects
        return {"$schema": f"{SCH}/visualContainer/2.0.0/schema.json", "name": name,
                "position": {"x": x, "y": y, "z": z, "height": h, "width": w, "tabOrder": z}, "visual": vis}
    return build
def textbox(x, y, w, h, text, size=20, bold=True):
    def build(name, z):
        return {"$schema": f"{SCH}/visualContainer/2.0.0/schema.json", "name": name,
          "position": {"x": x, "y": y, "z": z, "height": h, "width": w, "tabOrder": z},
          "visual": {"visualType": "textbox", "objects": {"general": [{"properties": {"paragraphs": [{"textRuns": [
            {"value": text, "textStyle": {"fontSize": f"{size}pt", "fontWeight": "bold" if bold else "normal"}}]}]}}]},
            "drillFilterOtherVisuals": True}}
    return build
def card(x,y,w,h,measure,title): return visual("card", x,y,w,h, title, {"Values":[M(measure)]})
def slicer(x,y,w,h,t,c,title): return visual("slicer", x,y,w,h, title, {"Values":[C(t,c)]})

# Page 1 - overview & sample drift
page("1. Overview", [
 textbox(20, 8, 1240, 44, "JogjaPulse - Human Mobility in D.I. Yogyakarta (Dec 2021 - Apr 2022)", 20),
 card(20,60,200,90,"Device-Hours","Device-hours (all)"), card(230,60,200,90,"Pings per Device-Hour","Pings / device-hour"),
 card(440,60,200,90,"Activity Index","Avg activity index"), card(650,60,200,90,"Avg Rainfall mm","Avg rainfall (mm/day)"),
 slicer(870,60,390,90,"dim_kapanewon","kab_kota","Regency / city"),
 visual("lineChart",20,160,620,270,"Daily activity index (1.0 = baseline, drift-corrected)",{"Category":[C("dim_date","date")],"Y":[M("Activity Index")]}),
 visual("lineChart",650,160,610,270,"Raw device-hours per day (sample shrinks ~9x)",{"Category":[C("dim_date","date")],"Y":[M("Device-Hours")]}),
 visual("lineChart",20,440,620,270,"Hourly rhythm by day type (share of day)",{"Category":[C("fact_hourly","hour")],"Y":[M("Share of Day %")],"Series":[C("dim_date","day_type")]}),
 visual("clusteredColumnChart",650,440,610,270,"Activity index by weekday",{"Category":[C("dim_date","weekday")],"Y":[M("Activity Index")]}),
])
# Page 2 - spatial hotspots
page("2. Spatial Hotspots", [
 textbox(20,8,1240,44,"Where are people? 500 m grid presence (k-anonymised, k=5)",20),
 slicer(20,60,300,80,"dim_date","day_type","Day type"),
 card(330,60,250,80,"Cell Mean Share","Mean cell share"),
 visual("scatterChart",20,150,780,560,"500 m cells: location (lon/lat), size = mean daily share",
   {"Category":[C("dim_cell","cell_id")],"X":[C("dim_cell","centroid_lon")],"Y":[C("dim_cell","centroid_lat")],"Size":[C("dim_cell","mean_share")]}),
 visual("tableEx",810,150,450,270,"Top cells by presence",{"Values":[C("dim_cell","cell_id"),C("dim_cell","centroid_lat"),C("dim_cell","centroid_lon"),C("dim_cell","mean_share")]},sort=(fld("dim_cell","mean_share"),"Descending")),
 visual("tableEx",810,430,450,280,"Top weekend-uplift cells (leisure / tourism)",{"Values":[C("dim_cell","cell_id"),C("dim_cell","weekend_uplift"),C("dim_cell","holiday_uplift"),C("dim_cell","days_published")]},sort=(fld("dim_cell","weekend_uplift"),"Descending")),
])
# Page 3 - kapanewon functions
page("3. Sub-district Profiles", [
 textbox(20,8,1240,44,"Functional profiles of 78 kapanewon: day vs night presence",20),
 slicer(20,60,400,80,"dim_kapanewon","functional_type","Functional type (k-means on 24h profile)"),
 slicer(430,60,300,80,"dim_kapanewon","kab_kota","Regency / city"),
 card(740,60,250,80,"Device Penetration %","Devices / population"),
 visual("clusteredBarChart",20,150,620,560,"Day/night presence ratio by kapanewon",{"Category":[C("dim_kapanewon","kapanewon")],"Y":[M("Avg Day/Night Ratio")]},sort=(fld("_Measures","Avg Day/Night Ratio"),"Descending")),
 visual("scatterChart",650,150,610,270,"Representativeness: population vs devices",{"Category":[C("dim_kapanewon","kapanewon")],"X":[C("dim_kapanewon","pop_actual")],"Y":[C("dim_kapanewon","n_users")]}),
 visual("lineChart",650,430,610,280,"24h share by regency",{"Category":[C("fact_hourly","hour")],"Y":[M("Share of Day %")],"Series":[C("dim_kapanewon","kab_kota")]}),
])
# Page 4 - OD flows
page("4. Origin-Destination", [
 textbox(20,8,1240,44,"Home-based visitation flows (Dec-Feb reliable; Mar-Apr flagged reduced quality)",20),
 slicer(20,60,300,80,"fact_od","month","Month"), slicer(330,60,300,80,"fact_od","reduced_quality","Reduced quality flag"),
 card(640,60,200,80,"OD Outbound","Inter-kapanewon visitors"),
 visual("pivotTable",20,150,620,560,"Origin regency x destination regency (visitors, incl. internal)",{"Rows":[C("fact_od","origin_kab_kota")],"Columns":[C("fact_od","dest_kab_kota")],"Values":[M("OD Visitors")]}),
 visual("clusteredBarChart",650,150,610,270,"Top net attractors (inbound/outbound ratio)",{"Category":[C("dim_kapanewon","kapanewon")],"Y":[M("Attraction Ratio")]},sort=(fld("_Measures","Attraction Ratio"),"Descending")),
 visual("clusteredBarChart",650,430,610,280,"Top destinations by inbound visitors",{"Category":[C("dim_kapanewon","kapanewon")],"Y":[M("OD Inbound")]},sort=(fld("_Measures","OD Inbound"),"Descending")),
])
# Page 5 - weather & holidays (source 2)
page("5. Weather & Holidays", [
 textbox(20,8,1240,44,"External source: Open-Meteo rainfall + Indonesian public holidays",20),
 slicer(20,60,300,80,"dim_date","month","Month"), slicer(330,60,300,80,"dim_date","day_type","Day type"),
 visual("scatterChart",20,150,620,280,"Rainfall vs activity index (each dot = day)",{"Category":[C("dim_date","date")],"X":[M("Avg Rainfall mm")],"Y":[M("Activity Index")]}),
 visual("clusteredColumnChart",650,150,610,280,"Activity index by rain class",{"Category":[C("dim_date","rain_class")],"Y":[M("Activity Index")]}),
 visual("lineChart",20,440,620,270,"Daily rainfall (mm)",{"Category":[C("dim_date","date")],"Y":[M("Avg Rainfall mm")]}),
 visual("tableEx",650,440,610,270,"Holidays & activity",{"Values":[C("dim_date","date"),C("dim_date","holiday_name"),M("Activity Index")]}),
])

(RP / "definition/version.json").write_text(json.dumps({"$schema": f"{SCH}/versionMetadata/1.0.0/schema.json", "version": "2.0.0"}, indent=2))
(RP / "definition/report.json").write_text(json.dumps({"$schema": f"{SCH}/report/3.0.0/schema.json",
   "themeCollection": {"baseTheme": {"name": "CY24SU10", "reportVersionAtImport": "5.61", "type": "SharedResources"}},
   "layoutOptimization": "None", "settings": {"useStylableVisualContainerHeader": True}}, indent=2))
(RP / "definition/pages/pages.json").write_text(json.dumps({"$schema": f"{SCH}/pagesMetadata/1.0.0/schema.json", "pageOrder": pages, "activePageName": pages[0]}, indent=2))
(RP / "definition.pbir").write_text(json.dumps({"version": "4.0", "datasetReference": {"byPath": {"path": "../JogjaPulse.SemanticModel"}}}, indent=2))
(PB / "JogjaPulse.pbip").write_text(json.dumps({"version": "1.0", "artifacts": [{"report": {"path": "JogjaPulse.Report"}}], "settings": {"enableAutoRecovery": True}}, indent=2))
(PB / ".gitignore").write_text("**/.pbi/localSettings.json\n**/.pbi/cache.abf\n")
print("PBIP written to", PB, "| DataFolder =", DATA)
