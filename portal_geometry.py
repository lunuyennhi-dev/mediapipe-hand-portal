"""
Geometric Module: Fixed-Finger Corner Anchor Architecture & Smooth Compositing.
Tracks 1 frame (Index + Thumb) or 2 frames (Index + Middle + Thumb).
Supports smooth cross-fade transitions between filters.
"""
import cv2
import numpy as np

def build_dynamic_portals(hands_data):
    """
    Constructs frames strictly anchored to fingertips:
    - REQUIREMENT: Both hands must have raised at least Index AND Thumb!
      If either hand has not raised them, returns [] (Frame is NOT activated).
    - If Middle finger is curled -> 1 Frame from Index & Thumb: [L_idx, R_idx, R_thm, L_thm]
    - If Middle finger is raised -> 2 Frames:
        Frame 1: [L_idx, R_idx, R_mid, L_mid]
        Frame 2: [L_mid, R_mid, R_thm, L_thm]
    """
    if len(hands_data) < 2:
        return []

    hand_left = hands_data[0]
    hand_right = hands_data[1]

    # Finger readiness: Both hands must have at least Index and Thumb extended
    left_ready = hand_left.get('is_index_ext', False) and hand_left.get('is_thumb_ext', False)
    right_ready = hand_right.get('is_index_ext', False) and hand_right.get('is_thumb_ext', False)

    if not (left_ready and right_ready):
        return []

    l_idx = np.array(hand_left['index'])
    l_mid = np.array(hand_left['middle'])
    l_thm = np.array(hand_left['thumb'])

    r_idx = np.array(hand_right['index'])
    r_mid = np.array(hand_right['middle'])
    r_thm = np.array(hand_right['thumb'])

    # Check if Middle finger is extended on both hands
    middle_raised = hand_left.get('is_middle_ext', False) and hand_right.get('is_middle_ext', False)

    if middle_raised:
        frame1 = np.array([l_idx, r_idx, r_mid, l_mid], dtype=np.int32)
        frame2 = np.array([l_mid, r_mid, r_thm, l_thm], dtype=np.int32)
        return [
            {'band_idx': 0, 'pts': frame1},
            {'band_idx': 1, 'pts': frame2}
        ]
    else:
        frame_unified = np.array([l_idx, r_idx, r_thm, l_thm], dtype=np.int32)
        return [
            {'band_idx': 0, 'pts': frame_unified}
        ]


def build_single_hand_portals(hand_data):
    """
    Fallback for 1 hand: Requires Index and Thumb extended.
    """
    if not (hand_data.get('is_index_ext', False) and hand_data.get('is_thumb_ext', False)):
        return []

    idx = np.array(hand_data['index'])
    mid = np.array(hand_data['middle'])
    thm = np.array(hand_data['thumb'])
    wri = np.array(hand_data['wrist'])

    if hand_data.get('is_middle_ext', False):
        frame1 = np.array([idx, mid, (mid + wri) // 2, (idx + wri) // 2], dtype=np.int32)
        frame2 = np.array([mid, thm, (thm + wri) // 2, (mid + wri) // 2], dtype=np.int32)
        return [
            {'band_idx': 0, 'pts': frame1},
            {'band_idx': 1, 'pts': frame2}
        ]
    else:
        frame1 = np.array([idx, thm, (thm + wri) // 2, (idx + wri) // 2], dtype=np.int32)
        return [
            {'band_idx': 0, 'pts': frame1}
        ]


def composite_portal_filters(base_img: np.ndarray, bands: list, active_filters: list, prev_filters: list,
                             transition_alpha: float, frame_count: int, filter_engine) -> np.ndarray:
    """
    Composites clean, borderless filters into each portal frame.
    Supports smooth cross-fade interpolation (transition_alpha: 0.0 -> 1.0) when switching filters.
    """
    if not bands:
        return base_img

    output_img = base_img.copy()
    cached_filtered = {}

    def get_filter(name):
        if name not in cached_filtered:
            cached_filtered[name] = filter_engine.apply(base_img, name, frame_count)
        return cached_filtered[name]

    for band in bands:
        b_idx = band['band_idx']
        curr_name = active_filters[b_idx % len(active_filters)]
        curr_img = get_filter(curr_name)

        if transition_alpha < 1.0 and prev_filters:
            prev_name = prev_filters[b_idx % len(prev_filters)]
            prev_img = get_filter(prev_name)
            # Smooth cross-fade blending between previous and current filter
            filtered_frame = cv2.addWeighted(curr_img, transition_alpha, prev_img, 1.0 - transition_alpha, 0)
        else:
            filtered_frame = curr_img

        pts = band['pts']

        # Clean binary polygon mask
        mask = np.zeros(base_img.shape[:2], dtype=np.uint8)
        cv2.fillPoly(mask, [pts], 255)

        # Vectorized compositing
        mask_3ch = (mask[:, :, None] == 255)
        output_img = np.where(mask_3ch, filtered_frame, output_img)

    return output_img
