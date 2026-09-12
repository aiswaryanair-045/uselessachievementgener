import cv2
import time
import random
import numpy as np

from detector import ActionDetector

from actions import (
    get_points,
    get_rank,
    get_funny_message,
    get_action_symbol
)

from config import (
    CAMERA_ID,
    SCORE_COOLDOWN,
    MAX_HISTORY
)


# ============================================================
# CAMERA
# ============================================================

camera = cv2.VideoCapture(CAMERA_ID)

if not camera.isOpened():

    print("Camera could not be opened.")

    exit()


# ============================================================
# DETECTOR
# ============================================================

detector = ActionDetector()


# ============================================================
# GAME VARIABLES
# ============================================================

score = 0

combo = 0

last_action = "WAITING..."

last_score_time = 0

history = []

show_detection = False


# ============================================================
# COLORS
# ============================================================

BG = (18, 18, 24)

PANEL = (30, 30, 40)

WHITE = (245, 245, 245)

GRAY = (150, 150, 160)

GREEN = (80, 220, 120)

RED = (80, 80, 230)

YELLOW = (80, 210, 255)

PURPLE = (200, 100, 220)


# ============================================================
# DRAW TEXT
# ============================================================

def text(
    frame,
    message,
    position,
    size=0.6,
    color=WHITE,
    thickness=2
):

    cv2.putText(
        frame,
        str(message),
        position,
        cv2.FONT_HERSHEY_SIMPLEX,
        size,
        color,
        thickness,
        cv2.LINE_AA
    )


# ============================================================
# PANEL
# ============================================================

def panel(
    frame,
    x1,
    y1,
    x2,
    y2
):

    cv2.rectangle(
        frame,
        (x1, y1),
        (x2, y2),
        PANEL,
        -1
    )

    cv2.rectangle(
        frame,
        (x1, y1),
        (x2, y2),
        (60, 60, 70),
        1
    )


# ============================================================
# ADD HISTORY
# ============================================================

def add_history(action, points):

    global history

    history.insert(
        0,
        (action, points)
    )

    history = history[:MAX_HISTORY]


# ============================================================
# SCORE
# ============================================================

def process_action(action):

    global score
    global combo
    global last_score_time
    global last_action

    if action == "UNKNOWN":
        return

    now = time.time()

    if now - last_score_time < SCORE_COOLDOWN:
        return

    points = get_points(action)

    score += points

    last_action = action

    last_score_time = now

    add_history(
        action,
        points
    )

    if points > 0:

        combo += 1

    else:

        combo = 0


# ============================================================
# MAIN LOOP
# ============================================================

while True:

    success, frame = camera.read()

    if not success:
        break

    frame = cv2.flip(
        frame,
        1
    )

    camera_height, camera_width = frame.shape[:2]


    # ========================================================
    # DETECT
    # ========================================================

    action = detector.detect(
        frame
    )

    process_action(
        action
    )


    # ========================================================
    # CREATE APPLICATION WINDOW
    # ========================================================

    WINDOW_WIDTH = 1200
    WINDOW_HEIGHT = 720

    screen = cv2.resize(
        frame,
        (650, 480)
    )


    canvas = np.full(
        (
            WINDOW_HEIGHT,
            WINDOW_WIDTH,
            3
        ),
        BG,
        dtype="uint8"
    )


    # ========================================================
    # HEADER
    # ========================================================

    cv2.rectangle(
        canvas,
        (0, 0),
        (WINDOW_WIDTH, 70),
        PANEL,
        -1
    )

    text(
        canvas,
        "THE USELESS GENERATOR",
        (25, 45),
        1.0,
        WHITE,
        2
    )

    # LIVE indicator

    cv2.circle(
        canvas,
        (1080, 33),
        8,
        GREEN,
        -1
    )

    text(
        canvas,
        "LIVE",
        (1100, 40),
        0.6,
        GREEN
    )


    # ========================================================
    # CAMERA PANEL
    # ========================================================

    panel(
        canvas,
        20,
        90,
        670,
        610
    )

    canvas[
        105:585,
        30:680
    ] = screen


    text(
        canvas,
        "LIVE CAMERA",
        (40, 635),
        0.6,
        GRAY
    )


    # ========================================================
    # RIGHT SIDE
    # ========================================================

    # Current action

    panel(
        canvas,
        710,
        90,
        1180,
        245
    )

    text(
        canvas,
        "CURRENT ACTION",
        (735, 125),
        0.65,
        GRAY
    )


    if action != "UNKNOWN":

        symbol = get_action_symbol(
            action
        )

        points = get_points(
            action
        )

        text(
            canvas,
            symbol,
            (735, 170),
            0.8,
            YELLOW
        )

        text(
            canvas,
            action,
            (735, 205),
            0.8,
            WHITE
        )

        if points > 0:

            point_text = f"+{points} POINTS"

            point_color = GREEN

        else:

            point_text = f"{points} POINTS"

            point_color = RED

        text(
            canvas,
            point_text,
            (735, 230),
            0.6,
            point_color
        )

    else:

        text(
            canvas,
            "Watching...",
            (735, 185),
            0.8,
            GRAY
        )


    # ========================================================
    # SCORE PANEL
    # ========================================================

    panel(
        canvas,
        710,
        265,
        1180,
        450
    )

    text(
        canvas,
        "USELESS SCORE",
        (735, 300),
        0.65,
        GRAY
    )


    text(
        canvas,
        score,
        (735, 370),
        2.0,
        WHITE
    )


    # ========================================================
    # SCORE BAR
    # ========================================================

    meter = max(
        0,
        min(
            100,
            50 + score
        )
    )

    bar_x = 735
    bar_y = 395

    bar_width = 400
    bar_height = 22


    cv2.rectangle(
        canvas,
        (
            bar_x,
            bar_y
        ),
        (
            bar_x + bar_width,
            bar_y + bar_height
        ),
        (70, 70, 80),
        -1
    )


    filled = int(
        bar_width *
        meter /
        100
    )


    if filled > 0:

        cv2.rectangle(
            canvas,
            (
                bar_x,
                bar_y
            ),
            (
                bar_x + filled,
                bar_y + bar_height
            ),
            PURPLE,
            -1
        )


    text(
        canvas,
        f"USELESSNESS {meter}%",
        (735, 440),
        0.5,
        GRAY
    )


    # ========================================================
    # COMBO
    # ========================================================

    if combo >= 2:

        text(
            canvas,
            f"COMBO x{combo}!",
            (1000, 350),
            0.65,
            YELLOW
        )


    # ========================================================
    # HISTORY PANEL
    # ========================================================

    panel(
        canvas,
        710,
        470,
        1180,
        650
    )

    text(
        canvas,
        "LAST ACTIONS",
        (735, 505),
        0.65,
        GRAY
    )


    y = 540

    for action_name, points in history:

        if points > 0:

            colour = GREEN
            value = f"+{points}"

        else:

            colour = RED
            value = str(points)

        text(
            canvas,
            action_name,
            (735, y),
            0.52,
            WHITE
        )

        text(
            canvas,
            value,
            (1080, y),
            0.55,
            colour
        )

        y += 24


    # ========================================================
    # BOTTOM MESSAGE
    # ========================================================

    rank = get_rank(
        score
    )

    cv2.rectangle(
        canvas,
        (0, 660),
        (WINDOW_WIDTH, 720),
        PANEL,
        -1
    )


    text(
        canvas,
        rank,
        (30, 695),
        0.7,
        YELLOW
    )


    text(
        canvas,
        get_funny_message(score),
        (420, 695),
        0.55,
        GRAY
    )


    text(
        canvas,
        "R Reset",
        (950, 690),
        0.5,
        WHITE
    )

    text(
        canvas,
        "Q Quit",
        (1080, 690),
        0.5,
        WHITE
    )


    # ========================================================
    # SHOW
    # ========================================================

    cv2.imshow(
        "THE USELESS GENERATOR",
        canvas
    )


    # ========================================================
    # KEYS
    # ========================================================

    key = cv2.waitKey(1) & 0xFF


    if key == ord("q"):

        break


    elif key == ord("r"):

        score = 0

        combo = 0

        last_action = "RESET"

        history = []

        last_score_time = 0


# ============================================================
# CLEANUP
# ============================================================

camera.release()

cv2.destroyAllWindows()

print()
print("================================")
print("FINAL SCORE:", score)
print("================================")
