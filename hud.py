"""
Minimalist & Clean AR HUD Module.
Renders countdown timer, touch-hold progress ring, notifications, and camera shutter flash.
Borders, points, and floating labels on frames are completely hidden.
"""
import time
import math
import cv2
import numpy as np
import config

class HUDOverlay:
    def __init__(self):
        self.notification_text = ""
        self.notification_expiry = 0.0
        self.flash_alpha = 0.0

    def trigger_notification(self, text: str, duration: float = 1.0):
        """Displays a momentary sleek toast notification."""
        self.notification_text = text
        self.notification_expiry = time.time() + duration

    def trigger_flash(self):
        """Triggers a camera shutter white flash animation."""
        self.flash_alpha = 1.0

    def draw_touch_hold_progress(self, image: np.ndarray, progress: float, center: tuple = None):
        """
        Draws an elegant mini progress ring around the pinching fingertips
        while holding Index & Thumb before starting the 3s countdown.
        """
        if progress < 0.10:
            return

        h, w = image.shape[:2]
        if center is None or not (0 <= center[0] < w and 0 <= center[1] < h):
            cx, cy = w // 2, h - 50
        else:
            cx, cy = int(center[0]), int(center[1])

        radius = 24
        angle_deg = int(progress * 360)
        cv2.circle(image, (cx, cy), radius, (40, 40, 40), 3, cv2.LINE_AA)
        cv2.ellipse(image, (cx, cy), (radius, radius), -90, 0, angle_deg, config.COLOR_NEON_YELLOW, 3, cv2.LINE_AA)

    def draw_countdown_overlay(self, image: np.ndarray, time_left: float, total_time: float = config.COUNTDOWN_SECONDS):
        """
        Draws a large cyber countdown ring in the center of the screen with time remaining.
        """
        h, w = image.shape[:2]
        cx, cy = w // 2, h // 2

        fraction = max(0.0, min(1.0, (total_time - time_left) / total_time))
        angle_deg = int(fraction * 360)

        # Outer ring
        radius = 75
        cv2.circle(image, (cx, cy), radius + 6, (30, 30, 30), 6, cv2.LINE_AA)
        cv2.ellipse(image, (cx, cy), (radius + 6, radius + 6), -90, 0, angle_deg, config.COLOR_NEON_YELLOW, 6, cv2.LINE_AA)
        
        # Center circle backdrop
        overlay = image.copy()
        cv2.circle(overlay, (cx, cy), radius, (15, 15, 15), -1)
        cv2.addWeighted(overlay, 0.65, image, 0.35, 0, dst=image)
        cv2.circle(image, (cx, cy), radius, (200, 200, 200), 1, cv2.LINE_AA)

        # Large countdown number (3, 2, 1)
        display_sec = str(int(math.ceil(time_left)))
        (tw, th), _ = cv2.getTextSize(display_sec, cv2.FONT_HERSHEY_SIMPLEX, 2.5, 4)
        cv2.putText(image, display_sec, (cx - tw // 2, cy + th // 2), cv2.FONT_HERSHEY_SIMPLEX, 2.5, (255, 255, 255), 5, cv2.LINE_AA)
        cv2.putText(image, display_sec, (cx - tw // 2, cy + th // 2), cv2.FONT_HERSHEY_SIMPLEX, 2.5, config.COLOR_NEON_YELLOW, 2, cv2.LINE_AA)

        prompt = "CHUAN BI CHUP ANH!"
        (pw, ph), _ = cv2.getTextSize(prompt, cv2.FONT_HERSHEY_SIMPLEX, 0.65, 2)
        cv2.putText(image, prompt, (cx - pw // 2, cy + radius + 35), cv2.FONT_HERSHEY_SIMPLEX, 0.65, config.COLOR_WHITE, 2, cv2.LINE_AA)

    def draw_notifications_and_flash(self, image: np.ndarray):
        """Draws transient notification toast and camera shutter flash."""
        if time.time() < self.notification_expiry and self.notification_text:
            h, w = image.shape[:2]
            (tw, th), _ = cv2.getTextSize(self.notification_text, cv2.FONT_HERSHEY_SIMPLEX, 0.65, 2)
            cx, cy = w // 2, 45
            x1 = cx - tw // 2 - 15
            y1 = cy - th - 10
            x2 = cx + tw // 2 + 15
            y2 = cy + 10

            sub = image[max(0, y1):min(h, y2), max(0, x1):min(w, x2)]
            if sub.shape[0] > 0 and sub.shape[1] > 0:
                overlay = np.zeros_like(sub)
                cv2.addWeighted(overlay, 0.8, sub, 0.2, 0, dst=sub)
                cv2.rectangle(image, (x1, y1), (x2, y2), config.COLOR_NEON_YELLOW, 1, cv2.LINE_AA)
                cv2.putText(image, self.notification_text, (x1 + 15, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.65, config.COLOR_WHITE, 2, cv2.LINE_AA)

        if self.flash_alpha > 0.05:
            white_screen = np.full_like(image, 255)
            cv2.addWeighted(white_screen, self.flash_alpha, image, 1.0 - self.flash_alpha, 0, dst=image)
            self.flash_alpha = max(0.0, self.flash_alpha - 0.2)
