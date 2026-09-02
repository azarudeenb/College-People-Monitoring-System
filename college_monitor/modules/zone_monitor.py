"""
Zone Monitoring - Entry/Exit counting, restricted area alerts
"""
import numpy as np
from collections import defaultdict
import config


class ZoneMonitor:
    def __init__(self, frame_width, frame_height):
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.zones = self._scale_zones()
        self.entry_count = 0
        self.exit_count = 0
        self.prev_positions = {}
        self.zone_occupancy = defaultdict(set)
        self.entry_line = self._scale_line()

    def _scale_zones(self):
        """Convert normalized zone coords to pixel coords."""
        scaled = {}
        for name, points in config.ZONES.items():
            scaled[name] = np.array([
                (int(x * self.frame_width), int(y * self.frame_height))
                for x, y in points
            ], dtype=np.int32)
        return scaled

    def _scale_line(self):
        """Scale entry/exit line to pixel coords."""
        sx, sy = config.ENTRY_LINE_START
        ex, ey = config.ENTRY_LINE_END
        return (
            (int(sx * self.frame_width), int(sy * self.frame_height)),
            (int(ex * self.frame_width), int(ey * self.frame_height)),
        )

    def point_in_zone(self, point, zone_name):
        """Check if a point is inside a zone polygon."""
        if zone_name not in self.zones:
            return False
        import cv2
        result = cv2.pointPolygonTest(self.zones[zone_name], point, False)
        return result >= 0

    def update(self, tracked_detections):
        """Update zone occupancy and entry/exit counts."""
        if tracked_detections.tracker_id is None:
            return

        current_positions = {}
        
        for i, track_id in enumerate(tracked_detections.tracker_id):
            cx = (tracked_detections.xyxy[i][0] + tracked_detections.xyxy[i][2]) / 2
            cy = (tracked_detections.xyxy[i][1] + tracked_detections.xyxy[i][3]) / 2
            current_positions[track_id] = (cx, cy)

            # Check zone membership
            for zone_name in self.zones:
                if self.point_in_zone((cx, cy), zone_name):
                    self.zone_occupancy[zone_name].add(track_id)
                else:
                    self.zone_occupancy[zone_name].discard(track_id)

            # Entry/Exit counting (crossing vertical line)
            if track_id in self.prev_positions:
                prev_x = self.prev_positions[track_id][0]
                line_x = self.entry_line[0][0]
                
                if prev_x < line_x and cx >= line_x:
                    self.entry_count += 1
                elif prev_x > line_x and cx <= line_x:
                    self.exit_count += 1

        self.prev_positions = current_positions

    def get_zone_count(self, zone_name):
        """Get number of people in a zone."""
        return len(self.zone_occupancy.get(zone_name, set()))

    def get_restricted_alerts(self):
        """Check if anyone is in restricted zones."""
        alerts = []
        for zone_name in config.RESTRICTED_ZONES:
            occupants = self.zone_occupancy.get(zone_name, set())
            if occupants:
                alerts.append({
                    "zone": zone_name,
                    "count": len(occupants),
                    "track_ids": list(occupants),
                })
        return alerts

    def get_stats(self):
        """Get current entry/exit stats."""
        return {
            "entries": self.entry_count,
            "exits": self.exit_count,
            "inside": self.entry_count - self.exit_count,
            "zones": {name: len(ids) for name, ids in self.zone_occupancy.items()},
        }
