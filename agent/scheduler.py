from dotenv import load_dotenv
from agents import Agent, Runner, trace
import os
from agent.prompts import get_scheduler_instructions


load_dotenv(override=True)

openai_api_key = os.getenv("OPENAI_API_KEY")
google_client_id = os.getenv("GOOGLE_CLIENT_ID")
google_client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
google_refresh_token = os.getenv("GOOGLE_REFRESH_TOKEN")

def scheduler_agent() -> Agent:

    instructions = get_scheduler_instructions()

    return Agent(
        name="Google Calendar Scheduler",
        instructions=instructions,
        model="gpt-5-nano",
    )