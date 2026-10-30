# Recipe names per plant from Urbanivore's index (https://urbanivore.fr/recettes), read as text, into recipes.js. Names only, no links, photos or recipe text.
import json, re, subprocess
# Urbanivore's plant name to our genus, or species where the rest of the genus differs
KEYS = {"Abricotier": "Prunus armeniaca", "Alisier blanc, Alouchier": "Sorbus aria", "Amandier": "Prunus dulcis", "Amélanchier": "Amelanchier", "Arbousier": "Arbutus", "Arbre de Judée": "Cercis", "Argousier": "Hippophae",
  "Aronie": "Aronia", "Aubépine": "Crataegus", "Cerisier à fruits": "Prunus avium,Prunus cerasus", "Châtaignier": "Castanea", "Chêne": "Quercus", "Chèvrefeuille": "Lonicera", "Cognassier": "Cydonia", "Cornouiller": "Cornus mas",
  "Figuier": "Ficus carica", "Frêne": "Fraxinus", "Glycine": "Wisteria", "Hêtre": "Fagus", "Magnolia": "Magnolia", "Mûrier blanc": "Morus", "Noisetier": "Corylus", "Osmanthe": "Osmanthus", "Poirier": "Pyrus",
  "Pin sylvestre": "Pinus sylvestris", "Cormier": "Sorbus domestica", "Lilas": "Syringa", "Prunier": "Prunus domestica,Prunus cerasifera", "Robinier, Faux acacia": "Robinia", "Sumac de Virginie": "Rhus typhina", "Sureau": "Sambucus nigra", "Tilleul": "Tilia"}
SKIP = {"Vin de feuille de cerisier"}  # Prunus leaves hold toxic compounds
raw = subprocess.run(["curl", "-sfL", "--max-time", "60", "https://urbanivore.fr/js/recettes.js"], capture_output=True, check=True).stdout.decode("utf-8")
out, keys = {}, []
for m in re.finditer(r'''^\s*"([^"\n]+)"\s*:\s*\[|\btitre\s*:\s*"((?:[^"\\]|\\.)*)"''', raw, re.M):
    if m.group(1): keys = KEYS.get(m.group(1), "").split(",")
    elif m.group(2) and m.group(2) not in SKIP:
        for k in keys:
            if k: out.setdefault(k, []).append(m.group(2).strip())
with open("recipes.js", "w", encoding="utf-8") as f: f.write(f"// Recipe names per genus or species, from urbanivore.fr\nconst RECIPES = {json.dumps(out, ensure_ascii=False, separators=(',', ':'))};\n")
print(len(out), "plants,", sum(map(len, out.values())), "names")
