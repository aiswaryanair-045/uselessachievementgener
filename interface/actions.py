ACTIONS = {
    "RAISE HANDS": 10,
    "WEIRD FACE": 15,
    "LOOKING AT BOOK": -10,
    "TAKING PEN": -10
}


def get_points(action):
    return ACTIONS.get(action, 0)


def get_rank(score):

    if score >= 100:
        return "LEGENDARY USELESSNESS!"

    if score >= 70:
        return "MASTER OF USELESSNESS!"

    if score >= 40:
        return "PROFESSIONAL USELESS!"

    if score >= 20:
        return "AMATEUR USELESS!"

    if score > 0:
        return "GETTING USELESS..."

    if score < 0:
        return "PRODUCTIVITY DETECTED!"

    return "NORMAL HUMAN"


def get_action_symbol(action):

    symbols = {
        "RAISE HANDS": "HANDS",
        "WEIRD FACE": "FACE",
        "LOOKING AT BOOK": "BOOK",
        "TAKING PEN": "PEN"
    }

    return symbols.get(action, "?")


def get_funny_message(score):

    messages = [
        "Excellent waste of time!",
        "Productivity is your enemy!",
        "Keep doing absolutely nothing useful!",
        "Your talent is questionable.",
        "Society is impressed.",
        "This is completely unnecessary!",
        "Outstanding useless behavior!"
    ]

    index = abs(score) % len(messages)

    return messages[index]