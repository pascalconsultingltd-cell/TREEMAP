# TREEMAP

Two cities, switched with the London / Barcelone toggle (or `?city=bcn`): London (NW5 2TE) and Barcelona (Carrer del Comte Borrell 84).

HTML/JavaScript map of street and park trees within a 1 km radius of NW5 2TE (London).

## Data
- Source: GLA Public Realm Trees — https://apps.london.gov.uk/public-realm-trees/explore?borough=E09000007 (Camden)
- 1 km radius may cross into Islington (E09000019) and Haringey (E09000014): check and include if so.
- Centre point: geocode NW5 2TE via https://api.postcodes.io/postcodes/NW52TE

- API: https://apps.london.gov.uk/api/tables/public-realm-trees-2026/trees (PostgREST; answers curl, returns 403 to Python urllib).
- Centre 51.548553, -0.130711. Haringey has no trees within 1 km.

## Files
- `fetch_trees.py`: downloads the 3 boroughs, keeps trees within 1 km, writes `trees.js`. Run: `C:/Users/sebas/Anaconda3/python.exe fetch_trees.py`
- `trees.js`: `CENTRE`, `RADIUS_M`, `TREES` (5510 trees, Oct 2026 fetch).
- `fetch_basemap.py`: one-off OSM fetch (Overpass mirror maps.mail.ru) of streets, rail, parks, water, buildings within 1.3 km into `basemap.js`.
- `index.html`: Leaflet drawing our own basemap from `basemap.js` (no tile servers: OSM blocks file://, CARTO needs a key); dots coloured by top 10 genera, sized by canopy, popup per tree. Opens by double-click.

- `photos/` + `photos.js`: Wikimedia Commons photos (500px) per legend group and season, picked by hand; credits in `photos.js`. Empty seasons reuse the nearest one. Close-ups (leaf, flower, fruit/samaras/cone, bark) where a good photo exists.

## Features
- Legend: species (EN / FR names), search, favourites, sorting, filters (edible, leaf, height, bees, sex, toxic), colour modes.
- Foraging walks (30 min / 1 h, selection, in season), saved walks, share links, guided walk mode.
- 🧭 nearest tree arrow (follows the compass), + for the next height up.
- Phones: bottom sheet, 📍 location that follows you, long press for one species.
- Offline: `sw.js` keeps both cities and all photos on the device. Interface in FR or EN.

## Barcelona
- `fetch_trees_bcn.py`: Open Data BCN street, zone and park trees (CC BY 4.0) within 1 km of Comte Borrell 84 into `trees_bcn.js` (no height, canopy or girth in this data).
- `basemap_bcn.js`: `python fetch_basemap.py 41.3800475 2.1594943 basemap_bcn.js`.
- After regenerating any data file, bump `V` in `index.html` so browsers reload it.
