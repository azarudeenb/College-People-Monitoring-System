"""
Drawing utilities - bounding boxes, zones, overlays, text
"""
import cv2
import numpy as np
import config


def draw_detections(frame, tracked_detections, names=None):
    """Draw bounding boxes and tracking IDs on frame."""
    if tracked_detections.tracker_id is None:
        return frame

    for i, track_id in enumerate(tracked_detections.tracker_id):
        x1, y1, x2, y2 = tracked_detections.xyxy[i].astype(int)
        
        name = names.get(track_id, None) if names else None
        color = (0, 255, 0) if name else (0, 165, 255)
        
        if config.SHOW_BOUNDING_BOXES:
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

        label = f"#{track_id}"
        if name and config.SHOW_FACE_LABELS:
            label = f"{name} (#{track_id})"
        elif config.SHOW_TRACKING_IDS:
            label = f"#{track_id}"

        cv2.putText(frame, label, (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    return frame


def draw_zones(frame):
    """Draw zone overlays on frame."""
    if not config.SHOW_ZONE_OVERLAYS:
        return frame

    h, w = frame.shape[:2]
    overlay = frame.copy()

    for zone_name, points in config.ZONES.items():
        scaled = np.array([
            (int(x * w), int(y * h)) for x, y in points
        ], dtype=np.int32)

        if zone_name in config.RESTRICTED_ZONES:
            color = (0, 0, 255)
        elif "entrance" in zone_name or "entry" in zone_name:
            color = (0, 255, 0)
        elif "exit" in zone_name:
            color = (255, 0, 0)
        else:
            color = (255, 255, 0)

        cv2.fillPoly(overlay, [scaled], color)
        cv2.polylines(frame, [scaled], True, color, 2)
        
        cx = int(np.mean(scaled[:, 0]))
        cy = int(np.mean(scaled[:, 1]))
        cv2.putText(frame, zone_name, (cx - 30, cy),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

    frame = cv2.addWeighted(overlay, 0.2, frame, 0.8, 0)
    return frame


def draw_entry_line(frame):
    """Draw the entry/exit counting line."""
    h, w = frame.shape[:2]
    sx, sy = config.ENTRY_LINE_START
    ex, ey = config.ENTRY_LINE_END
    
    pt1 = (int(sx * w), int(sy * h))
    pt2 = (int(ex * w), int(ey * h))
    
    cv2.line(frame, pt1, pt2, (0, 255, 255), 2)
    cv2.putText(frame, "Entry/Exit Line", (pt1[0] + 5, pt1[1] + 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
    return frame


def draw_stats(frame, stats):
    """Draw stats overlay (top-left corner)."""
    y_offset = 30
    for key, value in stats.items():
        text = f"{key}: {value}"
        cv2.putText(frame, text, (10, y_offset),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        y_offset += 25
    return frame
