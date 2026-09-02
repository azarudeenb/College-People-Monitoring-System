"""
College People Monitoring System - Main Entry Point
=====================================================
Usage:
    python main.py                     # Run with webcam
    python main.py --source video.mp4  # Run with video file
    python main.py --no-face           # Skip face recognition (faster)
    python main.py --heatmap           # Show heatmap overlay

Controls:
    q - Quit
    h - Toggle heatmap overlay
    s - Save current heatmap
    a - Show today's attendance
    f - Toggle face recognition
    z - Toggle zone overlays
"""
import cv2
import argparse
import time

import config
from modules.detector import PersonDetector
from modules.tracker import PersonTracker
from modules.face_recognition import FaceRecognizer
from modules.attendance import AttendanceManager
from modules.zone_monitor import ZoneMonitor
from modules.crowd_analytics import CrowdAnalytics
from modules.alerts import AlertManager
from utils.drawing import draw_detections, draw_zones, draw_entry_line, draw_stats
from utils.video import VideoStream


def parse_args():
    parser = argparse.ArgumentParser(description="College People Monitoring System")
    parser.add_argument("--source", default=None, help="Video source (webcam index or file path)")
    parser.add_argument("--no-face", action="store_true", help="Disable face recognition")
    parser.add_argument("--heatmap", action="store_true", help="Show heatmap overlay")
    return parser.parse_args()


def main():
    args = parse_args()
    
    source = args.source if args.source else config.CAMERA_SOURCE
    if args.source and args.source.isdigit():
        source = int(args.source)

    # Initialize modules
    print("[Main] Initializing modules...")
    detector = PersonDetector()
    tracker = PersonTracker()
    face_recognizer = None if args.no_face else FaceRecognizer()
    attendance = AttendanceManager()
    alerts = AlertManager()

    # Start video stream
    stream = VideoStream(source)
    stream.start()
    
    w, h = stream.get_frame_size()
    zone_monitor = ZoneMonitor(w, h)
    crowd_analytics = CrowdAnalytics(w, h)

    print(f"[Main] Running on {w}x{h} @ {stream.get_fps():.0f} FPS")
    print("[Main] Press 'q' to quit, 'h' for heatmap, 's' to save heatmap")
    print("=" * 50)

    # State
    show_heatmap = args.heatmap
    show_zones = config.SHOW_ZONE_OVERLAYS
    use_face = not args.no_face
    face_names = {}
    fps_time = time.time()
    fps = 0

    try:
        while True:
            ret, frame = stream.read()
            if not ret:
                print("[Main] End of stream.")
                break

            # Detection
            detections = detector.get_detection_array(frame)

            # Tracking
            tracked = tracker.update(detections, stream.frame_count)

            # Zone Monitoring
            zone_monitor.update(tracked)

            # Crowd Analytics
            crowd_analytics.update(tracked)

            # Face Recognition (every 15 frames)
            if use_face and face_recognizer and stream.frame_count % 15 == 0:
                if tracked.tracker_id is not None:
                    for i, track_id in enumerate(tracked.tracker_id):
                        if track_id in face_names:
                            continue
                        x1, y1, x2, y2 = tracked.xyxy[i].astype(int)
                        face_crop = frame[max(0, y1):y2, max(0, x1):x2]
                        if face_crop.size > 0:
                            name, dist = face_recognizer.recognize(face_crop)
                            if name != "Unknown":
                                face_names[track_id] = name
                                success, msg = attendance.mark_attendance(name)
                                if success:
                                    alerts.trigger("attendance", msg, "INFO")

            # Security Alerts
            restricted_alerts = zone_monitor.get_restricted_alerts()
            for alert in restricted_alerts:
                alerts.trigger(
                    "restricted_zone",
                    f"[ALERT] {alert['count']} person(s) in {alert['zone']}!",
                    "CRITICAL"
                )

            # Loitering Detection
            if tracked.tracker_id is not None:
                for track_id in tracked.tracker_id:
                    duration = tracker.get_track_duration(track_id)
                    if duration > config.LOITERING_THRESHOLD:
                        name = face_names.get(track_id, f"Person #{track_id}")
                        alerts.trigger(
                            f"loitering_{track_id}",
                            f"[LOITER] {name} loitering for {int(duration)}s",
                            "WARNING",
                            cooldown=60,
                        )

            # Crowd Density Alert
            if crowd_analytics.is_crowded():
                alerts.trigger("crowd_density",
                             f"[CROWD] High density: {crowd_analytics.get_current_count()} people",
                             "WARNING")

            # Drawing
            display = frame.copy()

            if show_zones:
                display = draw_zones(display)
                display = draw_entry_line(display)

            if show_heatmap:
                display = crowd_analytics.get_heatmap_overlay(display)

            display = draw_detections(display, tracked, face_names)

            # Stats overlay
            stats = zone_monitor.get_stats()
            stats["People"] = crowd_analytics.get_current_count()
            stats["FPS"] = f"{fps:.0f}"
            display = draw_stats(display, stats)

            # Calculate FPS
            if stream.frame_count % 10 == 0:
                fps = 10 / (time.time() - fps_time)
                fps_time = time.time()

            # Display
            cv2.imshow("College Monitor", display)

            # Keyboard Controls
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
            elif key == ord("h"):
                show_heatmap = not show_heatmap
                print(f"[Main] Heatmap: {'ON' if show_heatmap else 'OFF'}")
            elif key == ord("s"):
                path = crowd_analytics.save_heatmap("manual")
                print(f"[Main] Heatmap saved: {path}")
            elif key == ord("a"):
                records = attendance.get_today_attendance()
                print(f"\n[Attendance] Today: {len(records)} records")
                for r in records:
                    print(f"  {r[0]} - {r[1]} ({r[2]}, {r[3]})")
                print()
            elif key == ord("f"):
                use_face = not use_face
                print(f"[Main] Face recognition: {'ON' if use_face else 'OFF'}")
            elif key == ord("z"):
                show_zones = not show_zones
                print(f"[Main] Zone overlay: {'ON' if show_zones else 'OFF'}")

    except KeyboardInterrupt:
        print("\n[Main] Interrupted.")
    finally:
        stream.stop()
        cv2.destroyAllWindows()
        
        # Final stats
        print("\n" + "=" * 50)
        print("[Final Stats]")
        stats = zone_monitor.get_stats()
        print(f"  Total Entries: {stats['entries']}")
        print(f"  Total Exits: {stats['exits']}")
        print(f"  Peak Count: {crowd_analytics.get_peak_count()}")
        print(f"  Avg Count: {crowd_analytics.get_average_count():.1f}")
        
        path = crowd_analytics.save_heatmap("final")
        print(f"  Heatmap saved: {path}")
        
        csv_path = attendance.export_csv()
        print(f"  Attendance exported: {csv_path}")


if __name__ == "__main__":
    main()
