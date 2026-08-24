<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/YOLOv8-Detection-orange?style=for-the-badge&logo=yolo&logoColor=white" />
  <img src="https://img.shields.io/badge/DeepFace-Recognition-green?style=for-the-badge" />
  <img src="https://img.shields.io/badge/OpenCV-Video-red?style=for-the-badge&logo=opencv&logoColor=white" />
  <img src="https://img.shields.io/badge/Streamlit-Dashboard-ff4b4b?style=for-the-badge&logo=streamlit&logoColor=white" />
  <img src="https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white" />
</p>

# 🎓 College People Monitoring System

A comprehensive **real-time people monitoring system** for college campuses powered by computer vision and deep learning. Detects, tracks, and identifies people across camera feeds with zone-based analytics, automated attendance, and security alerts.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🚶 **Person Detection & Tracking** | YOLOv8 + ByteTrack for real-time multi-person tracking with unique IDs |
| 👤 **Face Recognition** | DeepFace (ArcFace) for enrolling and identifying known individuals |
| 📋 **Auto Attendance** | Automatically marks attendance when recognized faces enter classroom zones |
| 🚨 **Security Alerts** | Restricted zone intrusion detection + loitering alerts |
| 📊 **Crowd Analytics** | Real-time density heatmaps, people counting, peak hour analysis |
| 📈 **Live Dashboard** | Streamlit-based web dashboard with charts and attendance history |
| 🐳 **Docker Ready** | One-command deployment with Docker + Railway/Render configs included |

---

## 🏗️ Architecture

```
Camera Feed(s) ──► Detection (YOLOv8) ──► Tracking (ByteTrack)
                                                │
                        ┌───────────────────────┼───────────────────────┐
                        ▼                       ▼                       ▼
              Face Recognition          Zone Monitor            Crowd Analytics
              (DeepFace/ArcFace)     (Entry/Exit/Restricted)    (Heatmap/Density)
                        │                       │                       │
                        ▼                       ▼                       ▼
                  Attendance DB           Alert System            Heatmap Files
                   (SQLite)             (Console/Log)              (PNG)
                        │                       │                       │
                        └───────────────────────┼───────────────────────┘
                                                ▼
                                    Streamlit Dashboard (Web UI)
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Webcam or video file
- ~1GB disk space (for model downloads)

### Installation

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/college-monitor.git
cd college-monitor

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### Run the Monitor

```bash
# With webcam (default)
python main.py

# With a video file
python main.py --source campus_footage.mp4

# Without face recognition (faster for testing)
python main.py --no-face

# With heatmap overlay
python main.py --heatmap
```

### Run the Dashboard

```bash
# In a separate terminal
streamlit run dashboard/app.py
# Opens at http://localhost:8501
```

---

## ⌨️ Keyboard Controls

| Key | Action |
|-----|--------|
| `q` | Quit the application |
| `h` | Toggle heatmap overlay |
| `s` | Save current heatmap to file |
| `a` | Print today's attendance records |
| `f` | Toggle face recognition on/off |
| `z` | Toggle zone overlays |

---

## 👤 Enrolling Faces

Add face images to the `data/known_faces/` directory:

```
data/known_faces/
├── john_doe/
│   ├── photo1.jpg
│   └── photo2.jpg      # Multiple images improve accuracy
├── jane_smith/
│   └── photo1.jpg
└── your_name/
    └── selfie.jpg
```

> **Tip:** Use clear, front-facing photos with good lighting for best recognition accuracy.

---

## ⚙️ Configuration

All settings are in **`config.py`**:

```python
# Camera
CAMERA_SOURCE = 0              # 0 = webcam, or "rtsp://..." for IP cameras

# Detection
YOLO_MODEL = "yolov8n.pt"     # n=fast, s=balanced, m=accurate
CONFIDENCE_THRESHOLD = 0.5

# Face Recognition
FACE_MODEL = "ArcFace"
FACE_DISTANCE_THRESHOLD = 0.6  # Lower = stricter matching

# Zones (normalized 0-1 polygon coordinates)
ZONES = {
    "entrance": [(0.0, 0.4), (0.3, 0.4), (0.3, 1.0), (0.0, 1.0)],
    "restricted_lab": [(0.3, 0.0), (0.7, 0.0), (0.7, 0.3), (0.3, 0.3)],
}

# Attendance
CLASS_HOURS = {"morning": ("09:00", "12:00"), "afternoon": ("13:00", "16:00")}

# Security
LOITERING_THRESHOLD = 60      # seconds
RESTRICTED_ZONES = ["restricted_lab"]
```

---

## 📁 Project Structure

```
college_monitor/
├── main.py                  # Entry point - orchestrates all modules
├── config.py                # All configuration settings
├── requirements.txt         # Python dependencies
├── Dockerfile               # Docker containerization
├── docker-compose.yml       # Multi-service deployment
├── railway.json             # Railway deployment config
├── render.yaml              # Render deployment config
├── modules/
│   ├── detector.py          # YOLOv8 person detection
│   ├── tracker.py           # ByteTrack multi-object tracking
│   ├── face_recognition.py  # DeepFace enrollment & matching
│   ├── attendance.py        # SQLite attendance system
│   ├── zone_monitor.py      # Entry/exit + restricted zones
│   ├── crowd_analytics.py   # Heatmaps + density analysis
│   └── alerts.py            # Alert management system
├── utils/
│   ├── drawing.py           # Visualization overlays
│   └── video.py             # Camera/video stream handler
├── dashboard/
│   └── app.py               # Streamlit web dashboard
└── data/
    ├── known_faces/         # Enrolled face images
    ├── attendance.db        # Auto-created SQLite DB
    └── heatmaps/            # Saved heatmap images
```

---

## 🐳 Docker Deployment

### Local Docker

```bash
# Build
docker build -t college-monitor .

# Run dashboard
docker run -p 8501:8501 -v ./data:/app/data college-monitor

# Run monitor with video
docker run -v ./data:/app/data -v ./videos:/app/videos \
  college-monitor python main.py --source /app/videos/campus.mp4 --no-face
```

### Docker Compose

```bash
docker-compose up -d
```

### Deploy to Railway

```bash
# Push to GitHub, then:
# railway.app → New Project → Deploy from GitHub → Select repo → Done!
```

### Deploy to Render

```bash
# Push to GitHub, then:
# render.com → New → Web Service → Connect repo → Auto-deploys!
```

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| Detection | [Ultralytics YOLOv8](https://github.com/ultralytics/ultralytics) |
| Tracking | [Supervision](https://github.com/roboflow/supervision) (ByteTrack) |
| Face Recognition | [DeepFace](https://github.com/serengil/deepface) (ArcFace) |
| Video I/O | [OpenCV](https://opencv.org/) |
| Database | SQLite3 |
| Dashboard | [Streamlit](https://streamlit.io/) |
| Containerization | Docker |
| Deployment | Railway / Render |

---

## 📝 Roadmap

- [x] Person detection (YOLOv8)
- [x] Multi-object tracking (ByteTrack)
- [x] Face recognition & enrollment
- [x] Automated attendance system
- [x] Zone-based monitoring
- [x] Entry/exit counting
- [x] Crowd density heatmaps
- [x] Security alerts (restricted zones + loitering)
- [x] Streamlit dashboard
- [x] Docker + cloud deployment
- [ ] RTSP camera support
- [ ] PostgreSQL for production
- [ ] Email/SMS alert notifications
- [ ] Multi-camera support
- [ ] Web-based face enrollment UI
- [ ] API endpoint for mobile app

---

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgements

- [Ultralytics](https://github.com/ultralytics/ultralytics) for YOLOv8
- [Roboflow](https://github.com/roboflow/supervision) for Supervision
- [Sefik Ilkin Serengil](https://github.com/serengil/deepface) for DeepFace
- [Streamlit](https://streamlit.io/) for the dashboard framework

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/YOUR_USERNAME">Azarudeen</a>
</p>
