"""
RETROLENS: Ultra-Smooth Hand AR Portal & Gesture Filter System
- Hand Tracking: High-accuracy One Euro Filter with zero lag and zero jitter.
- Filter Switch: Touch Middle Finger to Thumb (Ngón giữa chạm ngón cái).
- Smooth Transition: Cinematic cross-fade between filters.
- Snapshot: Touch Index Finger to Thumb (Ngón trỏ chạm ngón cái) -> 3-second countdown.
- Frame Activation: Requires Index and Thumb extended on both hands.
- Dynamic Modes: Curl Middle finger -> 1 Frame; Raise Middle finger -> 2 Frames.
"""
import sys
import os
import time
import datetime
import cv2
import numpy as np

import config
from hand_tracker import HandTracker
from filters import FilterEngine
from portal_geometry import (
    build_dynamic_portals,
    build_single_hand_portals,
    composite_portal_filters
)
from hud import HUDOverlay

def main():
    print("=" * 65)
    print("  RETROLENS: High-Accuracy AR Portal System")
    print("=" * 65)
    print("Quy tac tuong tac:")
    print("  - Kich hoat khung: Bat buoc gio Ngon Tro & Ngon Cai tren ca 2 tay")
    print("  - Gap ngon giua: 1 KHUNG TO DUY NHAT (Ngon Tro & Ngon Cai)")
    print("  - Gio ngon giua: 2 KHUNG XEP CHONG (Tro - Giua va Giua - Cai)")
    print("  - DOI FILTER: Cham NGON GIUA VOI NGON CAI (Chuyen canh cross-fade)")
    print("  - CHUP ANH 3S: Cham NGON TRO VOI NGON CAI (hoac phim [SPACE])")
    print("  - Phim [S]: Chup ngay lap tuc  |  Phim [C]: Huy dem nguoc  |  [Q]: Thoat")
    print("=" * 65)

    cap = cv2.VideoCapture(config.CAMERA_INDEX)
    if not cap.isOpened():
        print(f"[Error] Could not open webcam index {config.CAMERA_INDEX}.")
        sys.exit(1)

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.FRAME_HEIGHT)

    tracker = HandTracker(model_path=config.MODEL_PATH, max_hands=2)
    hud = HUDOverlay()

    filter_offset = 0
    frame_counter = 0

    # Smooth filter cross-fade transition state
    num_filters = len(config.FILTER_NAMES)
    prev_filters = []
    transition_start_time = 0.0

    # Snapshot countdown state
    is_counting_down = False
    countdown_end_time = 0.0

    hud.trigger_notification("SAN SANG: GIO TAY TAO KHUNG!")

    try:
        while True:
            ret, raw_frame = cap.read()
            if not ret or raw_frame is None:
                time.sleep(0.01)
                continue

            frame = cv2.flip(raw_frame, 1)
            frame_counter += 1
            curr_time = time.time()

            # Process hand tracking with One Euro Filter
            hands_data = tracker.process_frame(frame)

            # Rule: Switch filter when Middle touches Thumb (Ngón giữa chạm ngón cái)
            gesture_action = tracker.check_filter_switch_gesture(hands_data)
            if gesture_action != 0:
                # Save previous filters for cross-fade blending
                prev_filters = [
                    config.FILTER_NAMES[(filter_offset + k) % num_filters]
                    for k in range(2)
                ]
                filter_offset = (filter_offset + gesture_action) % num_filters
                transition_start_time = curr_time
                f1 = config.FILTER_NAMES[filter_offset]
                f2 = config.FILTER_NAMES[(filter_offset + 1) % num_filters]
                hud.trigger_notification(f"FILTER 1: {f1}  |  FILTER 2: {f2}")

            # Rule: Start 3-second countdown when Index touches Thumb
            snap_triggered, hold_prog, pinch_center = tracker.check_snapshot_gesture(hands_data)
            if not is_counting_down:
                if snap_triggered:
                    is_counting_down = True
                    countdown_end_time = curr_time + config.COUNTDOWN_SECONDS
                    hud.trigger_notification("CHAM TRO & CAI -> DEM NGUOC 3S CHUP ANH!")

            # Rule: Dynamic frame generation
            # Returns [] if required fingers are not raised yet!
            bands = []
            if len(hands_data) >= 2:
                bands = build_dynamic_portals(hands_data)
            elif len(hands_data) == 1:
                bands = build_single_hand_portals(hands_data[0])

            # Active filter list for visible bands
            active_filter_list = [
                config.FILTER_NAMES[(filter_offset + k) % num_filters]
                for k in range(max(1, len(bands)))
            ]

            # Calculate transition cross-fade alpha [0.0 -> 1.0]
            elapsed_transition = curr_time - transition_start_time
            transition_alpha = min(1.0, elapsed_transition / config.FILTER_TRANSITION_SEC)

            # Composite pure borderless filters with smooth cross-fade transition
            display_frame = composite_portal_filters(
                frame,
                bands,
                active_filter_list,
                prev_filters,
                transition_alpha,
                frame_counter,
                FilterEngine
            )

            # Draw touch-hold progress ring when pinching Index & Thumb
            if not is_counting_down and hold_prog > 0.15:
                hud.draw_touch_hold_progress(display_frame, hold_prog, pinch_center)

            # Handle 3-second countdown
            if is_counting_down:
                time_left = countdown_end_time - curr_time
                if time_left > 0:
                    hud.draw_countdown_overlay(display_frame, time_left, config.COUNTDOWN_SECONDS)
                else:
                    # Timer expired -> Capture Snapshot!
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    out_path = os.path.join(config.SCREENSHOTS_DIR, f"snapshot_{timestamp}.png")
                    cv2.imwrite(out_path, display_frame)
                    hud.trigger_flash()
                    hud.trigger_notification(f"DA CHUP ANH: snapshot_{timestamp}.png", duration=1.8)
                    is_counting_down = False

            # Draw feedback toast and flash shutter
            hud.draw_notifications_and_flash(display_frame)

            # Show clean, beautiful camera canvas
            cv2.imshow("RETROLENS - Clean AR Portal", display_frame)

            # Keyboard controls
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27:
                break
            elif key == ord('s'):
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                out_path = os.path.join(config.SCREENSHOTS_DIR, f"snapshot_{timestamp}.png")
                cv2.imwrite(out_path, display_frame)
                hud.trigger_flash()
                hud.trigger_notification("DA CHUP ANH!")
            elif key == ord(' ') and not is_counting_down:
                is_counting_down = True
                countdown_end_time = time.time() + config.COUNTDOWN_SECONDS
                hud.trigger_notification("DEM NGUOC 3S CHUP ANH!")
            elif key == ord('c') and is_counting_down:
                is_counting_down = False
                hud.trigger_notification("DA HUY DEM NGUOC")
            elif key == ord('f') or key == 9:
                prev_filters = active_filter_list.copy()
                filter_offset = (filter_offset + 1) % num_filters
                transition_start_time = time.time()
                f1 = config.FILTER_NAMES[filter_offset]
                f2 = config.FILTER_NAMES[(filter_offset + 1) % num_filters]
                hud.trigger_notification(f"FILTER 1: {f1}  |  FILTER 2: {f2}")

    finally:
        cap.release()
        tracker.close()
        cv2.destroyAllWindows()
        print("[Info] Application exited cleanly.")

if __name__ == "__main__":
    main()
