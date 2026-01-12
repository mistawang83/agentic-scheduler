from dotenv import load_dotenv
from agents import Agent, Runner, trace
import os
from agent.prompts import get_manager_instructions
from agent.scheduler import scheduler_agent


load_dotenv(override=True)

openai_api_key = os.getenv("OPENAI_API_KEY")

def manager_agent() -> Agent:

    instructions = get_manager_instructions()

    return Agent(
        name="Google Calendar Manager",
        instructions=instructions,
        model="gpt-5-nano",
    )
