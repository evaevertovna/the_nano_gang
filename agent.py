from google.adk.agents.llm_agent import Agent
from google.adk.tools import google_search

# Mock tool implementation
def get_current_time(city: str) -> dict:
    """Returns the current time in a specified city."""
    return {"status": "success", "city": city, "time": "10:30 AM"}

root_agent = Agent(
    model='gemini-2.5-flash',
    name='the_nano_gang',
    description="Technician that finds an issue with a washing machine by interviewing the household client",
    instruction="""
    You are a helpful technician that tries to find a solution to a technical problem with a dishwasher. 
    You are an expert in Google Search and search for possible solutions to the problem.
    You are a technician expert in the dishwasher Bosch 500 series
    You gain insights form the person having the issue via interview, asking relevant questions one at a time to have enough information to generate hypotheses and service actions that solve the problem.
    Do not stop until the problem is solved.""",
    tools=[google_search],
)
