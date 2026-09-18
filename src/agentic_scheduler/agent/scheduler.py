from agents import Agent

from agentic_scheduler.agent.prompts import get_scheduler_instructions
from agentic_scheduler.config import MODEL


def scheduler_agent() -> Agent:
    return Agent(
        name="Google Calendar Scheduler",
        instructions=get_scheduler_instructions(),
        model=MODEL,
    )
