# app.py
# Flask REST API exposing a single endpoint to query OS Open Roads data
# by a bounding box (bbox) and return matching features as GeoJSON.

import os
from flask import Flask, jsonify, request
from shapely.geometry import box
from data_loader import load_roads

app = Flask(__name__)

# Path to the downloaded OS Open Roads GeoPackage file
DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "oproad_gb.gpkg")


@app.route("/api/roads", methods=["GET"])
def get_roads():
    """
    GET /api/roads?bbox=minx,miny,maxx,maxy

    Returns road features within the given bounding box as GeoJSON.

    Query Parameters:
        bbox (str): Comma-separated bounding box in WGS84 (lng/lat order):
                    minx,miny,maxx,maxy
                    Example: -0.1276,51.5074,-0.1,51.52  (central London)

    Returns:
        200: GeoJSON FeatureCollection of matching road links
        400: If bbox param is missing or malformed
        500: If data cannot be loaded
    """

    # --- 1. Parse and validate the bbox query parameter ---
    bbox_param = request.args.get("bbox")

    if not bbox_param:
        return jsonify({
            "error": "Missing required query parameter: bbox",
            "example": "/api/roads?bbox=-0.1276,51.5074,-0.1,51.52"
        }), 400

    try:
        # Split "minx,miny,maxx,maxy" into four floats
        minx, miny, maxx, maxy = map(float, bbox_param.split(","))
    except ValueError:
        return jsonify({
            "error": "Invalid bbox format. Expected: minx,miny,maxx,maxy",
            "example": "/api/roads?bbox=-0.1276,51.5074,-0.1,51.52"
        }), 400

    # Basic sanity check on coordinate ranges
    if not (-180 <= minx < maxx <= 180) or not (-90 <= miny < maxy <= 90):
        return jsonify({
            "error": "bbox coordinates out of valid WGS84 range"
        }), 400

    # --- 2. Load roads data (cached after first load) ---
    try:
        roads_gdf = load_roads(DATA_PATH)
    except Exception as e:
        return jsonify({"error": f"Failed to load spatial data: {str(e)}"}), 500

    # --- 3. Spatial filter — keep only roads within the bbox ---
    # Create a shapely box geometry from the bbox coordinates
    bbox_geom = box(minx, miny, maxx, maxy)

    # cx[] is geopandas spatial index — much faster than row-by-row check
    filtered_gdf = roads_gdf.cx[minx:maxx, miny:maxy]

    if filtered_gdf.empty:
        return jsonify({
            "type": "FeatureCollection",
            "features": [],
            "message": "No roads found in the given bounding box"
        }), 200

    # --- 4. Return as GeoJSON ---
    # Limit to 500 features max to avoid huge responses
    filtered_gdf = filtered_gdf.head(500)

    return jsonify({
        "type": "FeatureCollection",
        "feature_count": len(filtered_gdf),
        "bbox": [minx, miny, maxx, maxy],
        "features": filtered_gdf.__geo_interface__["features"]
    }), 200


@app.route("/health", methods=["GET"])
def health_check():
    """
    GET /health
    Simple health check endpoint to confirm the API is running.
    """
    return jsonify({"status": "ok", "service": "OS Roads API"}), 200


if __name__ == "__main__":
    app.run(debug=True, port=5000)