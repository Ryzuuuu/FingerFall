"""FingerFall: catch falling balls with your index finger and dodge the bombs.

Run with ``python ball_game.py``. Press R to restart after a game over and Q to quit.
"""

import os
import random
import sys
import time
import urllib.error
import urllib.request

import cv2
import mediapipe as mp
from mediapipe.tasks import python as mpp
from mediapipe.tasks.python import vision

MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/hand_landmarker/"
    "hand_landmarker/float16/1/hand_landmarker.task"
)
MODEL_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "hand_landmarker.task"
)
WINDOW_NAME = "FingerFall"

INDEX_FINGER_TIP = 8  # MediaPipe hand landmark index
BALL_SCORE = 10
MISS_PENALTY = 8
BALL_SPAWN_SECONDS = 1.2
BOMB_SPAWN_SECONDS = 3.0

FONT = cv2.FONT_HERSHEY_SIMPLEX


def ensure_model():
    """Download the hand landmark model on first run."""
    if os.path.exists(MODEL_PATH):
        return
    print("Downloading hand model (~8 MB)...")
    partial_path = MODEL_PATH + ".part"
    try:
        urllib.request.urlretrieve(MODEL_URL, partial_path)
    except (urllib.error.URLError, OSError) as exc:
        sys.exit(f"Could not download the hand model: {exc}")
    os.replace(partial_path, MODEL_PATH)


def new_ball(w):
    return {
        "x": random.randint(40, w - 40),
        "y": 0,
        "r": 35,
        "speed": random.randint(10, 20),
        "color": tuple(random.randint(80, 255) for _ in range(3)),
    }


def new_bomb(w):
    return {
        "x": random.randint(40, w - 40),
        "y": 0,
        "r": 30,
        "speed": random.randint(6, 11),
    }


def reset():
    """Return a fresh game state: balls, bombs, score, spawn timers, game_over."""
    return [], [], 0, time.time(), time.time(), False


def touches(finger, obj):
    """True if the fingertip (x, y) is inside the object's circle."""
    if finger is None:
        return False
    fx, fy = finger
    return ((fx - obj["x"]) ** 2 + (fy - obj["y"]) ** 2) ** 0.5 < obj["r"]


def find_fingertip(detector, frame):
    """Return the index fingertip position in pixels, or None if no hand is visible."""
    h, w = frame.shape[:2]
    image = mp.Image(
        image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    )
    result = detector.detect(image)
    if not result.hand_landmarks:
        return None
    tip = result.hand_landmarks[0][INDEX_FINGER_TIP]
    return int(tip.x * w), int(tip.y * h)


def update_balls(frame, balls, score, finger):
    """Move balls, award catches, penalise misses and draw the survivors."""
    h = frame.shape[0]
    alive = []
    for ball in balls:
        ball["y"] += ball["speed"]
        if touches(finger, ball):
            score += BALL_SCORE
        elif ball["y"] > h:
            score -= MISS_PENALTY
        else:
            center = (ball["x"], ball["y"])
            cv2.circle(frame, center, ball["r"], ball["color"], -1)
            cv2.circle(frame, center, ball["r"], (255, 255, 255), 2)
            alive.append(ball)
    return alive, score


def update_bombs(frame, bombs, finger):
    """Move bombs and draw the survivors. Returns (bombs, game_over)."""
    h = frame.shape[0]
    alive = []
    for bomb in bombs:
        bomb["y"] += bomb["speed"]
        if touches(finger, bomb):
            return bombs, True
        if bomb["y"] <= h:
            x, y, r = bomb["x"], bomb["y"], bomb["r"]
            cv2.circle(frame, (x, y), r, (30, 30, 30), -1)
            cv2.circle(frame, (x, y), r, (0, 0, 220), 2)
            off = r // 2
            cv2.line(frame, (x - off, y - off), (x + off, y + off), (0, 0, 220), 3)
            cv2.line(frame, (x + off, y - off), (x - off, y + off), (0, 0, 220), 3)
            alive.append(bomb)
    return alive, False


def put_centered(frame, text, y, scale, color, thickness):
    """Draw text horizontally centred on the frame."""
    (text_w, _), _ = cv2.getTextSize(text, FONT, scale, thickness)
    cv2.putText(
        frame, text, ((frame.shape[1] - text_w) // 2, y), FONT, scale, color, thickness
    )


def draw_game_over(frame, score):
    h = frame.shape[0]
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (frame.shape[1], h), (0, 0, 0), -1)
    frame = cv2.addWeighted(overlay, 0.6, frame, 0.4, 0)
    put_centered(frame, "GAME OVER", h // 2 - 60, 2, (0, 60, 255), 6)
    put_centered(frame, f"Score: {score}", h // 2, 1.4, (255, 255, 255), 3)
    put_centered(frame, "R - Restart   Q - Quit", h // 2 + 65, 0.9, (200, 200, 200), 2)
    return frame


def draw_hud(frame, score):
    h = frame.shape[0]
    color = (0, 255, 100) if score >= 0 else (0, 80, 255)
    cv2.putText(frame, f"Score: {score}", (10, 45), FONT, 1.4, (0, 0, 0), 5)
    cv2.putText(frame, f"Score: {score}", (10, 45), FONT, 1.4, color, 3)
    cv2.putText(
        frame,
        f"+{BALL_SCORE} catch   -{MISS_PENALTY} miss   bomb = game over   Q quit",
        (10, h - 15),
        FONT,
        0.5,
        (200, 200, 200),
        1,
    )


def main():
    ensure_model()
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        sys.exit(
            "Could not open the webcam. Check that it is connected and not in use."
        )

    options = vision.HandLandmarkerOptions(
        base_options=mpp.BaseOptions(model_asset_path=MODEL_PATH), num_hands=1
    )
    balls, bombs, score, last_spawn, last_bomb, game_over = reset()

    with vision.HandLandmarker.create_from_options(options) as detector:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frame = cv2.flip(frame, 1)
            w = frame.shape[1]

            if game_over:
                cv2.imshow(WINDOW_NAME, draw_game_over(frame, score))
                key = cv2.waitKey(1) & 0xFF
                if key == ord("r"):
                    balls, bombs, score, last_spawn, last_bomb, game_over = reset()
                elif key == ord("q"):
                    break
                continue

            now = time.time()
            if now - last_spawn > BALL_SPAWN_SECONDS:
                balls.append(new_ball(w))
                last_spawn = now
            if now - last_bomb > BOMB_SPAWN_SECONDS:
                bombs.append(new_bomb(w))
                last_bomb = now

            finger = find_fingertip(detector, frame)
            if finger is not None:
                cv2.circle(frame, finger, 18, (0, 255, 100), -1)

            balls, score = update_balls(frame, balls, score, finger)
            bombs, game_over = update_bombs(frame, bombs, finger)

            draw_hud(frame, score)
            cv2.imshow(WINDOW_NAME, frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
