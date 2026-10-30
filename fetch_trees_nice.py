# Fetch GBIF plant sightings within RADIUS_M of Place de la Liberation, Nice, into trees_nice.js, same shape as trees.js.
# Nice's official tree file has positions but no species, so these are sightings (not an inventory): 30 m accuracy or better, one point per plant.
import json, math, subprocess
LAT, LON, RADIUS_M, HOME = 43.7104022, 7.2621427, 1000, "Place de la Libération"
URL = "https://api.gbif.org/v1/occurrence/search?geoDistance=%s,%s,1km&phylumKey=7707728&basisOfRecord=HUMAN_OBSERVATION&hasCoordinate=true&limit=300&offset=" % (LAT, LON)
INAT = "50c9509d-22c7-4a22-a47d-8c48425ef4a7"  # research-grade: confirmed by people
SOURCE = {INAT: "iNaturalist", "7a3679ef-5582-4aaa-81f0-8c2545cafc81": "Pl@ntNet", "14d5676a-2c54-4f94-9023-1e8dcd822aa0": "Pl@ntNet"}
# Legend group by genus: trees and shrubs, from any source
WOODY = {"Ceratonia": "Carob", "Celtis": "Nettle Tree", "Ficus": "Fig", "Olea": "Olive", "Laurus": "Bay", "Cydonia": "Quince", "Myrtus": "Myrtle", "Sambucus": "Elder",
  "Quercus": "Oak", "Eriobotrya": "Loquat", "Opuntia": "Prickly pear", "Pistacia": "Mastic tree", "Pittosporum": "Pittosporum", "Viburnum": "Laurustinus", "Nerium": "Oleander",
  "Ailanthus": "Tree-of-heaven", "Cercis": "Judas tree", "Melia": "Chinaberry", "Eucalyptus": "Eucalyptus", "Hibiscus": "Rose of Sharon", "Rhus": "Sumac", "Ostrya": "Hop hornbeam",
  "Pyracantha": "Firethorn", "Rhamnus": "Buckthorn", "Syringa": "Lilac", "Buxus": "Box", "Polygala": "Polygala", "Teucrium": "Shrubby germander", "Buddleja": "Buddleia", "Philadelphus": "Mock orange"}
# Edible herbs: only sightings confirmed by people, a wrong herb can be dangerous
HERBS = {"Plantago": "Plantain", "Taraxacum": "Dandelion", "Portulaca": "Purslane", "Tropaeolum": "Nasturtium", "Reichardia": "French scorzonera"}
def dist(a, b, c, d):
    x = math.radians(d - b) * math.cos(math.radians((a + c) / 2))
    return 6371000 * math.hypot(x, math.radians(c - a))
R, off = [], 0
while True:
    d = json.loads(subprocess.run(["curl", "-sf", "--max-time", "60", URL + str(off)], capture_output=True, check=True).stdout)
    R += d["results"]; off += 300
    if d["endOfRecords"]: break
trees = []
for r in sorted(R, key=lambda r: r["key"]):
    sp = (r.get("species") or "").replace("Rhaphiolepis bibas", "Eriobotrya japonica")  # loquat under the name the rest of the app uses
    genus, ds = sp.split(" ")[0], r["datasetKey"]
    acc, lat, lon = r.get("coordinateUncertaintyInMeters"), r["decimalLatitude"], r["decimalLongitude"]
    name = WOODY.get(genus) or (ds == INAT and HERBS.get(genus))
    if not name or not acc or acc > 30 or sp == "Pinus mugo" or dist(LAT, LON, lat, lon) > RADIUS_M: continue
    if any(t["taxon_species"] == sp and dist(t["lat"], t["lon"], lat, lon) <= 15 for t in trees): continue  # same plant seen again
    trees.append({"uniqueid": r["key"], "common_name": name, "taxon_species": sp, "gla_name": name, "age_cat": "Not recorded", "height_m": "Not recorded", "canopy_m": "Not recorded",
        "girth_dbh": "Not recorded", "climate_suitability": "Not recorded", "location": "%s · %s · ±%d m" % (r.get("year", "?"), SOURCE.get(ds, "GBIF"), acc), "maintainer": "Identification confirmée" if ds == INAT else "Identification automatique, à vérifier",
        "size": "", "lat": round(lat, 6), "lon": round(lon, 6), "dist": round(dist(LAT, LON, lat, lon))})
with open("trees_nice.js", "w", encoding="utf-8") as f:
    f.write(f"const CENTRE = [{LAT}, {LON}], RADIUS_M = {RADIUS_M}, HOME = {json.dumps(HOME, ensure_ascii=False)};\nconst TREES = {json.dumps(trees, separators=(',', ':'), ensure_ascii=False)};\n")
print(len(trees), "plants written to trees_nice.js")
