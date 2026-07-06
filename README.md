# FingerFall

FingerFall is a simple webcam-based game built with OpenCV and MediaPipe. The goal is to catch falling colored balls with your finger while avoiding bombs. Each successful catch increases your score, and hitting a bomb ends the game.

## Features

- Real-time hand tracking using MediaPipe
- Falling ball and bomb gameplay
- Score tracking with a simple HUD
- Restart and quit controls
- Automatic download of the hand landmark model on first run

## Requirements

- Python 3.9+
- A working webcam
- Internet access for the first-time model download

## Installation

1. Clone the repository
   ```bash
   git clone https://github.com/Ryzuuuu/FingerFall.git
   cd FingerFall
   ```

2. Create and activate a virtual environment
   ```bash
   python -m venv .venv
   .\.venv\Scripts\activate
   ```

3. Install the dependencies
   ```bash
   pip install -r requirements.txt
   ```

4. Run the game
   ```bash
   python ball_game.py
   ```

## Controls

- Q: Quit the game
- R: Restart after a game over

## How It Works

The game reads frames from your webcam, detects your hand with MediaPipe, and uses the index finger position as the interaction point. Balls increase your score when caught, while bombs end the game.

## Project Files

- ball_game.py: Main game logic and rendering
- hand_landmarker.task: MediaPipe hand landmark model file (downloaded automatically if missing)

## Notes

- The first launch may take a few moments while the hand model is downloaded.
- Make sure your camera permissions are enabled for the application to work properly.
