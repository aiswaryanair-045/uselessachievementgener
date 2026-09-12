import cv2
import numpy as np
import time
import math

# ============================================================
# USELESS GENERATOR - LIVE CALIBRATION VERSION
# One Python file
# ============================================================

CAMERA_ID = 0

# How many frames are recorded for each action
CALIBRATION_SECONDS = 3

# Minimum difference required before an action is accepted
DETECTION_THRESHOLD = 0.38

# Prevent scoring the same action repeatedly
SCORE_COOLDOWN = 2.5


# ------------------------------------------------------------
# ACTIONS
# ------------------------------------------------------------

ACTIONS = {
    "RAISE HANDS": {
        "points": 10,
        "emoji": "HANDS"
    },

    "WEIRD FACE": {
        "points": 15,
        "emoji": "FACE"
    },

    "LOOK AT BOOK": {
        "points": -10,
        "emoji": "BOOK"
    },

    "TAKE PEN": {
        "points": -10,
        "emoji": "PEN"
    }
}


# ------------------------------------------------------------
# CAMERA
# ------------------------------------------------------------

cap = cv2.VideoCapture(CAMERA_ID)

if not cap.isOpened():
    print("Camera could not be opened.")
    print("Try changing CAMERA_ID from 0 to 1.")
    exit()


# ------------------------------------------------------------
# VARIABLES
# ------------------------------------------------------------

mode = "MENU"

current_action = "Waiting..."

score = 0

last_scored_action = ""
last_score_time = 0

calibration_data = {}

calibration_order = [
    "RAISE HANDS",
    "WEIRD FACE",
    "LOOK AT BOOK",
    "TAKE PEN"
]

calibration_index = 0

calibration_start = 0

samples = []

previous_gray = None


# ------------------------------------------------------------
# HELPER FUNCTIONS
# ------------------------------------------------------------

def put_text(frame, text, position, size=0.7):
    cv2.putText(
        frame,
        text,
        position,
        cv2.FONT_HERSHEY_SIMPLEX,
        size,
        (255, 255, 255),
        2,
        cv2.LINE_AA
    )


def normalize_feature(feature):
    """
    Normalize a feature vector so lighting/camera size
    has less effect.
    """
    feature = np.array(feature, dtype=np.float32)

    norm = np.linalg.norm(feature)

    if norm < 0.0001:
        return feature

    return feature / norm


# ------------------------------------------------------------
# FEATURE EXTRACTION
# ------------------------------------------------------------

def get_features(frame):
    """
    Extract simple visual/movement features.

    This does not use an external AI model.
    """

    height, width = frame.shape[:2]

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    gray = cv2.resize(gray, (32, 24))

    # Normalize brightness
    gray = gray.astype(np.float32) / 255.0

    # Divide image into regions
    regions = []

    h, w = gray.shape

    regions.append(gray[0:int(h * 0.45), :])
    regions.append(gray[int(h * 0.45):, :])

    regions.append(gray[:, 0:int(w * 0.33)])
    regions.append(gray[:, int(w * 0.33):int(w * 0.66)])
    regions.append(gray[:, int(w * 0.66):])

    feature = []

    # Average brightness of regions
    for region in regions:
        feature.append(float(np.mean(region)))
        feature.append(float(np.std(region)))

    # Edge information
    edges = cv2.Canny(
        (gray * 255).astype(np.uint8),
        60,
        150
    )

    edge_small = cv2.resize(
        edges,
        (16, 12)
    )

    edge_small = edge_small.astype(np.float32) / 255.0

    feature.extend(edge_small.flatten().tolist())

    return normalize_feature(feature)


# ------------------------------------------------------------
# DISTANCE BETWEEN TWO ACTIONS
# ------------------------------------------------------------

def feature_distance(a, b):
    a = np.array(a)
    b = np.array(b)

    return float(np.linalg.norm(a - b))


# ------------------------------------------------------------
# CALIBRATION
# ------------------------------------------------------------

def start_calibration():
    global mode
    global calibration_index
    global calibration_start
    global samples

    mode = "CALIBRATION"

    calibration_index = 0

    samples = []

    calibration_start = time.time()


def finish_current_calibration():
    global calibration_data
    global samples
    global calibration_index
    global calibration_start

    if len(samples) == 0:
        return

    action = calibration_order[calibration_index]

    # Average all samples
    average = np.mean(
        np.array(samples),
        axis=0
    )

    calibration_data[action] = normalize_feature(average)

    print()
    print("Learned:", action)
    print("Samples:", len(samples))

    samples = []

    calibration_index += 1

    calibration_start = time.time()


# ------------------------------------------------------------
# DETECT ACTION
# ------------------------------------------------------------

def detect_action(feature):
    if len(calibration_data) == 0:
        return "UNKNOWN", 999

    best_action = "UNKNOWN"
    best_distance = 999

    for action, learned_feature in calibration_data.items():

        distance = feature_distance(
            feature,
            learned_feature
        )

        if distance < best_distance:
            best_distance = distance
            best_action = action

    if best_distance <= DETECTION_THRESHOLD:
        return best_action, best_distance

    return "UNKNOWN", best_distance


# ------------------------------------------------------------
# SCORE
# ------------------------------------------------------------

def add_score(action):

    global score
    global last_scored_action
    global last_score_time

    now = time.time()

    points = ACTIONS[action]["points"]

    # Prevent constant scoring
    if (
        action == last_scored_action
        and now - last_score_time < SCORE_COOLDOWN
    ):
        return

    if now - last_score_time < 0.8:
        return

    score += points

    last_scored_action = action
    last_score_time = now

    if points > 0:
        print(
            "USELESS ACTION:",
            action,
            "+",
            points
        )
    else:
        print(
            "PRODUCTIVITY DETECTED:",
            action,
            points
        )


# ------------------------------------------------------------
# MAIN LOOP
# ------------------------------------------------------------

print()
print("======================================")
print("       USELESS GENERATOR")
print("======================================")
print()
print("Press C = Start calibration")
print("Press G = Start game")
print("Press R = Reset score")
print("Press Q = Quit")
print()
print("Camera starting...")
print()


while True:

    success, frame = cap.read()

    if not success:
        print("Could not read camera.")
        break

    frame = cv2.flip(frame, 1)

    height, width = frame.shape[:2]

    # --------------------------------------------------------
    # GET FEATURES
    # --------------------------------------------------------

    feature = get_features(frame)

    # --------------------------------------------------------
    # MENU
    # --------------------------------------------------------

    if mode == "MENU":

        overlay = frame.copy()

        cv2.rectangle(
            overlay,
            (0, 0),
            (width, height),
            (20, 20, 20),
            -1
        )

        cv2.addWeighted(
            overlay,
            0.75,
            frame,
            0.25,
            0,
            frame
        )

        put_text(
            frame,
            "USELESS GENERATOR",
            (width // 2 - 230, 100),
            1.2
        )

        put_text(
            frame,
            "Teach the camera your actions!",
            (width // 2 - 220, 150),
            0.7
        )

        put_text(
            frame,
            "C = Calibration",
            (width // 2 - 130, 220),
            0.7
        )

        put_text(
            frame,
            "G = Game",
            (width // 2 - 100, 265),
            0.7
        )

        put_text(
            frame,
            "Q = Quit",
            (width // 2 - 100, 310),
            0.7
        )

        put_text(
            frame,
            "Actions:",
            (width // 2 - 100, 390),
            0.7
        )

        put_text(
            frame,
            "Raise hands     +10",
            (width // 2 - 100, 430),
            0.6
        )

        put_text(
            frame,
            "Weird face       +15",
            (width // 2 - 100, 465),
            0.6
        )

        put_text(
            frame,
            "Look at book     -10",
            (width // 2 - 100, 500),
            0.6
        )

        put_text(
            frame,
            "Take pen         -10",
            (width // 2 - 100, 535),
            0.6
        )

    # --------------------------------------------------------
    # CALIBRATION
    # --------------------------------------------------------

    elif mode == "CALIBRATION":

        action = calibration_order[calibration_index]

        elapsed = time.time() - calibration_start

        remaining = CALIBRATION_SECONDS - elapsed

        if remaining <= 0:

            finish_current_calibration()

            if calibration_index >= len(calibration_order):

                mode = "READY"

                print()
                print("================================")
                print("CALIBRATION COMPLETE!")
                print("================================")
                print()

            continue

        # Record sample
        samples.append(feature)

        # Dark top panel
        overlay = frame.copy()

        cv2.rectangle(
            overlay,
            (0, 0),
            (width, 150),
            (20, 20, 20),
            -1
        )

        cv2.addWeighted(
            overlay,
            0.8,
            frame,
            0.2,
            0,
            frame
        )

        put_text(
            frame,
            "CALIBRATING",
            (25, 40),
            0.8
        )

        put_text(
            frame,
            "DO THIS: " + action,
            (25, 85),
            0.8
        )

        put_text(
            frame,
            "Time: " + str(round(remaining, 1)),
            (25, 125),
            0.6
        )

        put_text(
            frame,
            "Perform the action naturally",
            (25, height - 30),
            0.6
        )

    # --------------------------------------------------------
    # READY
    # --------------------------------------------------------

    elif mode == "READY":

        overlay = frame.copy()

        cv2.rectangle(
            overlay,
            (0, 0),
            (width, height),
            (20, 20, 20),
            -1
        )

        cv2.addWeighted(
            overlay,
            0.7,
            frame,
            0.3,
            0,
            frame
        )

        put_text(
            frame,
            "CALIBRATION COMPLETE!",
            (width // 2 - 250, 150),
            1.0
        )

        put_text(
            frame,
            "Press G to start the game",
            (width // 2 - 190, 230),
            0.75
        )

        put_text(
            frame,
            "Press C to calibrate again",
            (width // 2 - 190, 280),
            0.65
        )

    # --------------------------------------------------------
    # GAME
    # --------------------------------------------------------

    elif mode == "GAME":

        detected, distance = detect_action(feature)

        current_action = detected

        # Score detected action
        if detected != "UNKNOWN":

            add_score(detected)

        # ----------------------------------------------------
        # UI
        # ----------------------------------------------------

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

        put_text(
            frame,
            "USELESS GENERATOR",
            (20, 35),
            0.85
        )

        put_text(
            frame,
            "SCORE: " + str(score),
            (20, 75),
            0.75
        )

        if detected != "UNKNOWN":

            put_text(
                frame,
                "ACTION: " + detected,
                (20, 115),
                0.65
            )

        else:

            put_text(
                frame,
                "ACTION: Watching...",
                (20, 115),
                0.65
            )

        # ----------------------------------------------------
        # USELESSNESS METER
        # ----------------------------------------------------

        # Keep meter between 0 and 100
        uselessness = max(
            0,
            min(
                100,
                50 + score
            )
        )

        put_text(
            frame,
            "USELESSNESS: " + str(uselessness) + "%",
            (20, 185),
            0.65
        )

        meter_x = 20
        meter_y = 205
        meter_width = 500
        meter_height = 30

        cv2.rectangle(
            frame,
            (meter_x, meter_y),
            (
                meter_x + meter_width,
                meter_y + meter_height
            ),
            (180, 180, 180),
            2
        )

        filled = int(
            meter_width * uselessness / 100
        )

        if filled > 0:

            cv2.rectangle(
                frame,
                (meter_x, meter_y),
                (
                    meter_x + filled,
                    meter_y + meter_height
                ),
                (255, 255, 255),
                -1
            )

        # ----------------------------------------------------
        # FUNNY MESSAGE
        # ----------------------------------------------------

        if score >= 80:

            message = "LEGENDARY USELESSNESS!"

        elif score >= 50:

            message = "MASTER OF USELESSNESS!"

        elif score >= 25:

            message = "VERY USELESS!"

        elif score > 0:

            message = "KEEP WASTING TIME!"

        elif score < 0:

            message = "PRODUCTIVITY DETECTED!"

        else:

            message = "DO SOMETHING USELESS!"

        put_text(
            frame,
            message,
            (20, 290),
            0.7
        )

        # ----------------------------------------------------
        # CONTROLS
        # ----------------------------------------------------

        put_text(
            frame,
            "R = Reset     C = Recalibrate     Q = Quit",
            (20, height - 25),
            0.55
        )

    # --------------------------------------------------------
    # SHOW
    # --------------------------------------------------------

    cv2.imshow(
        "USELESS GENERATOR",
        frame
    )

    key = cv2.waitKey(1) & 0xFF

    # --------------------------------------------------------
    # KEYBOARD
    # --------------------------------------------------------

    if key == ord("q"):

        break

    elif key == ord("c"):

        start_calibration()

    elif key == ord("g"):

        if len(calibration_data) == len(ACTIONS):

            mode = "GAME"

            print()
            print("================================")
            print("GAME STARTED!")
            print("================================")
            print()

        else:

            print()
            print("Please calibrate all actions first.")
            print()

    elif key == ord("r"):

        score = 0

        last_scored_action = ""

        last_score_time = 0

        print("Score reset!")


# ------------------------------------------------------------
# CLEANUP
# ------------------------------------------------------------

cap.release()

cv2.destroyAllWindows()

print()
print("======================================")
print("GAME FINISHED")
print("FINAL SCORE:", score)
print("======================================")