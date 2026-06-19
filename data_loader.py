# data_loader.py
# Responsible for loading the GeoPackage file into memory once
# and caching it so every API request doesn't reload from disk.

import geopandas as gpd

# Global cache — loaded once when the Flask app starts
_roads_gdf = None

def load_roads(filepath: str) -> gpd.GeoDataFrame:
    """
    Loads the OS Open Roads GeoPackage file into a GeoDataFrame.
    Uses a module-level cache so the file is only read once.
    
    Args:
        filepath: Path to the .gpkg file
    
    Returns:
        GeoDataFrame with road features in WGS84 (EPSG:4326) CRS
    """
    global _roads_gdf

    if _roads_gdf is None:
        print(f"[data_loader] Loading roads data from: {filepath}")

        # Read the 'road_link' layer from the GeoPackage
        # OS Open Roads has two layers: 'road_link' and 'road_node'
        # road_link contains the actual road geometries (lines)
        _roads_gdf = gpd.read_file(filepath, layer="road_link")

        # OS data comes in British National Grid (EPSG:27700)
        # We convert to WGS84 (EPSG:4326) — standard lat/lng for REST APIs
        _roads_gdf = _roads_gdf.to_crs(epsg=4326)

        print(f"[data_loader] Loaded {len(_roads_gdf)} road features.")

    return _roads_gdf