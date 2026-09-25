import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://api.stlouisfed.org/fred"
API_KEY = os.getenv("FRED_API_KEY")



def _get(endpoint: str, **params) -> dict:
    """Make a GET request to FRED API with one retry."""
    params["api_key"] = API_KEY
    params["file_type"] = "json"

    for attempt in range(2):
        try:
            resp = requests.get(f"{BASE_URL}/{endpoint}", params=params, timeout=30)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as e:
            if attempt == 1:
                raise
            print(f"  [retry] {e}")
            time.sleep(2)


def search_series(query: str, limit: int = 10) -> list[dict]:
    """Search FRED for series matching a keyword."""
    data = _get("series/search", search_text=query, limit=limit, order_by="popularity", sort_order="desc")
    return [
        {"id": s["id"], "title": s["title"], "frequency": s["frequency"]}
        for s in data.get("seriess", [])
    ]


def get_observations(series_id: str, start: str = "2000-01-01", end: str = None) -> list[dict]:
    """Fetch observations for a series."""
    params = {"series_id": series_id, "observation_start": start}
    if end:
        params["observation_end"] = end
    data = _get("series/observations", **params)
    return [
        {"date": o["date"], "value": o["value"]}
        for o in data.get("observations", [])
        if o["value"] != "."
    ]


if __name__ == "__main__":
    # Quick test
    print("Search:", search_series("unemployment rate")[:3])
    print("Observations:", get_observations("UNRATE", start="2024-01-01")[:3])