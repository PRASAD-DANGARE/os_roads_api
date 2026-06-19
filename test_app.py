# test_app.py
# Unit tests for the OS Roads API endpoint.
# Uses Flask's built-in test client + unittest.mock to avoid
# loading the real GeoPackage file during tests.

import json
import unittest
from unittest.mock import patch, MagicMock
import geopandas as gpd
from shapely.geometry import LineString

from app import app


def make_mock_gdf():
    """
    Creates a tiny fake GeoDataFrame with 2 road features.
    Used to mock the real GeoPackage load during tests.
    """
    return gpd.GeoDataFrame(
        {
            "roadFunction": ["A Road", "B Road"],
            "name1":        ["High Street", "London Road"],
            "geometry": [
                LineString([(-0.12, 51.50), (-0.11, 51.51)]),
                LineString([(-0.11, 51.51), (-0.10, 51.52)]),
            ],
        },
        crs="EPSG:4326"
    )


class TestRoadsAPI(unittest.TestCase):

    def setUp(self):
        """Configure Flask test client before each test."""
        app.config["TESTING"] = True
        self.client = app.test_client()

    # --- Patch load_roads so we never touch the real .gpkg file ---
    @patch("app.load_roads", return_value=make_mock_gdf())
    def test_valid_bbox_returns_geojson(self, mock_load):
        """A valid bbox should return 200 with a GeoJSON FeatureCollection."""
        response = self.client.get("/api/roads?bbox=-0.13,51.49,-0.09,51.53")
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertEqual(data["type"], "FeatureCollection")
        self.assertIn("features", data)
        self.assertIsInstance(data["features"], list)

    @patch("app.load_roads", return_value=make_mock_gdf())
    def test_missing_bbox_returns_400(self, mock_load):
        """Request without bbox param should return 400."""
        response = self.client.get("/api/roads")
        self.assertEqual(response.status_code, 400)

        data = json.loads(response.data)
        self.assertIn("error", data)

    @patch("app.load_roads", return_value=make_mock_gdf())
    def test_malformed_bbox_returns_400(self, mock_load):
        """Malformed bbox (not 4 numbers) should return 400."""
        response = self.client.get("/api/roads?bbox=abc,def")
        self.assertEqual(response.status_code, 400)

    @patch("app.load_roads", return_value=make_mock_gdf())
    def test_bbox_outside_gb_returns_empty(self, mock_load):
        """bbox far outside GB should return 0 features (empty collection)."""
        response = self.client.get("/api/roads?bbox=70.0,40.0,71.0,41.0")
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertEqual(len(data["features"]), 0)

    def test_health_check(self):
        """Health endpoint should always return 200."""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()