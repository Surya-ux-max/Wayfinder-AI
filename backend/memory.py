career_memory = {
    "profiles": []
}

def save_career_state(data: dict):
    career_memory["profiles"].append(data)

def get_latest_career_state():
    if career_memory["profiles"]:
        return career_memory["profiles"][-1]
    return None
