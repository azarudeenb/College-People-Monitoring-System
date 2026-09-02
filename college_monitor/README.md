# College People Monitoring System

A comprehensive real-time people monitoring system for college campuses using computer vision.

## Features

- Person Detection & Tracking (YOLOv8 + ByteTrack)
- Face Recognition (DeepFace with ArcFace)
- Automatic Attendance (time-windowed, zone-aware)
- Security Alerts (restricted zones, loitering detection)
- Crowd Analytics (heatmaps, density, peak analysis)
- Streamlit Dashboard (live stats and history)

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Add known faces (optional)
# Put images in: data/known_faces/<person_name>/photo.jpg

# 3. Run the monitor
python main.py                    # Webcam
python main.py --source video.mp4 # Video file
python main.py --no-face          # Skip face recognition (faster)
python main.py --heatmap          # Show heatmap overlay

# 4. Run the dashboard (separate terminal)
streamlit run dashboard/app.py
```

## Keyboard Controls

| Key | Action |
|-----|--------|
| q   | Quit |
| h   | Toggle heatmap overlay |
| s   | Save current heatmap |
| a   | Show today's attendance |
| f   | Toggle face recognition |
| z   | Toggle zone overlays |

## Project Structure

```
college_monitor/
├── main.py              # Entry point
├── config.py            # All settings
├── requirements.txt     # Dependencies
├── README.md
├── modules/
│   ├── detector.py      # YOLOv8 detection
│   ├── tracker.py       # ByteTrack tracking
│   ├── face_recognition.py
│   ├── attendance.py    # SQLite attendance
│   ├── zone_monitor.py  # Entry/exit + zones
│   ├── crowd_analytics.py
│   └── alerts.py
├── utils/
│   ├── drawing.py       # Visualization
│   └── video.py         # Camera handling
├── dashboard/
│   └── app.py           # Streamlit dashboard
└── data/
    ├── known_faces/     # Face images per person
    ├── attendance.db    # Auto-created
    └── heatmaps/        # Saved heatmaps
```

## Configuration

Edit `config.py` to customize:
- Camera source (webcam/file/RTSP)
- Zone definitions (polygons)
- Class hours for attendance
- Alert thresholds
- Model selection (YOLO size, face model)

## Tips

- Start with `--no-face` for faster testing
- Use `yolov8n.pt` for speed, `yolov8m.pt` for accuracy
- Add multiple images per person for better recognition
- Adjust `FACE_DISTANCE_THRESHOLD` if getting false matches
