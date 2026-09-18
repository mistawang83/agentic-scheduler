import json
import requests
import os
from agents import function_tool


DOWNLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../storage/downloads/")
BASE = "https://mycourses2.mcgill.ca"


os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def load_cookies_from_storage_state(path="storage/d2l_auth.json") -> dict:
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

class SessionExpiredError(Exception):
    pass

def d2l_get(url: str, **kwargs) -> requests.Response:
    resp = get_session().get(url, **kwargs)
    if resp.status_code == 401:
        raise SessionExpiredError(
            "Brightspace session expired. Run your login script manually "
            "to refresh storage/d2l_auth.json, then retry the request."
        )
    resp.raise_for_status()
    return resp

# Simple in-process caches so the agent isn't re-hitting these every call.
_versions_cache: dict | None = None
_courses_cache: list[dict] | None = None


@function_tool
def get_api_versions() -> dict:
    """Return the supported/latest API versions for each Brightspace product. 
    Call this once and reuse the LatestVersion values."""
    global _versions_cache
    if _versions_cache is None:
        resp = d2l_get(f"{BASE}/d2l/api/versions/")
        _versions_cache = resp.json()
    return _versions_cache


@function_tool
def get_courses() -> list[dict]:
    """List all courses the logged-in user is enrolled in, with their
    orgUnitId, name, and course code. Use this to resolve a course name
    mentioned by the user into an orgUnitId - never guess the ID."""
    global _courses_cache
    if _courses_cache is not None:
        return _courses_cache

    lp_version = _get_latest_version("lp")
    resp = d2l_get(f"{BASE}/d2l/api/lp/{lp_version}/enrollments/myenrollments/")
    data = resp.json()
    _courses_cache = [
        {
            "orgUnitId": item["OrgUnit"]["Id"],
            "name": item["OrgUnit"]["Name"],
            "code": item["OrgUnit"]["Code"],
        }
        for item in data.get("Items", [])
    ]
    return _courses_cache

@function_tool
def get_course_content_tree(org_unit_id: str) -> list[dict]:
    """Fetch the full content tree for a course and return it as a flat list
    of topics, each with id, title, type (e.g. 'File', 'Link'), and url.
    Use the orgUnitId from get_courses."""
    le_version = _get_latest_version("le")
    resp = d2l_get(f"{BASE}/d2l/api/le/{le_version}/{org_unit_id}/content/toc")
    return _flatten_topics(resp.json())


@function_tool
def download_topic_file(org_unit_id: str, topic_id: str, filename: str) -> str:
    """Download the file attached to a specific content topic. Provide just
    the filename - it is saved under DOWNLOAD_DIR automatically."""
    le_version = _get_latest_version("le")
    resp = d2l_get(
        f"{BASE}/d2l/api/le/{le_version}/{org_unit_id}/content/topics/{topic_id}/file",
        params={"stream": "false"},
    )
    out_path = os.path.join(DOWNLOAD_DIR, filename)
    with open(out_path, "wb") as f:
        f.write(resp.content)
    return out_path


# --- Helper methods ---

def _get_latest_version(product_code: str) -> str:
    versions = _raw_versions()
    for entry in versions:
        if entry.get("ProductCode") == product_code:
            return entry["LatestVersion"]
    raise ValueError(f"No API version found for product '{product_code}'")


def _raw_versions() -> list[dict]:
    global _versions_cache
    if _versions_cache is None:
        resp = d2l_get(f"{BASE}/d2l/api/versions/")
        _versions_cache = resp.json()
    return _versions_cache


def _flatten_topics(tree: dict) -> list[dict]:
    topics = []

    def walk(node):
        for t in node.get("Topics", []):
            try:
                topics.append({
                    "id": t["TopicId"],
                    "title": t["Title"],
                    "type": t.get("TypeIdentifier"),
                    "url": t.get("Url"),
                })
            except KeyError as e:
                raise KeyError(
                    f"Topic entry missing expected field {e}. "
                    f"Actual keys: {list(t.keys())}"
                ) from e
        for m in node.get("Modules", []):
            walk(m)

    walk(tree)
    return topics