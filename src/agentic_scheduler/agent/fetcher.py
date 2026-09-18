from agents import Agent

from agentic_scheduler.agent.prompts import get_fetcher_instructions
from agentic_scheduler.brightspace.tools import (
    download_topic_file,
    get_api_versions,
    get_course_content_tree,
    get_courses,
)
from agentic_scheduler.config import MODEL


def fetcher_agent() -> Agent:
    return Agent(
        name="University Course Page Info Fetcher",
        instructions=get_fetcher_instructions(),
        model=MODEL,
        tools=[get_api_versions, get_courses, get_course_content_tree, download_topic_file],
    )
