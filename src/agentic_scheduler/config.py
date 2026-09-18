import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]

load_dotenv(PROJECT_ROOT / ".env", override=True)

# Local runtime data (gitignored)
DATA_DIR = PROJECT_ROOT / "data"
MEMORY_DB = DATA_DIR / "memory.db"
AUTH_STATE_FILE = DATA_DIR / "d2l_auth.json"
DOWNLOAD_DIR = DATA_DIR / "downloads"

# Brightspace
BRIGHTSPACE_BASE_URL = "https://mycourses2.mcgill.ca"

# Models
MODEL = "gpt-5-nano"

# Google Workspace MCP server (expected as a sibling checkout by default)
GOOGLE_MCP_SERVER_PATH = Path(
    os.getenv(
        "GOOGLE_MCP_SERVER_PATH",
        PROJECT_ROOT.parent / "google-workspace-mcp-server" / "build" / "index.js",
    )
)


def google_mcp_params() -> dict:
    return {
        "command": "node",
        "args": [str(GOOGLE_MCP_SERVER_PATH)],
        "env": {
            "GOOGLE_CLIENT_ID": os.getenv("GOOGLE_CLIENT_ID"),
            "GOOGLE_CLIENT_SECRET": os.getenv("GOOGLE_CLIENT_SECRET"),
            "GOOGLE_REFRESH_TOKEN": os.getenv("GOOGLE_REFRESH_TOKEN"),
        },
    }
