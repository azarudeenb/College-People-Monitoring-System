"""
Multi-Object Tracking using Supervision ByteTrack
"""
import numpy as np
import supervision as sv


class PersonTracker:
    def __init__(self):
        self.tracker = sv.ByteTrack(
            track_activation_threshold=0.25,
            lost_track_buffer=30,
            minimum_matching_threshold=0.8,
            frame_rate=30,
        )
        self.tracks = {}  # track_id -> {first_seen, last_seen, positions}

    def update(self, detections_array, frame_id=0):
        """
        Update tracker with new detections.
        """
        if len(detections_array) == 0:
            sv_detections = sv.Detections.empty()
        else:
            sv_detections = sv.Detections(
                xyxy=detections_array[:, :4],
                confidence=detections_array[:, 4],
            )

        tracked = self.tracker.update_with_detections(sv_detections)

        # Update internal track history
        if tracked.tracker_id is not None:
            for i, track_id in enumerate(tracked.tracker_id):
                cx = (tracked.xyxy[i][0] + tracked.xyxy[i][2]) / 2
                cy = (tracked.xyxy[i][1] + tracked.xyxy[i][3]) / 2
                
                if track_id not in self.tracks:
                    self.tracks[track_id] = {
                        "first_seen": frame_id,
                        "last_seen": frame_id,
                        "positions": [(cx, cy)],
                    }
                else:
                    self.tracks[track_id]["last_seen"] = frame_id
                    self.tracks[track_id]["positions"].append((cx, cy))

        return tracked

    def get_track_duration(self, track_id, fps=30):
        """Get how long a track has been active (in seconds)."""
        if track_id not in self.tracks:
            return 0
        track = self.tracks[track_id]
        frames = track["last_seen"] - track["first_seen"]
        return frames / fps

    def get_active_count(self):
        """Return number of currently active tracks."""
        return len(self.tracker.tracked_tracks)
