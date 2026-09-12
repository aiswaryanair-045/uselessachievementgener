import cv2
import numpy as np

from config import (
    HAND_MOTION_THRESHOLD,
    FACE_MOTION_THRESHOLD,
    MIN_BOOK_AREA,
    MIN_PEN_LENGTH
)


class ActionDetector:

    def __init__(self):

        self.previous_gray = None

    def detect(self, frame):

        gray = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2GRAY
        )

        gray = cv2.GaussianBlur(
            gray,
            (21, 21),
            0
        )

        height, width = gray.shape

        motion = 0

        if self.previous_gray is not None:

            difference = cv2.absdiff(
                self.previous_gray,
                gray
            )

            _, threshold = cv2.threshold(
                difference,
                25,
                255,
                cv2.THRESH_BINARY
            )

            motion = np.sum(
                threshold
            ) / 255

        self.previous_gray = gray.copy()

        # --------------------------------
        # RAISE HANDS
        # --------------------------------

        upper = frame[
            0:int(height * 0.55),
            :
        ]

        if motion > HAND_MOTION_THRESHOLD:

            upper_gray = cv2.cvtColor(
                upper,
                cv2.COLOR_BGR2GRAY
            )

            edges = cv2.Canny(
                upper_gray,
                60,
                150
            )

            contours, _ = cv2.findContours(
                edges,
                cv2.RETR_EXTERNAL,
                cv2.CHAIN_APPROX_SIMPLE
            )

            large_objects = 0

            for contour in contours:

                area = cv2.contourArea(
                    contour
                )

                if area > 1000:
                    large_objects += 1

            if large_objects >= 2:
                return "RAISE HANDS"


        # --------------------------------
        # WEIRD FACE
        # --------------------------------

        face_region = frame[
            int(height * 0.10):
            int(height * 0.60),

            int(width * 0.20):
            int(width * 0.80)
        ]

        if motion > FACE_MOTION_THRESHOLD:

            face_gray = cv2.cvtColor(
                face_region,
                cv2.COLOR_BGR2GRAY
            )

            face_edges = cv2.Canny(
                face_gray,
                80,
                180
            )

            edge_count = np.sum(
                face_edges > 0
            )

            if edge_count > 4000:

                return "WEIRD FACE"


        # --------------------------------
        # BOOK
        # --------------------------------

        edges = cv2.Canny(
            gray,
            60,
            150
        )

        contours, _ = cv2.findContours(
            edges,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        for contour in contours:

            area = cv2.contourArea(
                contour
            )

            if area < MIN_BOOK_AREA:
                continue

            perimeter = cv2.arcLength(
                contour,
                True
            )

            if perimeter == 0:
                continue

            polygon = cv2.approxPolyDP(
                contour,
                0.03 * perimeter,
                True
            )

            if 4 <= len(polygon) <= 6:

                x, y, w, h = cv2.boundingRect(
                    polygon
                )

                ratio = w / float(h)

                if (
                    0.5 < ratio < 2.2
                    and w > 150
                    and h > 100
                ):

                    return "LOOKING AT BOOK"


        # --------------------------------
        # PEN
        # --------------------------------

        for contour in contours:

            x, y, w, h = cv2.boundingRect(
                contour
            )

            long_side = max(w, h)

            short_side = max(
                1,
                min(w, h)
            )

            ratio = (
                long_side /
                short_side
            )

            if (
                ratio > 7
                and long_side > MIN_PEN_LENGTH
                and short_side < 45
            ):

                return "TAKING PEN"


        return "UNKNOWN"