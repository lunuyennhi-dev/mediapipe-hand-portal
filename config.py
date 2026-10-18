"""
Configuration and constants for MediaPipe Hand AR Multi-Portal System.
"""
import os

# Base paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "hand_landmarker.task")
SCREENSHOTS_DIR = os.path.join(BASE_DIR, "screenshots")
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

MODEL_URL = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task"

# Camera Settings
CAMERA_INDEX = 0
FRAME_WIDTH = 1280
FRAME_HEIGHT = 720
FPS = 30

# One Euro Filter parameters for ultra-smooth, zero-lag tracking
ONE_EURO_MIN_CUTOFF = 1.0  # Hz (Smoothness when holding still)
ONE_EURO_BETA = 0.012      # Speed coefficient (Zero lag when moving fast)
ONE_EURO_D_CUTOFF = 1.0    # Derivative cutoff frequency

# Gesture Pinch Thresholds (Normalized to palm scale)
PINCH_THRESHOLD_NORM = 0.28   # Normalized distance to trigger touch
RELEASE_THRESHOLD_NORM = 0.40 # Hysteresis distance to reset touch
GESTURE_COOLDOWN_SEC = 0.40    # Cooldown between filter switches

# Snapshot Countdown & Touch-Hold Protection
COUNTDOWN_SECONDS = 3.0       # 3-second countdown before capturing photo
TOUCH_HOLD_SECONDS = 0.40      # Hold Index & Thumb touch for 0.40s to prevent accidental trigger

# Smooth Filter Cross-fade Transition
FILTER_TRANSITION_SEC = 0.25  # Duration of smooth cross-fade when switching filters

# Clean UI Colors (BGR)
COLOR_NEON_YELLOW = (0, 240, 255)
COLOR_NEON_CYAN = (255, 255, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_NEON_GREEN = (50, 255, 50)

# List of 7 high-aesthetic filters (No lightning, no glitches)
FILTER_NAMES = [
    "THERMAL",        # 1. Thermal camera colormap (ColorMap Jet)
    "SKETCH",         # 2. Artistic pencil line art
    "PIXELATE",       # 3. 8-bit retro arcade
    "NIGHT_VISION",   # 4. Green night vision phosphor
    "X_RAY",          # 5. X-Ray negative bone contrast
    "VINTAGE_SEPIA",  # 6. Warm sepia film with vignette
    "MATRIX"          # 7. Matrix green digital code
]
