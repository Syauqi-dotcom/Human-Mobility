"""Build an equirectangular DIY basemap (lon/lat linear) from OpenStreetMap tiles, for a Power BI scatter background.
Usage: python code/basemap.py data/basemap/diy_basemap.png [osm|satellite]   (axes in code/03_build_pbip.py must match LON0..LAT1)
"""
import io, math, sys, time, urllib.request
import numpy as np
from PIL import Image, ImageDraw, ImageFont

LON0, LON1, LAT0, LAT1 = 109.92, 110.94, -8.22, -7.52   # must equal the scatter axis start/end
Z, T = 11, 256                                            # zoom, tile size
W = 1600
H = round(W * ((LAT1 - LAT0) * 1.0) / ((LON1 - LON0) * math.cos(math.radians(7.87))))


def tx(lon):  # fractional tile x
    return (lon + 180) / 360 * 2 ** Z


def ty(lat):  # fractional tile y (web mercator)
    r = math.radians(lat)
    return (1 - math.log(math.tan(r) + 1 / math.cos(r)) / math.pi) / 2 * 2 ** Z


x0, x1 = int(tx(LON0)), int(tx(LON1))
y0, y1 = int(ty(LAT1)), int(ty(LAT0))
STYLE = sys.argv[2] if len(sys.argv) > 2 else 'osm'
ESRI = 'https://server.arcgisonline.com/ArcGIS/rest/services'
LAYERS = {  # (url template, mode)
    'osm': [('https://tile.openstreetmap.org/{z}/{x}/{y}.png', 'RGB')],
    'satellite': [(ESRI + '/World_Imagery/MapServer/tile/{z}/{y}/{x}', 'RGB'),
                  (ESRI + '/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}', 'RGBA')],
}[STYLE]


def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'student-course-project/1.0'})
    return Image.open(io.BytesIO(urllib.request.urlopen(req, timeout=30).read()))


mosaic = Image.new('RGBA', ((x1 - x0 + 1) * T, (y1 - y0 + 1) * T))
for tmpl, mode in LAYERS:
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            tile = fetch(tmpl.format(z=Z, x=x, y=y)).convert('RGBA')
            mosaic.alpha_composite(tile, ((x - x0) * T, (y - y0) * T))
            time.sleep(0.2)
mosaic = mosaic.convert('RGB')

# resample: output column -> lon (linear), output row -> lat (linear) -> mercator pixel
src = np.asarray(mosaic)
lons = LON0 + (np.arange(W) + 0.5) / W * (LON1 - LON0)
lats = LAT1 - (np.arange(H) + 0.5) / H * (LAT1 - LAT0)
px = ((np.array([tx(v) for v in lons]) - x0) * T).astype(int).clip(0, src.shape[1] - 1)
py = ((np.array([ty(v) for v in lats]) - y0) * T).astype(int).clip(0, src.shape[0] - 1)
out = Image.fromarray(src[py[:, None], px[None, :]])
if STYLE == 'osm':  # light greyscale so the Power BI markers stand out
    out = Image.fromarray((np.asarray(out.convert('L'), dtype=float) * 0.62 + 255 * 0.38).astype(np.uint8)).convert('RGB')

d = ImageDraw.Draw(out)
try:
    font = ImageFont.truetype('arial.ttf', 18)
except OSError:
    font = ImageFont.load_default()
note = {'osm': '© OpenStreetMap contributors', 'satellite': 'Imagery © Esri, Maxar, Earthstar Geographics'}[STYLE]
tw = d.textlength(note, font=font)
d.rectangle([W - tw - 16, H - 30, W, H], fill=(255, 255, 255))
d.text((W - tw - 8, H - 26), note, fill=(90, 90, 90), font=font)
out.save(sys.argv[1], optimize=True)
print(out.size, 'tiles', (x1 - x0 + 1) * (y1 - y0 + 1))
