# One-off: fetch OSM streets, parks, water, rail and buildings around NW5 2TE into basemap.js (our own map, no tiles).
import json, subprocess
LAT, LON, R = 51.548553, -0.130711, 1300  # a bit beyond the 1 km tree circle
Q = f"""[out:json][timeout:120];
(way[highway](around:{R},{LAT},{LON}); way[railway~"^(rail|subway|light_rail)$"](around:{R},{LAT},{LON});
 way[leisure~"^(park|garden|pitch|playground|nature_reserve)$"](around:{R},{LAT},{LON}); way[landuse~"^(grass|cemetery|allotments|recreation_ground|forest|meadow)$"](around:{R},{LAT},{LON});
 way[natural~"^(water|wood|scrub)$"](around:{R},{LAT},{LON}); way[building](around:{R},{LAT},{LON}););
out tags geom;"""
# Overpass mirror: overpass-api.de returns 406 to curl
out = subprocess.run(["curl", "-sf", "--data-urlencode", f"data={Q}", "https://maps.mail.ru/osm/tools/overpass/api/interpreter"], capture_output=True, check=True).stdout
MAJOR = {"motorway", "trunk", "primary", "secondary", "tertiary"}
base = {"major": [], "minor": [], "path": [], "rail": [], "green": [], "water": [], "building": []}
names = {}
for w in json.loads(out)["elements"]:
    t, pts = w.get("tags", {}), [[round(p["lat"], 6), round(p["lon"], 6)] for p in w.get("geometry", [])]
    h = t.get("highway")
    if h: kind = "major" if h.split("_")[0] in MAJOR else "path" if h in ("footway", "path", "cycleway", "steps", "pedestrian", "bridleway", "track") else "minor"
    elif "railway" in t: kind = "rail"
    elif "building" in t: kind = "building"
    elif t.get("natural") == "water": kind = "water"
    else: kind = "green"
    base[kind].append(pts)
    if h and t.get("name") and kind != "path": names.setdefault(t["name"], pts[len(pts) // 2])  # one label point per street
base["labels"] = [[n, p] for n, p in names.items()]
with open("basemap.js", "w", encoding="utf-8") as f: f.write(f"const BASEMAP = {json.dumps(base, separators=(',', ':'))};\n")
print({k: len(v) for k, v in base.items()})
