#!/usr/bin/env python3

from config import EGO_MODEL, OLLAMA_BASE_URL, EGO_TEMPERATURE
from crewai import Agent, LLM, Task, Crew

llm = LLM(
    model=EGO_MODEL,
    base_url=OLLAMA_BASE_URL,
    temperature=EGO_TEMPERATURE,
)

ego_agent = Agent(
    role="Ego - Rational Mediator",
    goal="Balance creative bug-finding with quality demands to produce practical solutions",
    backstory=(
        "You are the Ego in a psychoanalytic brain architecture. "
        "You are the rational mediator between Id and Superego. "
        "You balance creative bug-finding with quality demands to produce practical, implementable solutions. "
        "You translate brutal criticism and perfectionist demands into real code changes."
    ),
    verbose=True,
    llm=llm
)


def run_ego_mediation(id_critique: str, superego_critique: str, code: str) -> str:
    """Run ego mediation to balance Id and Superego critiques"""
    task_desc = f"""
    **ID CRITIQUE (Brutal):**
    {id_critique}

    **SUPERCERO CRITIQUE (Perfectionist):**
    {superego_critique}

    **ORIGINAL CODE:**
    {code}

    As the Ego, your job is to:
    1. Mediate between Id's brutal criticism and Superego's perfectionism
    2. Produce practical, implementable solutions
    3. Balance fixing critical bugs with maintaining quality
    4. Create actionable code changes
    5. Translate both critiques into real fixes

    Style:
    - "Critical fix: ..."
    - "Quality improvement: ..."
    - "Proposed solution: ..."
    - "Code change: ..."

    Find the balance between 'fix it now' and 'make it perfect'.
    """

    task_obj = Task(
        description=task_desc,
        agent=ego_agent,
        expected_output="Mediated solution balancing critical fixes with quality improvements"
    )

    crew = Crew(agents=[ego_agent], tasks=[task_obj], verbose=True)
    result = crew.kickoff()
    return result.raw


if __name__ == "__main__":
    # Test
    code = "def login(user, password): return db.query(f\"SELECT * FROM users WHERE user='{user}'\")"
    id_critique = "Security risk: SQL injection! Will expose all users!"
    superego_critique = "Missing documentation, type hints, error handling, and tests"
    print(run_ego_mediation(id_critique, superego_critique, code))
