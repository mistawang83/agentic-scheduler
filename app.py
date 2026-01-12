from dotenv import load_dotenv
from agents import Agent, Runner, trace
from agents.mcp import MCPServerStdio
from agent.scheduler import scheduler_agent
from agent.memory import save_message, load_conversation
import os
import gradio as gr

load_dotenv(override=True)

openai_api_key = os.getenv("OPENAI_API_KEY")
google_client_id = os.getenv("GOOGLE_CLIENT_ID")
google_client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
google_refresh_token = os.getenv("GOOGLE_REFRESH_TOKEN")

mcp_params = {
    "command": "node",
    "args": ["/Users/Simon Wang/projects/google-workspace-mcp-server/build/index.js"],
    "env": {
        "GOOGLE_CLIENT_ID": google_client_id,
        "GOOGLE_CLIENT_SECRET": google_client_secret,
        "GOOGLE_REFRESH_TOKEN": google_refresh_token,
    }
}

class App:
    def __init__(self):
        self.agent = scheduler_agent()

    async def chat(self, message, history):
        conversation = load_conversation()
        request = f"""
            # This is the history of the conversation between you and the user.
            History: \n{conversation}
            \n\n
        """

        request += "## This is the new user message: \n" + message
        async with MCPServerStdio(params=mcp_params, client_session_timeout_seconds=30) as mcp_server:
            self.agent.mcp_servers = [mcp_server]
            with trace("scheduler"):
                result =  await Runner.run(self.agent, request)

            save_message("user", message)
            save_message("agent", result.final_output)
            return result.final_output
        
if __name__ == "__main__":
    app = App()
    gr.ChatInterface(app.chat).launch()