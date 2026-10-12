import math
import os
import random
import time
from pathlib import Path

import cv2
import mediapipe as mp
import numpy as np

import config


# ============================================================
# PATHS
# ============================================================

MODEL_PATH = Path("hand_landmarker.task")
HIGH_SCORE_PATH = Path("highscore.txt")

WINDOW_NAME = "Finger Gun Detector"


# ============================================================
# COLORS - BGR FORMAT FOR OPENCV
# ============================================================

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (0, 0, 255)
GREEN = (0, 255, 0)
BLUE = (255, 0, 0)
YELLOW = (0, 255, 255)
CYAN = (255, 255, 0)


# ============================================================
# MEDIAPIPE
# ============================================================

mp_base = mp.tasks.BaseOptions
mp_vision = mp.tasks.vision

if not MODEL_PATH.exists():
    print()
    print("ERROR")
    print("----------------------------------------")
    print("hand_landmarker.task was not found.")
    print()
    print("Run:")
    print("    python download_model.py")
    print()
    raise SystemExit(1)


landmarker_options = mp_vision.HandLandmarkerOptions(
    base_options=mp_base(
        model_asset_path=str(MODEL_PATH)
    ),
    running_mode=mp_vision.RunningMode.IMAGE,
    num_hands=config.MAX_HANDS,
    min_hand_detection_confidence=(
        config.MIN_HAND_DETECTION_CONFIDENCE
    ),
    min_hand_presence_confidence=(
        config.MIN_HAND_PRESENCE_CONFIDENCE
    ),
    min_tracking_confidence=(
        config.MIN_TRACKING_CONFIDENCE
    ),
)

hand_landmarker = mp_vision.HandLandmarker.create_from_options(
    landmarker_options
)


# ============================================================
# GAME STATE
# ============================================================

STATE_MENU = "MENU"
STATE_PLAYING = "PLAYING"
STATE_GAME_OVER = "GAME_OVER"

game_state = STATE_MENU


# ============================================================
# GAME VARIABLES
# ============================================================

score = 0
shots = 0
hits = 0

ammo = config.MAGAZINE_SIZE

game_start_time = 0.0
last_shot_time = 0.0
last_reload_time = 0.0

high_score = 0


# ============================================================
# VISUAL EFFECT STORAGE
# ============================================================

targets = []

tracers = []
muzzle_flashes = []
explosions = []

combo_messages = []


# ============================================================
# TARGET SETTINGS
# ============================================================

TARGET_LIFETIME = 0.25

TRACER_LIFETIME = 0.12
FLASH_LIFETIME = 0.10
EXPLOSION_LIFETIME = 0.35
COMBO_LIFETIME = 0.8


# ============================================================
# HAND STATE
# ============================================================

previous_thumb_y = {}


# ============================================================
# HIGH SCORE
# ============================================================

def load_high_score():
    """
    Read the high score from disk.
    """

    if not HIGH_SCORE_PATH.exists():
        return 0

    try:
        value = HIGH_SCORE_PATH.read_text().strip()

        if not value:
            return 0

        return int(value)

    except (ValueError, OSError):
        return 0


def save_high_score(value):
    """
    Save high score to disk.
    """

    try:
        HIGH_SCORE_PATH.write_text(str(value))
    except OSError:
        pass


# ============================================================
# GEOMETRY
# ============================================================

def distance(point_a, point_b):
    """
    Calculate Euclidean distance between two MediaPipe
    normalized landmarks.
    """

    dx = point_a.x - point_b.x
    dy = point_a.y - point_b.y

    return math.sqrt(dx * dx + dy * dy)


def is_finger_extended(landmarks, tip_index, pip_index):
    """
    Determine whether a finger is extended.

    If the fingertip is farther from the wrist than the PIP
    joint, we treat the finger as extended.
    """

    wrist = landmarks[0]

    fingertip = landmarks[tip_index]

    pip = landmarks[pip_index]

    tip_distance = distance(wrist, fingertip)

    pip_distance = distance(wrist, pip)

    return tip_distance > pip_distance


def get_finger_states(landmarks):
    """
    Return states for:
        index
        middle
        ring
        pinky
    """

    index_open = is_finger_extended(
        landmarks,
        8,
        6
    )

    middle_open = is_finger_extended(
        landmarks,
        12,
        10
    )

    ring_open = is_finger_extended(
        landmarks,
        16,
        14
    )

    pinky_open = is_finger_extended(
        landmarks,
        20,
        18
    )

    return (
        index_open,
        middle_open,
        ring_open,
        pinky_open,
    )


def is_finger_gun(landmarks):
    """
    Finger gun:

        index   = open
        middle  = closed
        ring    = closed
        pinky   = closed
    """

    (
        index_open,
        middle_open,
        ring_open,
        pinky_open,
    ) = get_finger_states(landmarks)

    return (
        index_open
        and not middle_open
        and not ring_open
        and not pinky_open
    )


def is_open_palm(landmarks):
    """
    Open palm:

        index
        middle
        ring
        pinky

    are all extended.
    """

    (
        index_open,
        middle_open,
        ring_open,
        pinky_open,
    ) = get_finger_states(landmarks)

    return (
        index_open
        and middle_open
        and ring_open
        and pinky_open
    )


# ============================================================
# TARGET GEOMETRY
# ============================================================

def line_hits_circle(start, end, center, radius):
    """
    Check whether a line segment intersects a circular target.
    """

    p1 = np.array(start, dtype=float)
    p2 = np.array(end, dtype=float)
    c = np.array(center, dtype=float)

    segment = p2 - p1

    length_squared = np.dot(segment, segment)

    if length_squared == 0:
        closest = p1

    else:
        t = np.dot(c - p1, segment) / length_squared

        t = max(0.0, min(1.0, t))

        closest = p1 + t * segment

    distance_to_line = np.linalg.norm(c - closest)

    return distance_to_line <= radius


# ============================================================
# TARGET CREATION
# ============================================================

def target_radius():
    """
    Make targets slightly smaller as the score increases.
    """

    reduction = score // 40

    return max(
        15,
        config.TARGET_RADIUS - reduction
    )


def create_target(width, height):
    """
    Create one target inside the camera frame.
    """

    radius = target_radius()

    minimum_x = radius + 20
    maximum_x = width - radius - 20

    minimum_y = radius + 80
    maximum_y = height - radius - 100

    if maximum_x <= minimum_x:
        x = width // 2
    else:
        x = random.randint(
            minimum_x,
            maximum_x
        )

    if maximum_y <= minimum_y:
        y = height // 2
    else:
        y = random.randint(
            minimum_y,
            maximum_y
        )

    return {
        "x": x,
        "y": y,
        "radius": radius,
        "hit": False,
        "hit_time": 0.0,
    }


def create_targets(width, height):
    """
    Create all targets.
    """

    return [
        create_target(width, height)
        for _ in range(config.NUMBER_OF_TARGETS)
    ]


# ============================================================
# GAME RESET
# ============================================================

def reset_game(width, height):
    """
    Reset everything for a new game.
    """

    global score
    global shots
    global hits
    global ammo

    global game_start_time
    global last_shot_time
    global last_reload_time

    global targets

    score = 0
    shots = 0
    hits = 0

    ammo = config.MAGAZINE_SIZE

    game_start_time = time.monotonic()

    last_shot_time = 0.0
    last_reload_time = 0.0

    targets = create_targets(
        width,
        height
    )

    tracers.clear()
    muzzle_flashes.clear()
    explosions.clear()
    combo_messages.clear()

    previous_thumb_y.clear()


# ============================================================
# SHOOTING
# ============================================================

def shoot(
    landmarks,
    width,
    height,
    current_time
):
    """
    Fire a virtual shot from the index finger.
    """

    global score
    global shots
    global hits
    global ammo
    global last_shot_time

    if ammo <= 0:
        return

    if (
        current_time - last_shot_time
        < config.SHOT_COOLDOWN
    ):
        return

    last_shot_time = current_time

    shots += 1
    ammo -= 1

    wrist = landmarks[0]
    index_tip = landmarks[8]

    start_x = index_tip.x * width
    start_y = index_tip.y * height

    wrist_x = wrist.x * width
    wrist_y = wrist.y * height

    direction_x = start_x - wrist_x
    direction_y = start_y - wrist_y

    magnitude = math.sqrt(
        direction_x ** 2
        + direction_y ** 2
    )

    if magnitude < 1:
        magnitude = 1

    direction_x /= magnitude
    direction_y /= magnitude

    end_x = int(
        start_x + direction_x * 1200
    )

    end_y = int(
        start_y + direction_y * 1200
    )

    tracers.append({
        "start": (
            int(start_x),
            int(start_y)
        ),
        "end": (
            end_x,
            end_y
        ),
        "created": current_time,
    })

    muzzle_flashes.append({
        "x": int(start_x),
        "y": int(start_y),
        "created": current_time,
    })

    did_hit = False

    for target in targets:

        if target["hit"]:
            continue

        hit = line_hits_circle(
            (start_x, start_y),
            (end_x, end_y),
            (target["x"], target["y"]),
            target["radius"]
        )

        if hit:

            target["hit"] = True
            target["hit_time"] = current_time

            score += 10

            did_hit = True

            explosions.append({
                "x": target["x"],
                "y": target["y"],
                "created": current_time,
            })

    if did_hit:
        hits += 1

        combo_messages.append({
            "text": "HIT! +10",
            "created": current_time,
        })

    else:
        combo_messages.append({
            "text": "MISS",
            "created": current_time,
        })


# ============================================================
# RELOAD
# ============================================================

def reload_weapon(current_time):
    """
    Reload the magazine.
    """

    global ammo
    global last_reload_time

    if ammo == config.MAGAZINE_SIZE:
        return

    if (
        current_time - last_reload_time
        < config.RELOAD_COOLDOWN
    ):
        return

    ammo = config.MAGAZINE_SIZE

    last_reload_time = current_time


# ============================================================
# UPDATE TARGETS
# ============================================================

def update_targets(
    width,
    height,
    current_time
):
    """
    Replace hit targets after a short delay.
    """

    for target in targets:

        if not target["hit"]:
            continue

        age = (
            current_time
            - target["hit_time"]
        )

        if age >= TARGET_LIFETIME:

            new_target = create_target(
                width,
                height
            )

            target.update(new_target)


# ============================================================
# DRAW TARGETS
# ============================================================

def draw_targets(frame):
    """
    Draw all targets.
    """

    for target in targets:

        center = (
            int(target["x"]),
            int(target["y"])
        )

        radius = int(
            target["radius"]
        )

        if target["hit"]:

            cv2.circle(
                frame,
                center,
                radius,
                GREEN,
                -1
            )

        else:

            cv2.circle(
                frame,
                center,
                radius,
                RED,
                3
            )

            cv2.circle(
                frame,
                center,
                6,
                RED,
                -1
            )


# ============================================================
# DRAW HAND
# ============================================================

def draw_hand(frame, landmarks):
    """
    Draw hand landmarks manually.

    This avoids depending on older MediaPipe drawing APIs.
    """

    height, width = frame.shape[:2]

    points = []

    for landmark in landmarks:

        x = int(
            landmark.x * width
        )

        y = int(
            landmark.y * height
        )

        points.append((x, y))

        cv2.circle(
            frame,
            (x, y),
            3,
            GREEN,
            -1
        )

    connections = [
        (0, 1),
        (1, 2),
        (2, 3),
        (3, 4),

        (0, 5),
        (5, 6),
        (6, 7),
        (7, 8),

        (5, 9),
        (9, 10),
        (10, 11),
        (11, 12),

        (9, 13),
        (13, 14),
        (14, 15),
        (15, 16),

        (13, 17),
        (17, 18),
        (18, 19),
        (19, 20),

        (0, 17),
    ]

    for start, end in connections:

        cv2.line(
            frame,
            points[start],
            points[end],
            GREEN,
            2
        )


# ============================================================
# VISUAL EFFECTS
# ============================================================

def draw_effects(frame, current_time):

    global tracers
    global muzzle_flashes
    global explosions
    global combo_messages

    # --------------------------------------------------------
    # TRACERS
    # --------------------------------------------------------

    active_tracers = []

    for tracer in tracers:

        age = (
            current_time
            - tracer["created"]
        )

        if age >= TRACER_LIFETIME:
            continue

        progress = (
            age / TRACER_LIFETIME
        )

        thickness = max(
            1,
            int(8 * (1 - progress))
        )

        cv2.line(
            frame,
            tracer["start"],
            tracer["end"],
            YELLOW,
            thickness
        )

        active_tracers.append(
            tracer
        )

    tracers = active_tracers

    # --------------------------------------------------------
    # MUZZLE FLASH
    # --------------------------------------------------------

    active_flashes = []

    for flash in muzzle_flashes:

        age = (
            current_time
            - flash["created"]
        )

        if age >= FLASH_LIFETIME:
            continue

        progress = (
            age / FLASH_LIFETIME
        )

        radius = int(
            8 + progress * 20
        )

        cv2.circle(
            frame,
            (
                flash["x"],
                flash["y"]
            ),
            radius,
            YELLOW,
            2
        )

        active_flashes.append(
            flash
        )

    muzzle_flashes = active_flashes

    # --------------------------------------------------------
    # EXPLOSIONS
    # --------------------------------------------------------

    active_explosions = []

    for explosion in explosions:

        age = (
            current_time
            - explosion["created"]
        )

        if age >= EXPLOSION_LIFETIME:
            continue

        progress = (
            age / EXPLOSION_LIFETIME
        )

        radius = int(
            10 + progress * 50
        )

        thickness = max(
            1,
            int(6 * (1 - progress))
        )

        cv2.circle(
            frame,
            (
                int(explosion["x"]),
                int(explosion["y"])
            ),
            radius,
            YELLOW,
            thickness
        )

        active_explosions.append(
            explosion
        )

    explosions = active_explosions

    # --------------------------------------------------------
    # COMBO / STATUS MESSAGE
    # --------------------------------------------------------

    active_messages = []

    height, width = frame.shape[:2]

    for message in combo_messages:

        age = (
            current_time
            - message["created"]
        )

        if age >= COMBO_LIFETIME:
            continue

        y = 110 - int(
            age * 40
        )

        cv2.putText(
            frame,
            message["text"],
            (
                width // 2 - 70,
                y
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            YELLOW,
            3
        )

        active_messages.append(
            message
        )

    combo_messages = active_messages


# ============================================================
# HUD
# ============================================================

def draw_hud(
    frame,
    remaining_time
):
    """
    Draw score, ammunition, accuracy and time.
    """

    height, width = frame.shape[:2]

    accuracy = (
        hits / shots * 100
        if shots > 0
        else 0.0
    )

    cv2.putText(
        frame,
        f"Score: {score}",
        (30, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        WHITE,
        2
    )

    cv2.putText(
        frame,
        f"Shots: {shots}",
        (30, 75),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        WHITE,
        2
    )

    cv2.putText(
        frame,
        f"Accuracy: {accuracy:.1f}%",
        (30, 110),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        WHITE,
        2
    )

    cv2.putText(
        frame,
        f"Ammo: {ammo}/{config.MAGAZINE_SIZE}",
        (width - 240, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        WHITE,
        2
    )

    cv2.putText(
        frame,
        f"Time: {int(remaining_time)}",
        (width - 180, 75),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        WHITE,
        2
    )


# ============================================================
# MENU
# ============================================================

def draw_menu(frame):
    """
    Draw the main menu.
    """

    height, width = frame.shape[:2]

    overlay = frame.copy()

    cv2.rectangle(
        overlay,
        (0, 0),
        (width, height),
        BLACK,
        -1
    )

    frame = cv2.addWeighted(
        overlay,
        0.55,
        frame,
        0.45,
        0
    )

    cv2.putText(
        frame,
        "FINGER GUN DETECTOR",
        (
            width // 2 - 260,
            height // 2 - 70
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.2,
        CYAN,
        3
    )

    cv2.putText(
        frame,
        "Press SPACE to start",
        (
            width // 2 - 170,
            height // 2
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.9,
        WHITE,
        2
    )

    cv2.putText(
        frame,
        f"High Score: {high_score}",
        (
            width // 2 - 120,
            height // 2 + 45
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        GREEN,
        2
    )

    cv2.putText(
        frame,
        "Q = Quit",
        (
            width // 2 - 50,
            height // 2 + 90
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        WHITE,
        1
    )

    return frame


# ============================================================
# GAME OVER SCREEN
# ============================================================

def draw_game_over(frame):
    """
    Draw game-over screen.
    """

    height, width = frame.shape[:2]

    accuracy = (
        hits / shots * 100
        if shots > 0
        else 0.0
    )

    overlay = frame.copy()

    cv2.rectangle(
        overlay,
        (0, 0),
        (width, height),
        BLACK,
        -1
    )

    frame = cv2.addWeighted(
        overlay,
        0.65,
        frame,
        0.35,
        0
    )

    cv2.putText(
        frame,
        "GAME OVER",
        (
            width // 2 - 150,
            height // 2 - 80
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.4,
        RED,
        3
    )

    cv2.putText(
        frame,
        f"Score: {score}",
        (
            width // 2 - 80,
            height // 2 - 20
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.9,
        WHITE,
        2
    )

    cv2.putText(
        frame,
        f"Accuracy: {accuracy:.1f}%",
        (
            width // 2 - 120,
            height // 2 + 25
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        CYAN,
        2
    )

    cv2.putText(
        frame,
        f"High Score: {high_score}",
        (
            width // 2 - 110,
            height // 2 + 70
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        YELLOW,
        2
    )

    cv2.putText(
        frame,
        "R = Restart     Q = Quit",
        (
            width // 2 - 150,
            height // 2 + 125
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        WHITE,
        2
    )

    return frame


# ============================================================
# CAMERA
# ============================================================

def open_camera():
    """
    Open webcam.
    """

    camera = cv2.VideoCapture(
        config.CAMERA_INDEX
    )

    if not camera.isOpened():

        print()
        print("ERROR: Could not open webcam.")
        print()
        print("Possible solutions:")
        print("1. Check that your webcam is connected.")
        print("2. Close other applications using the camera.")
        print("3. Try CAMERA_INDEX = 1 in config.py.")
        print()

        return None

    camera.set(
        cv2.CAP_PROP_FRAME_WIDTH,
        1280
    )

    camera.set(
        cv2.CAP_PROP_FRAME_HEIGHT,
        720
    )

    return camera


# ============================================================
# PROCESS HANDS
# ============================================================

def process_hands(
    frame,
    result,
    current_time
):
    """
    Process detected hands.

    Returns:
        finger_gun_detected
        open_palm_detected
        gun_landmarks
    """

    height, width = frame.shape[:2]

    finger_gun_detected = False
    open_palm_detected = False

    gun_landmarks = None

    if not result.hand_landmarks:
        return (
            False,
            False,
            None
        )

    for landmarks in result.hand_landmarks:

        draw_hand(
            frame,
            landmarks
        )

        gun_pose = is_finger_gun(
            landmarks
        )

        palm_pose = is_open_palm(
            landmarks
        )

        if palm_pose:
            open_palm_detected = True

        if gun_pose:
            finger_gun_detected = True
            gun_landmarks = landmarks

    # --------------------------------------------------------
    # RELOAD
    # --------------------------------------------------------

    if open_palm_detected:
        reload_weapon(current_time)

    # --------------------------------------------------------
    # SHOOTING
    # --------------------------------------------------------

    if gun_landmarks is not None:

        thumb_y = gun_landmarks[4].y

        previous_y = previous_thumb_y.get(
            "gun_hand"
        )

        if previous_y is not None:

            thumb_movement = (
                thumb_y - previous_y
            )

            # Thumb moving downward acts as trigger.
            if thumb_movement > 0.025:

                shoot(
                    gun_landmarks,
                    width,
                    height,
                    current_time
                )

        previous_thumb_y["gun_hand"] = thumb_y

    else:

        previous_thumb_y["gun_hand"] = None

    return (
        finger_gun_detected,
        open_palm_detected,
        gun_landmarks
    )


# ============================================================
# MAIN LOOP
# ============================================================

def main():

    global game_state
    global high_score

    high_score = load_high_score()

    camera = open_camera()

    if camera is None:
        return

    print()
    print("========================================")
    print("       FINGER GUN DETECTOR")
    print("========================================")
    print()
    print("SPACE -> Start game")
    print("R     -> Restart after game over")
    print("Q     -> Quit")
    print()
    print("Show your index finger like a gun.")
    print("Move your thumb downward to shoot.")
    print("Open your palm to reload.")
    print()

    try:

        while True:

            success, frame = camera.read()

            if not success:
                print("Camera frame could not be read.")
                break

            # Mirror the webcam image.
            frame = cv2.flip(
                frame,
                1
            )

            height, width = frame.shape[:2]

            current_time = time.monotonic()

            # ------------------------------------------------
            # MENU
            # ------------------------------------------------

            if game_state == STATE_MENU:

                display = draw_menu(
                    frame
                )

                cv2.imshow(
                    WINDOW_NAME,
                    display
                )

                key = cv2.waitKey(1) & 0xFF

                if key == ord("q"):
                    break

                if key == ord(" "):

                    reset_game(
                        width,
                        height
                    )

                    game_state = STATE_PLAYING

                continue

            # ------------------------------------------------
            # GAME TIMER
            # ------------------------------------------------

            elapsed = (
                current_time
                - game_start_time
            )

            remaining_time = max(
                0,
                config.GAME_DURATION - elapsed
            )

            if (
                game_state == STATE_PLAYING
                and remaining_time <= 0
            ):

                if score > high_score:

                    high_score = score

                    save_high_score(
                        high_score
                    )

                game_state = STATE_GAME_OVER

            # ------------------------------------------------
            # HAND DETECTION
            # ------------------------------------------------

            if game_state == STATE_PLAYING:

                rgb = cv2.cvtColor(
                    frame,
                    cv2.COLOR_BGR2RGB
                )

                image = mp.Image(
                    image_format=mp.ImageFormat.SRGB,
                    data=rgb
                )

                result = hand_landmarker.detect(
                    image
                )

                (
                    gun_detected,
                    palm_detected,
                    gun_landmarks,
                ) = process_hands(
                    frame,
                    result,
                    current_time
                )

                # ------------------------------------------------
                # NO HAND MESSAGE
                # ------------------------------------------------

                if not result.hand_landmarks:

                    cv2.putText(
                        frame,
                        "SHOW YOUR HAND",
                        (30, 150),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.8,
                        RED,
                        2
                    )

                elif not gun_detected:

                    cv2.putText(
                        frame,
                        "MAKE A FINGER GUN",
                        (30, 150),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        YELLOW,
                        2
                    )

                # ------------------------------------------------
                # UPDATE GAME
                # ------------------------------------------------

                update_targets(
                    width,
                    height,
                    current_time
                )

                draw_targets(
                    frame
                )

                draw_effects(
                    frame,
                    current_time
                )

                draw_hud(
                    frame,
                    remaining_time
                )

            # ------------------------------------------------
            # GAME OVER
            # ------------------------------------------------

            elif game_state == STATE_GAME_OVER:

                frame = draw_game_over(
                    frame
                )

            # ------------------------------------------------
            # SHOW FRAME
            # ------------------------------------------------

            cv2.imshow(
                WINDOW_NAME,
                frame
            )

            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):
                break

            if (
                key == ord("r")
                and game_state == STATE_GAME_OVER
            ):

                game_state = STATE_MENU

    finally:

        camera.release()

        cv2.destroyAllWindows()

        hand_landmarker.close()


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()