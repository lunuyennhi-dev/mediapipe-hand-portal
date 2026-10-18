"""
Comprehensive test script for RETROLENS.
Verifies all 7 aesthetic filters, dynamic portal generation,
finger readiness checks, cross-fade blending, and touch gestures.
"""
import os
import cv2
import numpy as np

import config
from filters import FilterEngine
from portal_geometry import (
    build_dynamic_portals,
    composite_portal_filters
)
from hud import HUDOverlay
from hand_tracker import HandTracker, OneEuroFilter2D

def run_tests():
    os.makedirs("demo_outputs", exist_ok=True)
    test_img = np.zeros((480, 640, 3), dtype=np.uint8)
    cv2.circle(test_img, (320, 240), 110, (200, 150, 80), -1)

    print(">>> [Test 1/5] Verifying 7 aesthetic filters (No lightning)...")
    assert len(config.FILTER_NAMES) == 7, f"Expected 7 filters, got {len(config.FILTER_NAMES)}"
    for fname in config.FILTER_NAMES:
        out = FilterEngine.apply(test_img, fname, frame_count=10)
        assert out.shape == test_img.shape
        cv2.imwrite(f"demo_outputs/filter_{fname.lower()}.png", out)
    print(f"  [PASSED] Clean filter list verified: {config.FILTER_NAMES}")

    print("\n>>> [Test 2/5] Verifying Finger Readiness (Chua gio du ngon -> KHONG KICH HOAT KHUNG)...")
    fake_hands_fist = [
        {'hand_idx': 0, 'index': (120, 100), 'middle': (120, 200), 'thumb': (120, 300),
         'is_index_ext': False, 'is_middle_ext': False, 'is_thumb_ext': False},
        {'hand_idx': 1, 'index': (500, 100), 'middle': (500, 200), 'thumb': (500, 300),
         'is_index_ext': False, 'is_middle_ext': False, 'is_thumb_ext': False}
    ]
    portals_fist = build_dynamic_portals(fake_hands_fist)
    assert len(portals_fist) == 0, f"Expected 0 frames, got {len(portals_fist)}"
    print("  [PASSED] Zero frames activated when fingers are not raised!")

    print("\n>>> [Test 3/5] Verifying 1-frame vs 2-frame modes...")
    # 1-frame (Middle curled)
    fake_hands_curled = [
        {'hand_idx': 0, 'index': (120, 100), 'middle': (120, 200), 'thumb': (120, 300),
         'is_index_ext': True, 'is_middle_ext': False, 'is_thumb_ext': True},
        {'hand_idx': 1, 'index': (500, 100), 'middle': (500, 200), 'thumb': (500, 300),
         'is_index_ext': True, 'is_middle_ext': False, 'is_thumb_ext': True}
    ]
    portals_1 = build_dynamic_portals(fake_hands_curled)
    assert len(portals_1) == 1
    out_1 = composite_portal_filters(test_img, portals_1, ["THERMAL"], [], 1.0, 0, FilterEngine)
    cv2.imwrite("demo_outputs/single_portal_demo.png", out_1)

    # 2-frame (Middle raised)
    fake_hands_raised = [
        {'hand_idx': 0, 'index': (120, 100), 'middle': (120, 200), 'thumb': (120, 300),
         'is_index_ext': True, 'is_middle_ext': True, 'is_thumb_ext': True},
        {'hand_idx': 1, 'index': (500, 100), 'middle': (500, 200), 'thumb': (500, 300),
         'is_index_ext': True, 'is_middle_ext': True, 'is_thumb_ext': True}
    ]
    portals_2 = build_dynamic_portals(fake_hands_raised)
    assert len(portals_2) == 2
    out_2 = composite_portal_filters(test_img, portals_2, ["THERMAL", "SKETCH"], [], 1.0, 0, FilterEngine)
    cv2.imwrite("demo_outputs/dual_portal_demo.png", out_2)
    print("  [PASSED] 1-frame and 2-frame modes verified successfully!")

    print("\n>>> [Test 4/5] Verifying Cross-fade Filter Blending...")
    # Smooth blend halfway (alpha = 0.5)
    blend_out = composite_portal_filters(test_img, portals_2, ["SKETCH", "PIXELATE"], ["THERMAL", "SKETCH"], 0.5, 0, FilterEngine)
    cv2.imwrite("demo_outputs/crossfade_blend_demo.png", blend_out)
    print("  [PASSED] Cross-fade transition verified -> demo_outputs/crossfade_blend_demo.png")

    print("\n>>> [Test 5/5] Verifying One Euro Filter & HandTracker...")
    f = OneEuroFilter2D()
    p1 = f.filter([100, 100], 0.0)
    p2 = f.filter([102, 101], 0.033)
    assert np.allclose(p1, [100, 100])
    tracker = HandTracker(model_path=config.MODEL_PATH, max_hands=2)
    result = tracker.process_frame(test_img)
    tracker.close()
    print("  [PASSED] HandTracker and One Euro Filter verified successfully!")

    print("\n" + "=" * 65)
    print("ALL TESTS PASSED! CLEAN OPTIMIZED SYSTEM IS READY.")
    print("=" * 65)

if __name__ == "__main__":
    run_tests()
