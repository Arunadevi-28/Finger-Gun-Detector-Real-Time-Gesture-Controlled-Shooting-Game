# Finger Gun Detector

A computer-vision game that uses a webcam and **MediaPipe Hand Landmarker** to detect hand gestures and control a shooting game.

The player uses a **finger-gun gesture** to aim and shoot targets, and an **open-palm gesture** to reload the weapon.

---

## Features

* Real-time hand detection using a webcam
* MediaPipe Hand Landmarker for 21-point hand tracking
* Finger-gun gesture detection
* Open-palm gesture detection
* Gesture-based shooting
* Gesture-based reloading
* Six-round magazine
* Three moving targets
* 60-second game timer
* Score system
* Hit counter
* Shooting effects
* Reload cooldown
* High-score saving
* Keyboard controls for starting, restarting, and quitting
* Mirrored webcam display for natural interaction

---

## How the Game Works

The game uses the webcam to capture your hand.

The camera image is processed by MediaPipe, which detects the hand and provides the coordinates of 21 hand landmarks.

The program then analyzes those landmarks to determine which gesture you are making.

### Finger Gun

The finger-gun gesture is recognized when:

* The index finger is extended.
* The middle finger is folded.
* The ring finger is folded.
* The pinky finger is folded.

The finger-gun gesture is used to aim and shoot.

```text
Index   → OPEN
Middle  → CLOSED
Ring    → CLOSED
Pinky   → CLOSED

          ☝
          |
          |
       ___|
      /
     /
```

### Open Palm

The open-palm gesture is recognized when:

* The index finger is extended.
* The middle finger is extended.
* The ring finger is extended.
* The pinky finger is extended.

The open palm is used to reload the weapon.

```text
Index   → OPEN
Middle  → OPEN
Ring    → OPEN
Pinky   → OPEN

        ✋
```

---

## Game Controls

### Keyboard Controls

| Key     | Action                  |
| ------- | ----------------------- |
| `SPACE` | Start the game          |
| `R`     | Restart after game over |
| `Q`     | Quit the game           |

### Hand Controls

| Gesture    | Action        |
| ---------- | ------------- |
| Finger gun | Aim and shoot |
| Open palm  | Reload        |

---

## Game Rules

The game starts with a six-round magazine.

```text
Magazine = 6 shots
```

Every successful shot uses one round.

For example:

```text
6 / 6
↓ Shoot
5 / 6
↓ Shoot
4 / 6
```

When the magazine becomes empty, an open palm can be used to reload.

A successful target hit gives:

```text
+10 points
```

The game lasts for:

```text
60 seconds
```

At the end of the game, the final score is displayed.

If the score is higher than the previously saved high score, the high score is updated.

---

## Project Structure

```text
Finger Gun Detector/
│
├── main.py
├── config.py
├── requirements.txt
├── download_model.py
├── hand_landmarker.task
├── highscore.txt
├── .gitignore
├── README.md
│
└── venv/
```

### File Description

#### `main.py`

The main application.

It handles:

* Webcam input
* Hand detection
* Hand landmark processing
* Gesture recognition
* Finger-gun detection
* Open-palm detection
* Shooting
* Reloading
* Target generation
* Collision detection
* Score calculation
* Timer
* Game states
* High-score handling
* OpenCV display

#### `config.py`

Contains the main game configuration values.

Examples include:

* Camera index
* Game duration
* Magazine size
* Number of targets
* Target radius
* Detection confidence
* Shooting cooldown
* Reload cooldown

Keeping these values in a separate file makes it easier to modify the game without changing the main program.

#### `download_model.py`

Downloads the MediaPipe Hand Landmarker model.

The downloaded model is stored as:

```text
hand_landmarker.task
```

#### `hand_landmarker.task`

The MediaPipe Hand Landmarker model used by the application.

This file is required for hand detection.

#### `highscore.txt`

Stores the highest score achieved by the player.

If the file does not contain a valid score, the program starts with a high score of zero.

#### `requirements.txt`

Contains the Python packages required by the project.

#### `.gitignore`

Specifies files and folders that should not be committed to Git.

#### `README.md`

Project documentation.

---

# Requirements

## Hardware

You need:

* A computer running Windows, macOS, or Linux
* A working webcam
* A reasonably modern CPU
* Enough lighting for the camera to clearly see your hand

A built-in laptop webcam is sufficient.

---

## Software

The project requires:

* Python 3.12
* VS Code
* A webcam
* Internet access during initial package/model installation

Python 3.12 is recommended for the current project environment.

---

# Installation on Windows

The following instructions use the **VS Code integrated terminal**.

No separate Command Prompt window is required.

---

## 1. Open the Project

Open the project folder in VS Code:

```text
Finger Gun Detector
```

The terminal should be opened inside the project folder.

For example:

```text
C:\Users\YourName\Desktop\Finger Gun Detector>
```

---

## 2. Create a Virtual Environment

Open the VS Code integrated terminal and run:

```cmd
python -m venv venv
```

This creates a Python virtual environment named:

```text
venv
```

---

## 3. Activate the Virtual Environment

If the VS Code terminal is using **Command Prompt (CMD)**, run:

```cmd
venv\Scripts\activate
```

After activation, the terminal should show:

```text
(venv) C:\Users\YourName\Desktop\Finger Gun Detector>
```

The `(venv)` indicates that the virtual environment is active.

---

## 4. Verify Python

Run:

```cmd
python --version
```

The recommended version is:

```text
Python 3.12.x
```

You can also check which Python executable is being used:

```cmd
where python
```

The first result should point to:

```text
...\Finger Gun Detector\venv\Scripts\python.exe
```

---

# Install Dependencies

Upgrade pip:

```cmd
python -m pip install --upgrade pip
```

Then install the project dependencies:

```cmd
python -m pip install -r requirements.txt
```

This installs the required packages, including:

* OpenCV
* MediaPipe
* NumPy

---

# Download the Hand Landmarker Model

The project requires the MediaPipe model file:

```text
hand_landmarker.task
```

Run:

```cmd
python download_model.py
```

After a successful download, verify the file:

```cmd
dir hand_landmarker.task
```

The file must not be zero bytes.

You can also check its exact size using:

```cmd
python -c "from pathlib import Path; print(Path('hand_landmarker.task').stat().st_size)"
```

A valid model file should have a substantial file size.

---

# Run the Game

Once the dependencies and model have been installed, run:

```cmd
python main.py
```

The webcam window should open.

---

# Starting the Game

When the application starts, the menu is displayed.

Press:

```text
SPACE
```

to start the game.

Make sure your webcam can clearly see your hand.

---

# Playing the Game

## 1. Aim

Place your hand in front of the webcam.

Make a finger-gun gesture:

```text
☝️
```

The index finger acts as the aiming direction.

---

## 2. Shoot

While holding the finger-gun gesture, perform the shooting motion detected by the program.

The program uses the movement of the thumb to recognize the shot.

A successful shot:

```text
Finger gun
     ↓
Aiming direction
     ↓
Shoot
     ↓
Ray/target collision check
     ↓
Target hit?
```

If the shot hits a target:

```text
+10 SCORE
```

---

## 3. Reload

Show an open palm:

```text
✋
```

The program recognizes the extended fingers and reloads the magazine.

The normal magazine capacity is:

```text
6
```

So a reload changes the ammunition back to:

```text
6 / 6
```

The program includes a reload cooldown to prevent repeated reload operations while the palm remains visible.

---

# Hand Landmark Detection

MediaPipe detects 21 landmarks on a hand.

The landmarks represent important locations such as:

* Wrist
* Thumb joints
* Thumb tip
* Index finger joints
* Index fingertip
* Middle finger joints
* Middle fingertip
* Ring finger joints
* Ring fingertip
* Pinky joints
* Pinky fingertip

Conceptually:

```text
                 Finger tips
              ●     ●     ●
              │     │     │
              │     │     │
              ●     ●     ●
               \    │    /
                \   │   /
                 \  │  /
                  \ │ /
                   \|/
                   ●
                 Wrist
```

The program uses these landmark positions to determine whether individual fingers are extended or folded.

---

# Gesture Recognition

The game distinguishes between the two primary gestures.

## Finger Gun

```text
Index   = Extended
Middle  = Folded
Ring    = Folded
Pinky   = Folded
```

This represents:

```text
🔫
```

and is used for shooting.

---

## Open Palm

```text
Index   = Extended
Middle  = Extended
Ring    = Extended
Pinky   = Extended
```

This represents:

```text
✋
```

and is used for reloading.

---

# Game Architecture

The application follows this general processing pipeline:

```text
              WEBCAM
                 │
                 ▼
          Capture video frame
                 │
                 ▼
         MediaPipe Hand Landmarker
                 │
                 ▼
          21 hand landmarks
                 │
                 ▼
          Gesture recognition
                 │
          ┌──────┴──────┐
          │             │
          ▼             ▼
     Finger Gun      Open Palm
          │             │
          ▼             ▼
       Shooting       Reloading
          │
          ▼
    Target collision
          │
          ▼
       Score +10
```

---

# Game States

The application has several states.

## Menu

The initial state.

The player can press:

```text
SPACE
```

to start.

---

## Playing

The active game state.

During this state:

* The webcam is displayed.
* Hands are detected.
* Targets are displayed.
* Gestures are processed.
* The player can shoot.
* The player can reload.
* The timer counts down.
* The score is updated.

---

## Game Over

When the timer reaches zero, the game ends.

The final score is displayed.

The player can press:

```text
R
```

to restart.

---

# Configuration

The game's main settings are stored in:

```text
config.py
```

The configuration includes values such as:

```python
CAMERA_INDEX = 0
GAME_DURATION = 60
MAGAZINE_SIZE = 6
RELOAD_COOLDOWN = 1.0
SHOT_COOLDOWN = 0.35
NUMBER_OF_TARGETS = 3
TARGET_RADIUS = 30
MAX_HANDS = 2
```

These values can be changed to customize the game.

For example, changing:

```python
GAME_DURATION = 60
```

to:

```python
GAME_DURATION = 90
```

would make the game last 90 seconds.

Changing:

```python
MAGAZINE_SIZE = 6
```

to:

```python
MAGAZINE_SIZE = 10
```

would increase the magazine capacity.

---

# Camera Configuration

The default camera is:

```python
CAMERA_INDEX = 0
```

This normally corresponds to the computer's default webcam.

If the computer has multiple cameras, another camera index can be tested:

```python
CAMERA_INDEX = 1
```

or:

```python
CAMERA_INDEX = 2
```

---

# Troubleshooting

## `Unable to get file size`

If you see an error similar to:

```text
RuntimeError: Unable to get file size
```

check whether:

```text
hand_landmarker.task
```

exists and has a non-zero file size.

Run:

```cmd
dir hand_landmarker.task
```

If the file size is:

```text
0
```

download the model again:

```cmd
python download_model.py
```

---

## Webcam Does Not Open

Check that:

* The webcam is connected.
* No other application is exclusively using the webcam.
* Windows has camera permissions enabled.
* The correct camera index is selected in `config.py`.

Try:

```python
CAMERA_INDEX = 0
```

and, if necessary:

```python
CAMERA_INDEX = 1
```

---

## Hand Is Not Detected

Improve the lighting.

The camera should clearly see the hand against the background.

Avoid:

* Very dark rooms
* Strong backlighting
* Motion blur
* Hands outside the camera frame
* Objects blocking the hand

Keep your hand approximately:

```text
30–100 cm
```

from the camera and adjust according to your webcam.

---

## Finger Gun Is Not Recognized

Make sure:

* The index finger is clearly extended.
* The other fingers are clearly folded.
* The entire hand is visible.
* The hand is not too close to the edge of the frame.
* Lighting is sufficient.

Try holding the gesture steadily for a moment.

---

## Open Palm Is Not Recognized

Make sure all four main fingers are clearly extended:

```text
☝ Index
☝ Middle
☝ Ring
☝ Pinky
```

Avoid partially folded fingers.

The camera should be able to see the fingertips and finger joints.

---

## Low FPS

Possible causes include:

* High camera resolution
* Limited CPU performance
* Too many applications running simultaneously
* Poor lighting causing difficult hand detection
* Multiple hands being processed

Close unnecessary applications and make sure the webcam is not being used by another program.

---

# Running the Project Again

After the first installation, you normally only need to open the project and activate the virtual environment.

In the VS Code terminal:

```cmd
venv\Scripts\activate
```

Then run:

```cmd
python main.py
```

You do not normally need to reinstall the packages every time.

---

# Stopping the Game

Press:

```text
Q
```

while the game window is active.

This closes the application.

---

# Technologies Used

## Python

The main programming language.

## OpenCV

Used for:

* Webcam access
* Image processing
* Drawing the game interface
* Displaying frames
* Keyboard input

## MediaPipe

Used for:

* Hand detection
* Hand landmark detection
* Gesture recognition support

## NumPy

Used for numerical calculations involving:

* Coordinates
* Distances
* Vectors
* Target and hand geometry

---

# Project Workflow

The complete workflow is:

```text
1. Start application
        ↓
2. Open webcam
        ↓
3. Capture video frame
        ↓
4. Detect hand
        ↓
5. Extract 21 landmarks
        ↓
6. Analyze finger positions
        ↓
7. Identify gesture
        ↓
8. Finger gun → Shoot
        │
        └── Target hit → +10 score
        ↓
   Open palm → Reload
        ↓
9. Continue until timer reaches zero
        ↓
10. Display final score
        ↓
11. Save high score
```

---

# High Score

The highest score is stored in:

```text
highscore.txt
```

For example:

```text
120
```

If a later game produces:

```text
150
```

the high score becomes:

```text
150
```

This allows the player to compete against their previous score.

---

# Future Improvements

Possible future improvements include:

* Multiple difficulty levels
* Faster targets at higher difficulty
* Different target types
* Sound effects
* Background music
* Better shooting animation
* More advanced gesture recognition
* Accuracy statistics
* Shots-fired counter
* Accuracy percentage
* Combo system
* Leaderboards
* Customizable game duration
* Customizable magazine size
* Multiplayer mode
* More hand gestures
* Improved target movement
* Mobile or browser version

---

# Important Notes

The application depends on the MediaPipe model file:

```text
hand_landmarker.task
```

Without this model, the hand detector cannot start.

Do not replace the model with an empty file.

The virtual environment should also be activated before running the application:

```cmd
venv\Scripts\activate
```

The terminal should show:

```text
(venv)
```

before the project path.

---

# License

This project is intended for educational and demonstration purposes.

Check the licenses of the individual third-party libraries and MediaPipe model before redistributing the project or its model files.

---

# Summary

**Finger Gun Detector** combines computer vision and interactive gameplay.

The webcam provides the video.

OpenCV handles the camera and game display.

MediaPipe detects the hand and its 21 landmarks.

The program interprets those landmarks as gestures.

```text
✋ Open Palm
     ↓
   Reload

☝️ Finger Gun
     ↓
    Aim
     ↓
   Shoot
     ↓
Target Hit
     ↓
 +10 Score
```

The result is a webcam-controlled shooting game where the player's hand becomes the game controller.