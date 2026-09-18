from agents import function_tool

from agentic_scheduler.brightspace.client import d2l_get, get_latest_version, get_versions
from agentic_scheduler.config import DOWNLOAD_DIR

# Simple in-process cache so the agent isn't re-hitting this every call.
_courses_cache: list[dict] | None = None


@function_tool
def get_api_versions() -> list[dict]:
    """Return the supported/latest API versions for each Brightspace product.
    Call this once and reuse the LatestVersion values."""
    return get_versions()


@function_tool
def get_courses() -> list[dict]:
    """List all courses the logged-in user is enrolled in, with their
    orgUnitId, name, and course code. Use this to resolve a course name
    mentioned by the user into an orgUnitId - never guess the ID."""
    global _courses_cache
    if _courses_cache is not None:
        return _courses_cache

    lp_version = get_latest_version("lp")
    data = d2l_get(f"/d2l/api/lp/{lp_version}/enrollments/myenrollments/").json()
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
    le_version = get_latest_version("le")
    resp = d2l_get(f"/d2l/api/le/{le_version}/{org_unit_id}/content/toc")
    return _flatten_topics(resp.json())


@function_tool
def download_topic_file(org_unit_id: str, topic_id: str, filename: str) -> str:
    """Download the file attached to a specific content topic. Provide just
    the filename - it is saved under the downloads directory automatically."""
    le_version = get_latest_version("le")
    resp = d2l_get(
        f"/d2l/api/le/{le_version}/{org_unit_id}/content/topics/{topic_id}/file",
        params={"stream": "false"},
    )
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    out_path = DOWNLOAD_DIR / filename
    out_path.write_bytes(resp.content)
    return str(out_path)


# --- Helper methods ---

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
