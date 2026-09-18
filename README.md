App to fetch university course info and add into google calendar

## Setup

1. Copy `.env.example` to `.env` and fill in the values.
2. Build the Google Workspace MCP server. It is expected at
   `../google-workspace-mcp-server/build/index.js`, or set `GOOGLE_MCP_SERVER_PATH`.
3. Install dependencies: `uv sync`
4. Log in to Brightspace once (saves `data/d2l_auth.json`): `uv run scripts/login.py`

## Run

    uv run agentic-scheduler

Check the saved Brightspace session: `uv run scripts/check_login.py`

## Layout

    src/agentic_scheduler/
        app.py            Gradio UI and App entry point
        config.py         env vars, paths, MCP params
        memory.py         sqlite conversation history
        agent/            manager, scheduler, fetcher agents and prompts
        brightspace/      Brightspace API client and agent tools
    scripts/              manual utilities (login)
    data/                 local runtime data (gitignored)
