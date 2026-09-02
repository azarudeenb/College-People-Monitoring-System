"""
Crowd Analytics - Density, heatmaps, patterns
"""
import numpy as np
import cv2
import os
from datetime import datetime
import config


class CrowdAnalytics:
    def __init__(self, frame_width, frame_height):
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.heatmap = np.zeros((frame_height, frame_width), dtype=np.float32)
        self.decay = config.HEATMAP_DECAY
        self.history = []
        self.output_dir = config.HEATMAP_OUTPUT_DIR
        os.makedirs(self.output_dir, exist_ok=True)

    def update(self, tracked_detections):
        """Update heatmap and crowd stats."""
        self.heatmap *= self.decay

        if tracked_detections.tracker_id is None:
            return

        count = len(tracked_detections.tracker_id)
        self.history.append((datetime.now(), count))

        for i in range(len(tracked_detections.xyxy)):
            cx = int((tracked_detections.xyxy[i][0] + tracked_detections.xyxy[i][2]) / 2)
            cy = int((tracked_detections.xyxy[i][1] + tracked_detections.xyxy[i][3]) / 2)
            cv2.circle(self.heatmap, (cx, cy), 30, 1.0, -1)

    def get_heatmap_overlay(self, frame):
        """Generate colored heatmap overlay on frame."""
        hm_normalized = cv2.normalize(self.heatmap, None, 0, 255, cv2.NORM_MINMAX)
        hm_colored = cv2.applyColorMap(hm_normalized.astype(np.uint8), cv2.COLORMAP_JET)
        overlay = cv2.addWeighted(frame, 0.6, hm_colored, 0.4, 0)
        return overlay

    def save_heatmap(self, tag=""):
        """Save current heatmap to file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"heatmap_{tag}_{timestamp}.png"
        filepath = os.path.join(self.output_dir, filename)
        
        hm_normalized = cv2.normalize(self.heatmap, None, 0, 255, cv2.NORM_MINMAX)
        hm_colored = cv2.applyColorMap(hm_normalized.astype(np.uint8), cv2.COLORMAP_JET)
        cv2.imwrite(filepath, hm_colored)
        return filepath

    def get_current_count(self):
        if self.history:
            return self.history[-1][1]
        return 0

    def get_peak_count(self, last_n_minutes=60):
        if not self.history:
            return 0
        cutoff = datetime.now().timestamp() - (last_n_minutes * 60)
        recent = [count for ts, count in self.history if ts.timestamp() > cutoff]
        return max(recent) if recent else 0

    def get_average_count(self, last_n_minutes=60):
        if not self.history:
            return 0
        cutoff = datetime.now().timestamp() - (last_n_minutes * 60)
        recent = [count for ts, count in self.history if ts.timestamp() > cutoff]
        return sum(recent) / len(recent) if recent else 0

    def is_crowded(self, zone_count=None):
        current = zone_count or self.get_current_count()
        return current > config.CROWD_DENSITY_ALERT
