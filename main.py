# ==========================================
# USELESS GENERATOR
# MAIN PROGRAM
# ==========================================

import cv2
import time

from detector import ActionDetector
from actions import get_points, get_message
from config import SCORE_COOLDOWN


# ==========================================
# CAMERA
# ==========================================

camera = cv2.VideoCapture(0)

if not camera.isOpened():

    print()
    print("ERROR: Camera could not be opened.")
    print("Try changing CAMERA_ID in config.py")
    print("from 0 to 1.")
    print()

    exit()


# ==========================================
# OBJECTS
# ==========================================

detector = ActionDetector()

score = 0

last_action = "None"

last_score_time = 0


# ==========================================
# FUNCTIONS
# ==========================================

def draw_text(
    frame,
    message,
    x,
    y,
    size=0.7
):

    cv2.putText(
        frame,
        message,
        (x, y),
        cv2.FONT_HERSHEY_SIMPLEX,
        size,
        (255, 255, 255),
        2,
        cv2.LINE_AA
    )


def update_score(action):

    global score
    global last_action
    global last_score_time

    if action == "UNKNOWN":
        return

    now = time.time()

    if now - last_score_time < SCORE_COOLDOWN:
        return

    points = get_points(action)

    score += points

    last_action = action

    last_score_time = now

    if points > 0:

        print(
            f"USELESS ACTION: "
            f"{action} +{points}"
        )

    else:

        print(
            f"PRODUCTIVITY DETECTED: "
            f"{action} {points}"
        )


# ==========================================
# START
# ==========================================

print()
print("========================================")
print("       USELESS GENERATOR")
print("========================================")
print()
print("Actions:")
print()
print("Raise hands       +10")
print("Weird face        +15")
print("Look at book      -10")
print("Take pen          -10")
print()
print("R = Reset score")
print("D = Show detection regions")
print("Q = Quit")
print()
print("========================================")
print()


show_regions = False


# ==========================================
# MAIN LOOP
# ==========================================

while True:

    success, frame = camera.read()

    if not success:

        print(
            "ERROR: Could not read camera."
        )

        break


    # Mirror camera
    frame = cv2.flip(
        frame,
        1
    )


    height, width = frame.shape[:2]


    # ======================================
    # DETECT
    # ======================================

    action = detector.detect(
        frame
    )


    # ======================================
    # SCORE
    # ======================================

    update_score(
        action
    )


    # ======================================
    # USELESSNESS
    # ======================================

    uselessness = max(
        0,
        min(
            100,
            50 + score
        )
    )


    # ======================================
    # TOP PANEL
    # ======================================

    overlay = frame.copy()

    cv2.rectangle(
        overlay,
        (0, 0),
        (width, 145),
        (20, 20, 20),
        -1
    )

    cv2.addWeighted(
        overlay,
        0.85,
        frame,
        0.15,
        0,
        frame
    )


    draw_text(
        frame,
        "USELESS GENERATOR",
        20,
        35,
        0.85
    )


    draw_text(
        frame,
        f"SCORE: {score}",
        20,
        75,
        0.75
    )


    # ======================================
    # ACTION
    # ======================================

    if action != "UNKNOWN":

        draw_text(
            frame,
            f"ACTION: {action}",
            20,
            115,
            0.65
        )

    else:

        draw_text(
            frame,
            "ACTION: Watching...",
            20,
            115,
            0.65
        )


    # ======================================
    # METER
    # ======================================

    draw_text(
        frame,
        f"USELESSNESS: {uselessness}%",
        20,
        180,
        0.65
    )


    meter_x = 20
    meter_y = 200
    meter_width = 500
    meter_height = 30


    cv2.rectangle(
        frame,
        (
            meter_x,
            meter_y
        ),
        (
            meter_x + meter_width,
            meter_y + meter_height
        ),
        (180, 180, 180),
        2
    )


    filled = int(
        meter_width *
        uselessness /
        100
    )


    if filled > 0:

        cv2.rectangle(
            frame,
            (
                meter_x,
                meter_y
            ),
            (
                meter_x + filled,
                meter_y + meter_height
            ),
            (255, 255, 255),
            -1
        )


    # ======================================
    # FUNNY MESSAGE
    # ======================================

    message = get_message(
        score
    )


    draw_text(
        frame,
        message,
        20,
        285,
        0.7
    )


    # ======================================
    # LAST ACTION
    # ======================================

    draw_text(
        frame,
        f"Last action: {last_action}",
        20,
        325,
        0.55
    )


    # ======================================
    # CONTROLS
    # ======================================

    draw_text(
        frame,
        "R = Reset    D = Detection areas    Q = Quit",
        20,
        height - 25,
        0.5
    )


    # ======================================
    # OPTIONAL DETECTION REGIONS
    # ======================================

    if show_regions:

        detector.draw_regions(
            frame
        )


    # ======================================
    # SHOW CAMERA
    # ======================================

    cv2.imshow(
        "USELESS GENERATOR",
        frame
    )


    # ======================================
    # KEYBOARD
    # ======================================

    key = cv2.waitKey(1) & 0xFF


    if key == ord("q"):

        break


    elif key == ord("r"):

        score = 0

        last_action = "Reset"

        last_score_time = 0

        print(
            "Score reset!"
        )


    elif key == ord("d"):

        show_regions = not show_regions


# ==========================================
# CLEANUP
# ==========================================

camera.release()

cv2.destroyAllWindows()


print()
print("========================================")
print("FINAL USELESS SCORE:", score)
print("========================================")