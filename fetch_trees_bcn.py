# Fetch Barcelona trees (street, zone, park) within RADIUS_M of Carrer del Comte Borrell 84 into trees_bcn.js, same shape as trees.js.
import csv, io, json, math, re, subprocess
LAT, LON, RADIUS_M, HOME = 41.3800475, 2.1594943, 1000, "Comte Borrell 84"
SETS = ["Viari", "Zona", "Parcs"]  # Open Data BCN, CC BY 4.0
URL = "https://opendata-ajuntament.barcelona.cat/resources/bcn/Arbrat/OD_Arbrat_%s_BCN.csv"
# Legend group (English, like the GLA names) by genus; anything else is "Other"
GROUP = {"Platanus": "Plane", "Celtis": "Nettle Tree", "Pinus": "Pine", "Citrus": "Orange", "Tipuana": "Tipu tree", "Jacaranda": "Jacaranda", "Melia": "Chinaberry",
  "Robinia": "Black locust", "Styphnolobium": "Pagoda tree", "Sophora": "Pagoda tree", "Ulmus": "Elm", "Tilia": "Lime", "Populus": "Poplar", "Acer": "Maple",
  "Fraxinus": "Ash", "Ligustrum": "Privet", "Phoenix": "Palm", "Washingtonia": "Palm", "Chamaerops": "Palm", "Trachycarpus": "Palm", "Livistona": "Palm",
  "Butia": "Palm", "Syagrus": "Palm", "Morus": "Mulberry", "Ceratonia": "Carob", "Olea": "Olive", "Ficus": "Fig", "Eriobotrya": "Loquat", "Prunus": "Cherry",
  "Brachychiton": "Bottle tree", "Schinus": "Pepper tree", "Lagunaria": "Norfolk hibiscus", "Casuarina": "She-oak", "Cupressus": "Cypress", "Quercus": "Oak",
  "Magnolia": "Magnolia", "Gleditsia": "Honey Locust", "Koelreuteria": "Pride-of-India", "Liquidambar": "Sweetgum", "Ginkgo": "Ginkgo", "Bauhinia": "Orchid tree",
  "Erythrina": "Coral tree", "Cercis": "Judas tree", "Punica": "Pomegranate", "Diospyros": "Persimmon", "Ziziphus": "Jujube", "Laurus": "Bay",
  "Arbutus": "Strawberry-tree", "Pyrus": "Pear", "Malus": "Apple", "Juglans": "Walnut", "Castanea": "Chestnut", "Corylus": "Hazel", "Sambucus": "Elder",
  "Crataegus": "Hawthorn", "Taxus": "Yew", "Fagus": "Beech", "Aesculus": "Horse Chestnut", "Betula": "Birch", "Salix": "Willow", "Lagerstroemia": "Crape myrtle",
  "Eucalyptus": "Eucalyptus", "Albizia": "Silk tree", "Cinnamomum": "Camphor tree", "Ceiba": "Silk floss tree", "Pittosporum": "Pittosporum", "Photinia": "Photinia"}
def dist(lat, lon):
    x = math.radians(lon - LON) * math.cos(math.radians((lat + LAT) / 2))
    return 6371000 * math.hypot(x, math.radians(lat - LAT))
trees, ids = [], set()
for k, name in enumerate(SETS):
    raw = subprocess.run(["curl", "-sfL", URL % name], capture_output=True, check=True).stdout.decode("utf-8-sig")
    for r in csv.DictReader(io.StringIO(raw)):
        try: lat, lon = float(r["latitud"]), float(r["longitud"])
        except ValueError: continue
        d = dist(lat, lon)
        if d > RADIUS_M: continue
        sp = r["cat_nom_cientific"].strip() or "Unknown"
        es = r["cat_nom_castella"].strip(" -") or r["cat_nom_catala"].split(";")[0].strip(" -") or sp
        uid = 20000000 + int(re.sub(r"\D", "", r["codi"]) or 0) * 3 + k  # numeric and stable across refreshes: code digits + dataset
        if uid in ids: continue
        ids.add(uid)
        planted = r["data_plantacio"][:4]
        trees.append({"uniqueid": uid, "common_name": es, "taxon_species": sp, "gla_name": GROUP.get(sp.split(" ")[0], "Other"),
            "age_cat": "Planted " + planted if planted else "Not provided", "height_m": "Not recorded", "canopy_m": "Not recorded", "girth_dbh": "Not recorded",
            "climate_suitability": "Not recorded", "location": (r["espai_verd"] or r["adreca"]).strip(), "maintainer": "Ajuntament de Barcelona",
            "size": r["categoria_arbrat"].strip().capitalize(), "lat": round(lat, 6), "lon": round(lon, 6), "dist": round(d)})
    print(name, "done,", len(trees), "trees so far", flush=True)
with open("trees_bcn.js", "w", encoding="utf-8") as f:
    f.write(f"const CENTRE = [{LAT}, {LON}], RADIUS_M = {RADIUS_M}, HOME = {json.dumps(HOME)};\nconst TREES = {json.dumps(trees, separators=(',', ':'), ensure_ascii=False)};\n")
print(len(trees), "trees written to trees_bcn.js")
