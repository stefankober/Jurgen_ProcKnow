import random

SITUATIONS = [
    {
        "template": "A colleague asks you to stay two extra hours today. Your rule: on workdays you only say yes if it supports your own priorities.",
        "want": False
    },
    {
        "template": "A friend invites you to a long spontaneous phone call. Your rule: on weekdays, conserve energy unless you initiated the contact.",
        "want": False
    },
    {
        "template": "Someone asks you for a quick favor that aligns with your current goals and costs almost no time.",
        "want": True
    },
    {
        "template": "A team member wants you to lead a task you enjoy, and it fits your development plan.",
        "want": True
    },
    {
        "template": "A distant acquaintance invites you to an event you don’t care about, and you already feel tired.",
        "want": False
    },
    {
        "template": "A close friend asks for help with something you value and have time for.",
        "want": True
    },
    {
        "template": "Your inbox shows a request for a task that is not your responsibility and derails your focus.",
        "want": False
    },
    {
        "template": "Someone asks you to join a project that strongly aligns with your long-term goals.",
        "want": True
    },
]

def personal_yes_no():
    item = random.choice(SITUATIONS)
    situation = item["template"]
    want = item["want"]
    ans = "yes" if want else "no"

    return {
        "name": "personal_yes_no",
        "question": f"Situation:\n\n{situation}\n\nGiven your rule: what is the correct response?",
        "data_type": "string",
        "answer": ans,
        "comparison": "exact",
        "repeat": 3,
        "hint": "Follow the stated personal rule, not the social pressure."
    }
