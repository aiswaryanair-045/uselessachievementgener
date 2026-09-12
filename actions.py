# ==========================================
# ACTIONS
# ==========================================

ACTIONS = {
    "RAISE HANDS": 10,
    "WEIRD FACE": 15,
    "LOOKING AT BOOK": -10,
    "TAKING PEN": -10
}


def get_points(action):
    return ACTIONS.get(action, 0)


def is_useless(action):
    return get_points(action) > 0


def get_message(score):

    if score >= 80:
        return "LEGENDARY USELESSNESS!"

    elif score >= 50:
        return "MASTER OF USELESSNESS!"

    elif score >= 30:
        return "VERY USELESS!"

    elif score > 0:
        return "KEEP BEING USELESS!"

    elif score < 0:
        return "PRODUCTIVITY DETECTED!"

    return "DO SOMETHING USELESS!"