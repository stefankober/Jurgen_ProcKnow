import random
import numpy as np

def _sample_data():
    # small sample sizes for manual checking
    n = random.randint(6, 10)
    shift = round(random.uniform(-1.5, 1.5), 2)
    A = np.random.normal(0, 1, n)
    B = A + shift
    return A, B, shift

def external_ttest():
    A, B, shift = _sample_data()
    A_str = ", ".join(f"{x:.2f}" for x in A)
    B_str = ", ".join(f"{x:.2f}" for x in B)

    question = (
        f"Paired data from two conditions:\n\n"
        f"A = [{A_str}]\n"
        f"B = [{B_str}]\n\n"
        f"Your task: load into Excel/JASP/Jamovi/Python and perform a paired t-test.\n"
        f"Report the decision: reject or not_reject (alpha = 0.05)."
    )

    # ground truth for the answer (computed directly)
    import scipy.stats as st
    t, p = st.ttest_rel(A, B)
    ans = "reject" if p < 0.05 else "not_reject"

    return {
        "name": "external_ttest",
        "question": question,
        "data_type": "string",
        "answer": ans,
        "comparison": "exact",
        "repeat": 2,
        "hint": "Perform a paired t-test externally. Return: reject / not_reject."
    }


def external_wilcoxon():
    A, B, shift = _sample_data()
    A_str = ", ".join(f"{x:.2f}" for x in A)
    B_str = ", ".join(f"{x:.2f}" for x in B)

    question = (
        f"Paired non-normal data simulation:\n\n"
        f"A = [{A_str}]\n"
        f"B = [{B_str}]\n\n"
        f"Perform a Wilcoxon signed-rank test in JASP/Jamovi/Python.\n"
        f"Report: reject or not_reject (alpha = 0.05)."
    )

    import scipy.stats as st
    try:
        stat, p = st.wilcoxon(A, B)
    except:
        p = 1.0

    ans = "reject" if p < 0.05 else "not_reject"

    return {
        "name": "external_wilcoxon",
        "question": question,
        "data_type": "string",
        "answer": ans,
        "comparison": "exact",
        "repeat": 2,
        "hint": "Use Wilcoxon signed-rank. Answer: reject / not_reject."
    }


RIDDLES = [external_ttest, external_wilcoxon]

def external_tools_stats():
    func = random.choice(RIDDLES)
    return func()
