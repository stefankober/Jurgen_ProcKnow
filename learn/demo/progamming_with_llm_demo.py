import random

CONSTRUCTS = [
    "numbers",
    "strings",
    "lists",
    "dictionaries",
    "sets",
    "for-loops",
    "while-loops",
    "if-else",
    "functions",
    "recursion",
    "classes",
    "exceptions",
    "list comprehensions",
    "file I/O",
    "sorting",
    "lambda expressions",
]


def _pick_constructs(k_min=2, k_max=4):
    k = random.randint(k_min, k_max)
    return random.sample(CONSTRUCTS, k)


def _build_llm_prompt(language, constructs, extra_constraints):
    constructs_str = ", ".join(constructs)
    constraints_str = " ".join(extra_constraints)
    return (
        f"Give me a {language} programming exercise that *requires* using "
        f"the following constructs: {constructs_str}. "
        f"{constraints_str} "
        "Do not provide the solution, only the problem statement."
    )


def llm_practice_basic():
    """
    Card: ask LLM for a basic problem and self-report if you solved it.
    """
    constructs = _pick_constructs(2, 3)
    prompt_text = _build_llm_prompt(
        language="beginner-friendly Python",
        constructs=constructs,
        extra_constraints=[
            "The exercise should be suitable for a beginner,",
            "should be solvable in under 20 lines of code,",
            "and should involve some clear input and output.",
        ],
    )

    question = (
        "Put the following prompt into a large language model (for example ChatGPT).\n"
        "Then try to solve the programming exercise it returns *without asking it for the solution*.\n\n"
        "When you come back here, answer:\n"
        "- 'yes' if you solved it completely on your own,\n"
        "- 'no' if you did not fully solve it.\n\n"
        "Prompt to send to the LLM:\n"
        "----------------------------------------\n"
        f"{prompt_text}\n"
        "----------------------------------------\n"
    )

    return {
        "name": "llm_practice_basic",
        "question": question,
        "data_type": "string",
        # Semantics: 'yes' = success (counted as correct), 'no' = not yet (counted as wrong)
        "answer": "yes",
        "comparison": "exact",
        "repeat": 3,
        "hint": "Be honest. This log is for you. 'No' is not failure, it is training data.",
    }


def llm_practice_intermediate():
    """
    Card: ask LLM for an intermediate problem with specific constraints.
    """
    constructs = _pick_constructs(3, 4)
    prompt_text = _build_llm_prompt(
        language="intermediate-level Python",
        constructs=constructs,
        extra_constraints=[
            "The exercise should take about 20–40 minutes to solve,",
            "should require breaking the problem down into smaller functions,",
            "and should include at least one non-trivial edge case.",
        ],
    )

    question = (
        "Use a large language model to generate and then solve a programming problem.\n\n"
        "Steps:\n"
        "1. Copy the prompt below into an LLM (for example ChatGPT).\n"
        "2. Read the exercise it returns.\n"
        "3. Solve it on your own in your editor or REPL.\n"
        "4. Only if you are stuck, you may ask the LLM for hints (not the full solution).\n\n"
        "Back here in Jürgen ProcKnow, answer:\n"
        "- 'yes' if you ended up with a working solution you understand,\n"
        "- 'no' otherwise.\n\n"
        "Prompt to send to the LLM:\n"
        "----------------------------------------\n"
        f"{prompt_text}\n"
        "Also: briefly describe the real-world scenario this exercise could come from.\n"
        "----------------------------------------\n"
    )

    return {
        "name": "llm_practice_intermediate",
        "question": question,
        "data_type": "string",
        "answer": "yes",
        "comparison": "exact",
        "repeat": 3,
        "hint": "Focus on the constructs mentioned. If you struggled, 'no' is useful feedback.",
    }


def llm_practice_advanced():
    """
    Card: multi-part, more advanced exercise, still self-evaluated yes/no.
    """
    constructs = _pick_constructs(4, 5)
    prompt_text = _build_llm_prompt(
        language="more advanced Python",
        constructs=constructs,
        extra_constraints=[
            "The problem should have two parts (A and B),",
            "where B builds on A and adds one extra requirement.",
            "The exercise should mention time complexity considerations.",
        ],
    )

    question = (
        "Advanced self-training with an LLM.\n\n"
        "1. Copy the prompt below into a large language model.\n"
        "2. Let it generate the two-part programming challenge.\n"
        "3. Solve Part A and Part B on your own.\n"
        "4. Optionally, ask the LLM to review your solution afterwards.\n\n"
        "When you return, answer:\n"
        "- 'yes' if you solved both parts and understand your solution,\n"
        "- 'no' if you did not fully solve them or needed the LLM to write key parts.\n\n"
        "Prompt to send to the LLM:\n"
        "----------------------------------------\n"
        f"{prompt_text}\n"
        "----------------------------------------\n"
    )

    return {
        "name": "llm_practice_advanced",
        "question": question,
        "data_type": "string",
        "answer": "yes",
        "comparison": "exact",
        "repeat": 3,
        "hint": "If you only solved Part A, be strict with yourself and answer 'no'.",
    }
