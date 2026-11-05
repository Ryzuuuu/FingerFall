# FingerFall

A webcam game you play with your hand. Colored balls fall from the top of the screen: touch them with your index finger to score, and stay away from the bombs. Hand tracking runs in real time with OpenCV and MediaPipe, so there is no controller, mouse or keyboard needed to play.

<!-- Replace with a screen recording once available: ![FingerFall demo](docs/demo.gif) -->
> **Demo GIF:** coming soon.

## How to Play

1. Run the game and hold up one hand in front of the webcam. A green dot follows your index fingertip.
2. Touch falling balls with the dot to catch them.
3. Avoid the black bombs marked with a red X. Touching one ends the game.

| Event | Score |
| --- | --- |
| Catch a ball | +10 |
| Let a ball fall off the screen | -8 |
| Touch a bomb | Game over |

Controls: `Q` quits at any time, and `R` restarts after a game over.

## How It Works

1. **Capture:** OpenCV reads frames from the default webcam and mirrors them so movement feels natural.
2. **Hand tracking:** each frame is converted to RGB and passed to MediaPipe's `HandLandmarker` (the Tasks API), which returns 21 landmarks for the detected hand. Landmark 8, the index fingertip, is scaled to pixel coordinates and used as the pointer.
3. **Game loop:** balls (every 1.2 s) and bombs (every 3 s) spawn at a random x position and fall at a random speed. Collisions are a circle-vs-point distance check between the fingertip and each object.
4. **Rendering:** balls, bombs, the fingertip marker, the score HUD and the game over overlay are all drawn onto the frame with OpenCV and shown in a window.

Object speeds are measured in pixels per frame, so the game feels faster on a higher-FPS camera.

## Tech Stack

- Python 3.9+
- [OpenCV](https://opencv.org/) for webcam capture and drawing
- [MediaPipe](https://ai.google.dev/edge/mediapipe) Hand Landmarker for hand tracking

## Setup

You need Python 3.9 or newer, a webcam, and an internet connection for the first run (the hand model is downloaded once).

1. Clone the repository
   ```bash
   git clone https://github.com/Ryzuuuu/FingerFall.git
   cd FingerFall
   ```

2. Create and activate a virtual environment
   ```bash
   python -m venv .venv
   ```
   Windows:
   ```bash
   .\.venv\Scripts\activate
   ```
   macOS / Linux:
   ```bash
   source .venv/bin/activate
   ```

3. Install the dependencies
   ```bash
   pip install -r requirements.txt
   ```

4. Run the game
   ```bash
   python ball_game.py
   ```

The first launch downloads `hand_landmarker.task` (about 8 MB) next to the script. It is git-ignored and reused on later runs.

## Project Structure

```
FingerFall/
├── ball_game.py       # Game logic, hand tracking and rendering
├── requirements.txt   # Python dependencies
└── README.md
```

## Customizing

Gameplay settings are constants near the top of `ball_game.py`: `BALL_SCORE`, `MISS_PENALTY`, `BALL_SPAWN_SECONDS` and `BOMB_SPAWN_SECONDS`. Ball and bomb size and speed are set in `new_ball` and `new_bomb`.

## Troubleshooting

- **"Could not open the webcam":** make sure a camera is connected, camera access is allowed for your terminal or editor, and no other app is using it. If you have several cameras, change the index in `cv2.VideoCapture(0)`.
- **"Could not download the hand model":** check your connection, or download [hand_landmarker.task](https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task) manually and place it next to `ball_game.py`.
- **The fingertip dot jitters or disappears:** use even lighting and keep your whole hand in view.
