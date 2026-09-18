import json

import requests

from agentic_scheduler.config import AUTH_STATE_FILE, BRIGHTSPACE_BASE_URL


class SessionExpiredError(Exception):
    pass


def load_cookies_from_storage_state(path=AUTH_STATE_FILE) -> dict:
    with open(path) as f:
        state = json.load(f)
    return {c["name"]: c["value"] for c in state["cookies"]}


_session: requests.Session | None = None


def get_session(force_reload: bool = False) -> requests.Session:
    global _session
    if _session is None or force_reload:
        _session = requests.Session()
        _session.cookies.update(load_cookies_from_storage_state())
    return _session


def d2l_get(path: str, **kwargs) -> requests.Response:
    """GET a Brightspace API path (e.g. '/d2l/api/versions/')."""
    resp = get_session().get(f"{BRIGHTSPACE_BASE_URL}{path}", **kwargs)
    if resp.status_code == 401:
        raise SessionExpiredError(
            "Brightspace session expired. Run `uv run scripts/login.py` "
            f"to refresh {AUTH_STATE_FILE.name}, then retry the request."
        )
    resp.raise_for_status()
    return resp


# Simple in-process cache so the agent isn't re-hitting this every call.
_versions_cache: list[dict] | None = None


def get_versions() -> list[dict]:
    global _versions_cache
    if _versions_cache is None:
        _versions_cache = d2l_get("/d2l/api/versions/").json()
    return _versions_cache


def get_latest_version(product_code: str) -> str:
    for entry in get_versions():
        if entry.get("ProductCode") == product_code:
            return entry["LatestVersion"]
    raise ValueError(f"No API version found for product '{product_code}'")
