#!/usr/bin/env python3

from config import SUPERCERO_MODEL, OLLAMA_BASE_URL, SUPERCERO_TEMPERATURE
from crewai import Agent, LLM, Task, Crew

llm = LLM(
    model=SUPERCERO_MODEL,
    base_url=OLLAMA_BASE_URL,
    temperature=SUPERCERO_TEMPERATURE,
)

superego_agent = Agent(
    role="Superego - Perfectionist Guardian",
    goal="Demand excellence, proper documentation, and adherence to best practices",
    backstory=(
        "You are the Superego in a psychoanalytic brain architecture. "
        "You are the perfectionist, the quality gatekeeper. "
        "You demand excellence, proper documentation, comprehensive testing, and adherence to all best practices. "
        "You do not accept it works - you demand it is perfect."
    ),
    verbose=True,
    llm=llm
)


def run_superego_critique(code: str, task: str) -> str:
    """Run superego critique to demand quality and best practices"""
    task_desc = f"""
    **TASK:** {task}

    **CODE:**
    {code}

    As the Superego, your job is to:
    1. Demand proper documentation and type hints
    2. Require comprehensive testing
    3. Enforce best practices and coding standards
    4. Point out missing error handling
    5. Demand architectural cleanliness

    Style:
    - "This needs documentation: ..."
    - "Missing tests for..."
    - "Best practice violation: ..."
    - "Should be refactored to..."

    Do not accept 'it works' - demand 'it is perfect'.
    """

    task_obj = Task(
        description=task_desc,
        agent=superego_agent,
        expected_output="Perfectionist critique demanding quality, documentation, and best practices"
    )

    crew = Crew(agents=[superego_agent], tasks=[task_obj], verbose=True)
    result = crew.kickoff()
    return result.raw


if __name__ == "__main__":
    # Test
    code = "def add(a,b): return a+b"
    print(run_superego_critique(code, "Check for quality issues"))
