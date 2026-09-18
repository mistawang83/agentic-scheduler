from agents import Agent

from agentic_scheduler.agent.prompts import get_manager_instructions
from agentic_scheduler.config import MODEL


def manager_agent() -> Agent:
    return Agent(
        name="Google Calendar Manager",
        instructions=get_manager_instructions(),
        model=MODEL,
    )
