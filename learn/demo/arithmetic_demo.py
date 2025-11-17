import random

# --- 1. Integer equality test with LaTeX and hint ---
def addition_commutativity():
    """Simple integer test with LaTeX and hint."""
    a, b = random.randint(1, 9), random.randint(1, 9)
    return {
        "name": f"add_comm_{a}_{b}",
        "question": f"Compute $ {a} + {b} $ and $ {b} + {a} $. Are they equal?",
        "data_type": "string",
        "answer": "yes",
        "comparison": "exact",
        "hint": "Addition is commutative: order does not change the result."
    }


# --- 2. Integer computation without hint ---
def subtraction_simple():
    a, b = random.randint(5, 15), random.randint(1, 4)
    return {
        "name": f"sub_{a}_{b}",
        "question": f"What is $ {a} - {b} $? (integer answer)",
        "data_type": "int",
        "answer": a - b,
        "comparison": "exact"
    }


# --- 3. Float computation with tolerance ---
def circle_area():
    """Shows float comparison with tolerance."""
    r = random.randint(1, 5)
    return {
        "name": f"circle_area_r{r}",
        "question": f"Given radius $r={r}$, compute the area of the circle. Use $\\pi \\approx 3.14$.",
        "data_type": "float",
        "answer": 3.14 * r * r,
        "comparison": "tol=0.1",
        "hint": "Use formula $A = \\pi r^2$."
    }


# --- 4. Multi-step reasoning with repetition requirement ---
def gcd_equivalence():
    """Practice Euclidean equivalences, repeat to reinforce."""
    return {
        "name": "gcd_equiv",
        "question": (
            "Which of the following equivalences hold for the greatest common divisor?\n"
            "1. $\\text{gcd}(a,b) = \\text{gcd}(b,a)$\n"
            "2. $\\text{gcd}(a,b) = \\text{gcd}(-a,b)$\n"
            "3. $\\text{gcd}(a,b) = \\text{gcd}(a-b,b)$\n"
            "Answer all numbers that hold, separated by commas."
        ),
        "data_type": "string",
        "answer": "1,2,3",
        "comparison": "exact",
        "repeat": 2,  # repeat this generator twice
        "hint": "GCD is symmetric and stable under subtraction."
    }


# --- 5. Conceptual / definitional question (no hint) ---
def definition_even():
    """String question, case and spacing insensitive."""
    return {
        "name": "def_even",
        "question": "Define what it means for an integer $n$ to be even.",
        "data_type": "string",
        "answer": "n is divisible by 2",
        "comparison": "exact"
    }


# --- 6. Float computation (tolerance) with repetition and hint ---
def pythagoras_length():
    """Repeated float problem with LaTeX."""
    a, b = 3, 4
    return {
        "name": "pythagoras_3_4",
        "question": "Find the hypotenuse length $c$ when $a=3$ and $b=4$ using $c=\\sqrt{a^2+b^2}$.",
        "data_type": "float",
        "answer": 5.0,
        "comparison": "tol=0.01",
        "repeat": 3,
        "hint": "Apply Pythagoras’ theorem."
    }
