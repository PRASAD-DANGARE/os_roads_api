# Ordnance Survey Open Roads — Flask Spatial API

A simple Flask REST API that returns road network data from the OS Open Roads dataset as GeoJSON, filtered by a bounding box.

---

## Dataset

**OS Open Roads** by Ordnance Survey
Download: https://osdatahub.os.uk/downloads/open/OpenRoads

| Field | Detail |
|---|---|
| Coverage | All of Great Britain |
| Data structure | Vector |
| Format | GeoPackage (`.gpkg`) |
| Version Date | April 2026 |
| Data provider | Ordnance Survey |

## Why This Dataset?

OS Open Roads is free, well-documented, and comes in GeoPackage format which geopandas reads directly without any preprocessing. The data covers the full GB road network and is a good fit for demonstrating a bbox-based spatial query over a real-world dataset. I chose GeoPackage over Shapefile because it's a single file and simpler to work with.

---

## Project Structure

```
os_roads_api/
├── app.py              # Flask app and API endpoint
├── data_loader.py      # Loads and caches the GeoPackage
├── test_app.py         # Unit tests
├── requirements.txt    # Dependencies
└── data/
    └── oproad_gb.gpkg  # Download separately (see Setup)
```

---

## Packages

| Package | Purpose |
|---|---|
| `flask` | REST API framework |
| `geopandas` | Read GeoPackage and spatial filtering |
| `shapely` | Bounding box geometry |
| `fiona` | Backend driver for reading `.gpkg` |

---

## Setup and Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-username/os_roads_api.git
cd os_roads_api
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
.\venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Download the dataset

Download **OS Open Roads** in **GeoPackage** format from:
```
https://osdatahub.os.uk/downloads/open/OpenRoads
```

Unzip the downloaded file, locate `oproad_gb.gpkg` inside the `Data/` folder, and place it at:
```
os_roads_api/data/oproad_gb.gpkg
```

> Note: The `.gpkg` file (2GB) is excluded from this repository via `.gitignore`. It must be downloaded separately from OS Data Hub.

### 5. Run the API

```bash
python app.py
```

The server starts at `http://127.0.0.1:5000`.

> On the first request, the GeoPackage file loads into memory (30–60 seconds). All subsequent requests are served from the in-memory cache.

---

## API Usage

### Health Check

```
GET /health
- http://127.0.0.1:5000/health
```

**Response:**
```json
{
  "status": "ok",
  "service": "OS Roads API"
}
```

---

### Get Roads by Bounding Box

```
GET /api/roads?bbox=minx,miny,maxx,maxy
```

**Example — Central London:**

```
GET /api/roads?bbox=-0.1276,51.5074,-0.1,51.52
- http://127.0.0.1:5000/api/roads?bbox=-0.1276,51.5074,-0.1,51.52
```

**Success Response (200):**
```json
{
  "bbox": [
    -0.1276,
    51.5074,
    -0.1,
    51.52
  ],
  "feature_count": 500,
  "features": [
    {
      "bbox": [
        -0.12505196647111821,
        51.51387483115679,
        -0.12425649524799666,
        51.5142937533588
      ],
      "geometry": {
        "coordinates": [
          [
            -0.12505196647111821,
            51.51387483115679
          ],
          [
            -0.1248836297445814,
            51.5139590977396
          ],
          [
            -0.12471514837024598,
            51.51404336177048
          ],
          [
            -0.12448589445114248,
            51.51416855894809
          ],
          [
            -0.12425649524799666,
            51.5142937533588
          ]
        ],
        "type": "LineString"
      },
      "id": "2577",
      "properties": {
        "end_node": "B834706F-F8B2-4456-A2BB-0F67216CADBC",
        "fictitious": false,
        "form_of_way": "Single Carriageway",
        "id": "002A2B0B-68E9-4193-B0E3-DF993EFD4837",
        "length": 72.0,
        "length_uom": "m",
        "loop": false,
        "name_1": "Shelton Street",
        "name_1_lang": null,
        "name_2": null,
        "name_2_lang": null,
        "primary_route": false,
        "road_classification": "Unclassified",
        "road_classification_number": null,
        "road_function": "Local Road",
        "road_name_toid": "osgb4000000030527669",
        "road_number_toid": null,
        "road_structure": null,
        "start_node": "3501410B-E96B-408B-8367-10B33D152F85",
        "trunk_road": false
      },
      "type": "Feature"
    }
}
```

**Error Response (400) — missing bbox:**
```json
{
  "error": "Missing required query parameter: bbox",
  "example": "/api/roads?bbox=-0.1276,51.5074,-0.1,51.52"
}
```

**Error Response (400) — malformed bbox:**
```json
{
  "error": "Invalid bbox format. Expected: minx,miny,maxx,maxy"
}
```

---

## Running Tests

```bash
python -m unittest test_app.py -v
```

**Expected output:**
```
test_bbox_outside_gb_returns_empty (test_app.TestRoadsAPI.test_bbox_outside_gb_returns_empty)
bbox far outside GB should return 0 features (empty collection). ... ok
test_health_check (test_app.TestRoadsAPI.test_health_check)
Health endpoint should always return 200. ... ok
test_malformed_bbox_returns_400 (test_app.TestRoadsAPI.test_malformed_bbox_returns_400)
Malformed bbox (not 4 numbers) should return 400. ... ok
test_missing_bbox_returns_400 (test_app.TestRoadsAPI.test_missing_bbox_returns_400)
Request without bbox param should return 400. ... ok
test_valid_bbox_returns_geojson (test_app.TestRoadsAPI.test_valid_bbox_returns_geojson)
A valid bbox should return 200 with a GeoJSON FeatureCollection. ... ok

----------------------------------------------------------------------
Ran 5 tests in 0.127s

OK
```
