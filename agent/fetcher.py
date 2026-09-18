from dotenv import load_dotenv
from agents import Agent, Runner, trace
import os
from agent.prompts import get_fetcher_instructions
from agent.tools.fetcher_tools import get_api_versions, get_courses, get_course_content_tree, download_topic_file

load_dotenv(override=True)

openai_api_key = os.getenv("OPENAI_API_KEY")

def fetcher_agent() -> Agent :

    instructions = get_fetcher_instructions()
    
    return Agent(
        name="University Course Page Info Fetcher",
        instructions=instructions,
        model="gpt-5-nano",
        tools=[get_api_versions, get_courses, get_course_content_tree, download_topic_file]
    )