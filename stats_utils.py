import os
import json

# -----------------------------------------------
# Folder-specific progress DB helper utilities
# -----------------------------------------------

def get_db_file(folder_name):
    """Return the file name for storing stats of a specific folder."""
    return f"progress_{folder_name}.json"


def load_progress(folder_name):
    """Load stats for the given folder."""
    db_file = get_db_file(folder_name)
    if os.path.exists(db_file):
        try:
            with open(db_file, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_progress(folder_name, db):
    """Save stats for the given folder."""
    db_file = get_db_file(folder_name)
    with open(db_file, "w") as f:
        json.dump(db, f, indent=2)


def update_card_result(card, db, success, user_answer=None):
    """
    Update stats for a card and save to the appropriate folder's DB.
    """
    folder = card["topic"].split(".")[0]     # e.g. number_theory.chapter3 → number_theory
    key = f"{card['topic']}.{card['name']}"

    rec = db.get(key, {"correct": 0, "wrong": 0, "wrong_log": []})

    if success:
        rec["correct"] += 1
    else:
        rec["wrong"] += 1
        if user_answer is not None:
            rec["wrong_log"].append(user_answer)
            rec["wrong_log"] = rec["wrong_log"][-5:]

    db[key] = rec
    save_progress(folder, db)
