#!/usr/bin/env python3

from config import ID_MODEL, OLLAMA_BASE_URL, ID_TEMPERATURE
from crewai import Agent, LLM, Task, Crew

llm = LLM(
    model=ID_MODEL,
    base_url=OLLAMA_BASE_URL,
    temperature=ID_TEMPERATURE,
)

id_agent = Agent(
    role="Id - Impulsive Critic",
    goal="Find obvious bugs, security vulnerabilities, and performance issues quickly",
    backstory=(
        "You are the Id in a psychoanalytic brain architecture. "
        "You are impulsive, direct, and brutal. "
        "You do not care about perfection - you care about what is broken and needs fixing NOW. "
        "You spot security holes, obvious bugs, and performance problems immediately."
    ),
    verbose=True,
    llm=llm
)


def run_id_critique(code: str, task: str) -> str:
    """Run id critique to find obvious problems"""
    task_desc = f"""
    **TASK:** {task}

    **CODE:**
    {code}

    As the Id, your job is to:
    1. Spot obvious bugs and security vulnerabilities
    2. Identify performance issues
    3. Find missing input validation
    4. Point out crash risks
    5. Be DIRECT and BRUTAL - no softening

    Style:
    - "This is broken because..."
    - "Security risk: ..."
    - "Will crash if..."
    - "Fix this NOW: ..."

    Don't worry about perfection or architecture. Just find what's BROKEN.
    """

    task_obj = Task(
        description=task_desc,
        agent=id_agent,
        expected_output="Brutal critique identifying obvious bugs and security issues"
    )

    crew = Crew(agents=[id_agent], tasks=[task_obj], verbose=True)
    result = crew.kickoff()
    return result.raw


if __name__ == "__main__":
    # Test
    code = "def login(user, password): return db.query(f\"SELECT * FROM users WHERE user='{user}'\")"
    print(run_id_critique(code, "Check for security issues"))
