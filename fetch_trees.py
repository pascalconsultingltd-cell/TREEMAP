# Fetch GLA public realm trees within RADIUS_M of NW5 2TE into trees.js (loadable from file://).
import json, math, subprocess
API = "https://apps.london.gov.uk/api/tables/public-realm-trees-2026/trees"
LAT, LON, RADIUS_M = 51.548553, -0.130711, 1000
BOROUGHS = ["E09000007", "E09000019", "E09000014"]  # Camden, Islington, Haringey
COLS = "uniqueid,common_name,taxon_species,gla_name,age_cat,height_m,canopy_m,girth_dbh,climate_suitability,location,maintainer,pos_4326"
def dist(lat, lon):
    x = math.radians(lon - LON) * math.cos(math.radians((lat + LAT) / 2))
    return 6371000 * math.hypot(x, math.radians(lat - LAT))
trees = []
for b in BOROUGHS:
    offset = 0
    while True:
        url = f"{API}?borough_id=eq.{b}&select={COLS}&order=uniqueid&limit=10000&offset={offset}"
        rows = json.loads(subprocess.run(["curl", "-sf", url], capture_output=True, check=True).stdout)  # API returns 403 to urllib
        for r in rows:
            lon, lat = r.pop("pos_4326")["coordinates"]
            d = dist(lat, lon)
            if d <= RADIUS_M: trees.append({**r, "lat": round(lat, 6), "lon": round(lon, 6), "dist": round(d)})
        if len(rows) < 10000: break
        offset += 10000
    print(b, "done,", len(trees), "trees so far")
with open("trees.js", "w", encoding="utf-8") as f:
    f.write(f"const CENTRE = [{LAT}, {LON}], RADIUS_M = {RADIUS_M}, HOME = \"NW5 2TE\";\nconst TREES = {json.dumps(trees, separators=(',', ':'))};\n")
print(len(trees), "trees written to trees.js")
