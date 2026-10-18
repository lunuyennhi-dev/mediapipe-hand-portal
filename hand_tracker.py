"""
Hand Tracker Module with One Euro Filter 2D.
High-accuracy tracking for Index, Middle, and Thumb.
Gestures:
  - Middle touches Thumb (Pinch Middle & Thumb): Switch filter
  - Index touches Thumb (Pinch Index & Thumb): 3-second countdown snapshot
"""
import os
import time
import urllib.request
import numpy as np
import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import config

class OneEuroFilter2D:
    """Adaptive low-pass filter: zero jitter when holding still, zero lag when moving."""
    def __init__(self, min_cutoff=config.ONE_EURO_MIN_CUTOFF, beta=config.ONE_EURO_BETA, d_cutoff=config.ONE_EURO_D_CUTOFF):
        self.min_cutoff = min_cutoff
        self.beta = beta
        self.d_cutoff = d_cutoff
        self.x_prev = None
        self.dx_prev = None
        self.t_prev = None

    def filter(self, x, t):
        x = np.array(x, dtype=np.float32)
        if self.x_prev is None:
            self.x_prev = x
            self.dx_prev = np.zeros_like(x)
            self.t_prev = t
            return x

        dt = max(1e-4, t - self.t_prev)
        self.t_prev = t

        dx = (x - self.x_prev) / dt
        edx = self._alpha(dt, self.d_cutoff) * dx + (1.0 - self._alpha(dt, self.d_cutoff)) * self.dx_prev
        self.dx_prev = edx

        speed = float(np.linalg.norm(edx))
        cutoff = self.min_cutoff + self.beta * speed
        alpha = self._alpha(dt, cutoff)
        x_filtered = alpha * x + (1.0 - alpha) * self.x_prev
        self.x_prev = x_filtered
        return x_filtered

    def _alpha(self, dt, cutoff):
        tau = 1.0 / (2.0 * np.pi * cutoff)
        return 1.0 / (1.0 + tau / dt)

    def reset(self):
        self.x_prev = None
        self.dx_prev = None
        self.t_prev = None


class HandTracker:
    def __init__(self, model_path: str = config.MODEL_PATH, max_hands: int = 2):
        self.model_path = model_path
        self.max_hands = max_hands
        self._ensure_model_exists()
        
        base_options = python.BaseOptions(model_asset_path=self.model_path)
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.IMAGE,
            num_hands=self.max_hands,
            min_hand_detection_confidence=0.55,
            min_hand_presence_confidence=0.55,
            min_tracking_confidence=0.55
        )
        self.detector = vision.HandLandmarker.create_from_options(options)

        # Filters for each hand (0: Left, 1: Right) for key landmarks [0, 2, 4, 6, 8, 10, 12, 17]
        self.hand_filters = {
            0: {idx: OneEuroFilter2D() for idx in [0, 2, 4, 6, 8, 10, 12, 17]},
            1: {idx: OneEuroFilter2D() for idx in [0, 2, 4, 6, 8, 10, 12, 17]}
        }

        # Filter switch debounce (Middle & Thumb pinch)
        self.last_switch_time = 0.0
        self.switch_pinch_active = False

        # Snapshot pinch hold timer (Index & Thumb pinch held for TOUCH_HOLD_SECONDS)
        self.snap_hold_time = 0.0
        self.last_frame_time = time.time()
        self.last_snap_trigger_time = 0.0

    def _ensure_model_exists(self):
        if not os.path.exists(self.model_path):
            print(f"[HandTracker] Downloading MediaPipe model from {config.MODEL_URL}...")
            urllib.request.urlretrieve(config.MODEL_URL, self.model_path)
            print(f"[HandTracker] Model saved to {self.model_path}")

    def process_frame(self, frame_bgr: np.ndarray):
        """
        Processes BGR frame with One Euro Filter smoothing and extracts key landmarks.
        """
        curr_t = time.time()
        dt = max(0.001, curr_t - self.last_frame_time)
        self.last_frame_time = curr_t

        h, w = frame_bgr.shape[:2]
        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
        
        result = self.detector.detect(mp_image)
        hands_data = []

        if not result.hand_landmarks:
            for h_id in self.hand_filters:
                for f in self.hand_filters[h_id].values():
                    f.reset()
            self.snap_hold_time = 0.0
            return hands_data

        # Parse detected hands
        raw_hands = []
        for landmarks in result.hand_landmarks:
            px_pts = np.array([[lm.x * w, lm.y * h] for lm in landmarks], dtype=np.float32)
            wrist_x = px_pts[0][0]
            raw_hands.append({'pts': px_pts, 'wrist_x': wrist_x})

        # Sort hands strictly left-to-right on screen (by wrist x)
        raw_hands.sort(key=lambda item: item['wrist_x'])

        for hand_idx, r_hand in enumerate(raw_hands[:2]):
            px_pts = r_hand['pts']
            filters = self.hand_filters[hand_idx]

            # Smooth key landmarks with One Euro Filter
            wrist = filters[0].filter(px_pts[0], curr_t)
            thumb_mcp = filters[2].filter(px_pts[2], curr_t)
            thumb_tip = filters[4].filter(px_pts[4], curr_t)
            index_pip = filters[6].filter(px_pts[6], curr_t)
            index_tip = filters[8].filter(px_pts[8], curr_t)
            middle_pip = filters[10].filter(px_pts[10], curr_t)
            middle_tip = filters[12].filter(px_pts[12], curr_t)
            pinky_mcp = filters[17].filter(px_pts[17], curr_t)

            # Invariant scale: distance between wrist (0) and middle MCP (9)
            scale_ref = max(1.0, float(np.linalg.norm(px_pts[9] - px_pts[0])))

            # Accurate finger extension checks
            is_index_ext = np.linalg.norm(index_tip - wrist) > np.linalg.norm(index_pip - wrist) * 1.08
            is_middle_ext = np.linalg.norm(middle_tip - wrist) > np.linalg.norm(middle_pip - wrist) * 1.08
            is_thumb_ext = np.linalg.norm(thumb_tip - pinky_mcp) > np.linalg.norm(thumb_mcp - pinky_mcp) * 1.08

            # Normalized Euclidean distances for touches
            dist_middle_thumb = np.linalg.norm(middle_tip - thumb_tip) / scale_ref
            dist_index_thumb = np.linalg.norm(index_tip - thumb_tip) / scale_ref

            hands_data.append({
                'hand_idx': hand_idx,
                'wrist': tuple(wrist.astype(np.int32)),
                'thumb': tuple(thumb_tip.astype(np.int32)),
                'index': tuple(index_tip.astype(np.int32)),
                'middle': tuple(middle_tip.astype(np.int32)),
                'scale_ref': scale_ref,
                'is_index_ext': bool(is_index_ext),
                'is_middle_ext': bool(is_middle_ext),
                'is_thumb_ext': bool(is_thumb_ext),
                'dist_middle_thumb': float(dist_middle_thumb),
                'dist_index_thumb': float(dist_index_thumb),
                'is_middle_thumb_touch': bool(dist_middle_thumb < config.PINCH_THRESHOLD_NORM),
                'is_index_thumb_touch': bool(dist_index_thumb < config.PINCH_THRESHOLD_NORM)
            })

        # Update snapshot hold timer
        self._update_snap_hold(hands_data, dt)

        return hands_data

    def _update_snap_hold(self, hands_data, dt: float):
        # Touching Index & Thumb
        is_pinching = any(h['is_index_thumb_touch'] for h in hands_data)
        if is_pinching:
            self.snap_hold_time += dt
        else:
            self.snap_hold_time = max(0.0, self.snap_hold_time - dt * 2.5)

    def check_filter_switch_gesture(self, hands_data) -> int:
        """
        Rule: Switch filter when Middle touches Thumb (Ngón giữa chạm ngón cái).
        """
        curr_t = time.time()
        if (curr_t - self.last_switch_time) < config.GESTURE_COOLDOWN_SEC:
            return 0

        is_pinching = any(h['is_middle_thumb_touch'] for h in hands_data)

        if is_pinching and not self.switch_pinch_active:
            self.last_switch_time = curr_t
            self.switch_pinch_active = True
            return 1
        elif not is_pinching:
            all_released = all(h['dist_middle_thumb'] > config.RELEASE_THRESHOLD_NORM for h in hands_data)
            if all_released:
                self.switch_pinch_active = False

        return 0

    def check_snapshot_gesture(self, hands_data) -> tuple:
        """
        Rule: Start 3-second countdown when Index touches Thumb (holds for TOUCH_HOLD_SECONDS).
        Returns (is_triggered, hold_progress, pinch_center).
        """
        curr_t = time.time()
        hold_target = config.TOUCH_HOLD_SECONDS
        progress = min(1.0, self.snap_hold_time / hold_target)

        pinch_center = None
        for h in hands_data:
            if h['is_index_thumb_touch']:
                pinch_center = (
                    (h['index'][0] + h['thumb'][0]) // 2,
                    (h['index'][1] + h['thumb'][1]) // 2
                )
                break

        if (curr_t - self.last_snap_trigger_time) < 2.0:
            return False, 0.0, pinch_center

        if self.snap_hold_time >= hold_target:
            self.snap_hold_time = 0.0
            self.last_snap_trigger_time = curr_t
            return True, 1.0, pinch_center

        return False, progress, pinch_center

    def close(self):
        if hasattr(self, 'detector') and self.detector:
            self.detector.close()
