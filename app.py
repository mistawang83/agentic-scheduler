from dotenv import load_dotenv
from agents import Agent, Runner, trace
from agents.mcp import MCPServerStdio
from agent.manager import manager_agent
from agent.scheduler import scheduler_agent
from agent.fetcher import fetcher_agent
from scripts.memory import save_message, load_conversation
import os
import asyncio
import gradio as gr
import shutil
from pathlib import Path

load_dotenv(override=True)

openai_api_key = os.getenv("OPENAI_API_KEY")
google_client_id = os.getenv("GOOGLE_CLIENT_ID")
google_client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
google_refresh_token = os.getenv("GOOGLE_REFRESH_TOKEN")

google_mcp_params = {
    "command": "node",
    "args": ["../google-workspace-mcp-server/build/index.js"],
    "env": {
        "GOOGLE_CLIENT_ID": google_client_id,
        "GOOGLE_CLIENT_SECRET": google_client_secret,
        "GOOGLE_REFRESH_TOKEN": google_refresh_token,
    }
}

playwright_mcp_params = {
    "command": "npx",
    "args": [
        "@playwright/mcp@latest",
        "--isolated",
        "--storage-state=storage/playwright_auth.json",
        "--viewport-size=1280x720",
        "--output-dir=storage/playwright/"
    ],
}

class App:
    def __init__(self):
        self.manager = manager_agent()
        self.scheduler = scheduler_agent()
        self.fetcher = fetcher_agent()
        self.google_mcp_server = None
        self.playwright_mcp_server = None
        self.servers_started = False

    def clear_playwright_logs(self, output_dir: str = "storage/playwright/", keep_exts: set[str] = None):
        """
        Delete leftover log/session/trace files from the previous run,
        while optionally preserving real downloaded files (e.g. PDFs).
        """
        output_path = Path(output_dir)
        if not output_path.exists():
            return

        # Extensions to delete before each run
        junk_exts = {".yml", ".yaml", ".log", ".zip", ".json"}
        if keep_exts:
            junk_exts -= keep_exts

        for item in output_path.iterdir():
            if item.is_file() and item.suffix.lower() in junk_exts:
                item.unlink()
            elif item.is_dir() and item.name.startswith((".playwright-mcp", "trace-", "session")):
                shutil.rmtree(item, ignore_errors=True)

    async def start_servers(self):
        """
        Start both MCP servers and keep them running
        """
        if self.servers_started:
            return
        
        # Start Google MCP server
        self.google_mcp_server = MCPServerStdio(
            params=google_mcp_params, 
            client_session_timeout_seconds=30
        )
        await self.google_mcp_server.__aenter__()

        # Wipe previous session files and logs
        self.clear_playwright_logs()

        # Start Playwright MCP server
        self.playwright_mcp_server = MCPServerStdio(
            params=playwright_mcp_params,
            client_session_timeout_seconds=30
        )
        await self.playwright_mcp_server.__aenter__()
        
        # Set MCP servers on scheduler
        self.scheduler.mcp_servers = [self.google_mcp_server]
        self.fetcher.mcp_servers = [self.playwright_mcp_server]
        scheduler_tool = self.scheduler.as_tool(tool_name="scheduler_agent", tool_description="Create, modify and delete events from the user's Google Calendar")
        fetcher_tool = self.fetcher.as_tool(tool_name="fetcher_agent", tool_description="Fetch information about the user's university course deliverables and events", max_turns=30)
        self.manager.tools = [scheduler_tool, fetcher_tool]
        self.servers_started = True

    async def stop_servers(self):
        """Stop both MCP servers safely"""
        if not self.servers_started:
            return

        if self.playwright_mcp_server is not None:
            await self.playwright_mcp_server.__aexit__(None, None, None)
            self.playwright_mcp_server = None

        if self.google_mcp_server is not None:
            await self.google_mcp_server.__aexit__(None, None, None)
            self.google_mcp_server = None

        self.servers_started = False
        
    async def chat(self, message, history):
        # Ensure servers are started
        if not self.servers_started:
            await self.start_servers()
        
        conversation = load_conversation()
        request = f"""
            # This is the history of the conversation between you and the user.
            History: \n{conversation}
            \n\n
        """

        request += "## This is the new user message: \n" + message
        
        with trace("scheduler"):
            result = await Runner.run(self.manager, request, max_turns=30)

        save_message("user", message)
        save_message("agent", result.final_output)
        return result.final_output
        
if __name__ == "__main__":
    app = App()
    # Start servers before launching Gradio
    gr.ChatInterface(app.chat).launch()