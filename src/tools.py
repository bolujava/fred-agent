from .fred_client import search_series, get_observations


def tool_search_series(query: str) -> str:
    """Find FRED series IDs matching a keyword. Use this FIRST to find the right series."""
    results = search_series(query, limit=5)
    if not results:
        return "No series found."
    return "\n".join(f"{r['id']}: {r['title']} ({r['frequency']})" for r in results)


def tool_get_observations(series_id: str, start: str = "2020-01-01", end: str = None) -> str:
    """Fetch data for a FRED series. Returns date: value pairs."""
    obs = get_observations(series_id, start, end)
    if not obs:
        return "No data found."
    return "\n".join(f"{o['date']}: {o['value']}" for o in obs)


def tool_transform_series(series_id: str, transform: str = "percent_change") -> str:
    """Apply a transformation: 'percent_change', 'yoy', or 'raw'."""
    obs = get_observations(series_id)
    if not obs:
        return "No data."

    values = [float(o["value"]) for o in obs if o["value"] != "."]
    dates = [o["date"] for o in obs if o["value"] != "."]

    if transform == "percent_change" and len(values) > 1:
        result = ((values[-1] - values[-2]) / values[-2]) * 100
        return f"Latest percent change: {result:.2f}%"
    elif transform == "yoy" and len(values) > 12:
        result = ((values[-1] - values[-13]) / values[-13]) * 100
        return f"Year-over-year change: {result:.2f}%"
    else:
        return f"Latest value: {values[-1]}"


TOOL_MAP = {
    "search_series": tool_search_series,
    "get_observations": tool_get_observations,
    "transform_series": tool_transform_series,
}