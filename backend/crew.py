from crewai import Agent, Task, Crew, Process, LLM
import os
import litellm




litellm.drop_params = True


def _clean_messages(messages):
    cleaned = []
    for msg in messages:
        if isinstance(msg, dict):
            msg = {k: v for k, v in msg.items() if k != "cache_breakpoint"}
            if isinstance(msg.get("content"), list):
                msg["content"] = [
                    {k: v for k, v in block.items() if k != "cache_breakpoint"}
                    if isinstance(block, dict) else block
                    for block in msg["content"]
                ]
        cleaned.append(msg)
    return cleaned

_original_completion = litellm.completion

def _patched_completion(*args, **kwargs):
    if "messages" in kwargs:
        kwargs["messages"] = _clean_messages(kwargs["messages"])
    elif args:
        args = list(args)
        if len(args) > 1 and isinstance(args[1], list):
            args[1] = _clean_messages(args[1])
        args = tuple(args)
    return _original_completion(*args, **kwargs)

litellm.completion = _patched_completion


llm = LLM(
    model="groq/llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.2,
)

detector = Agent(
    role="Bug Detector",
    goal="Identify all bugs, errors, and potential issues in the provided code.",
    backstory=(
        "You are a meticulous static-analysis expert. "
        "You spot syntax errors, logical flaws, off-by-one errors, "
        "unhandled exceptions, and security vulnerabilities instantly."
    ),
    llm=llm,
    verbose=True,
    allow_delegation=False,
    cache=False,
)

reviewer = Agent(
    role="Code Reviewer",
    goal="Evaluate code quality, style, and best practices.",
    backstory=(
        "You are a senior engineer obsessed with clean, maintainable code. "
        "You review for readability, naming conventions, SOLID principles, "
        "unnecessary complexity, and missing documentation."
    ),
    llm=llm,
    verbose=True,
    allow_delegation=False,
    cache=False,
)

corrector = Agent(
    role="Code Corrector",
    goal="Rewrite the code fixing all detected bugs and applying all review suggestions.",
    backstory=(
        "You are a pragmatic refactoring specialist. "
        "Given a bug report and review feedback, you produce clean, corrected, "
        "production-ready code with inline comments explaining every change."
    ),
    llm=llm,
    verbose=True,
    allow_delegation=False,
    cache=False,
)

tester = Agent(
    role="Test Engineer",
    goal="Write comprehensive unit tests for the corrected code.",
    backstory=(
        "You are a TDD advocate. You write pytest unit tests that cover "
        "happy paths, edge cases, and error conditions. "
        "You also provide a brief test-coverage summary."
    ),
    llm=llm,
    verbose=True,
    allow_delegation=False,
    cache=False,
)


def build_crew(code: str) -> Crew:
    detect_task = Task(
        description=(
            f"Analyze the following code and list every bug, error, "
            f"and potential issue you find. Be exhaustive.\n\n```\n{code}\n```"
        ),
        expected_output="A numbered list of all identified bugs and issues.",
        agent=detector,
    )

    review_task = Task(
        description=(
            "Using the bug report above, also review the same code for "
            "code quality, style, and best-practice violations. "
            "Provide concrete, actionable suggestions."
        ),
        expected_output="A numbered list of code-quality and style recommendations.",
        agent=reviewer,
        context=[detect_task],
    )

    correct_task = Task(
        description=(
            "Using the bug report and the review suggestions, rewrite the code "
            "so that all issues are resolved. Include inline comments for every change. "
            "Important: Do not mention try/except in the summary unless you actually added them in the code. "
            "Return numeric values from functions, not strings. "
            "Do not duplicate validation checks."
        ),
        expected_output=(
            "The fully corrected code in a fenced code block, "
            "followed by a summary of changes made."
        ),
        agent=corrector,
        context=[detect_task, review_task],
    )

    test_task = Task(
        description=(
            "Write a complete pytest test suite for the corrected code. "
            "Cover normal cases, edge cases, and expected exceptions."
        ),
        expected_output=(
            "A ready-to-run pytest file in a fenced code block, "
            "followed by a short coverage summary."
        ),
        agent=tester,
        context=[correct_task],
    )

    return Crew(
        agents=[detector, reviewer, corrector, tester],
        tasks=[detect_task, review_task, correct_task, test_task],
        process=Process.sequential,
        verbose=True,
        cache=False,
    )


def run_review(code: str) -> dict:
    crew = build_crew(code)
    result = crew.kickoff()

    tasks = crew.tasks
    return {
        "bugs":         tasks[0].output.raw if tasks[0].output else "",
        "review":       tasks[1].output.raw if tasks[1].output else "",
        "corrected":    tasks[2].output.raw if tasks[2].output else "",
        "tests":        tasks[3].output.raw if tasks[3].output else "",
        "final_output": str(result),
    }