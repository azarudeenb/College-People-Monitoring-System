"""
Configuration for College People Monitoring System
"""

# ===== Camera Settings =====
CAMERA_SOURCE = 0  # 0 for webcam, or path to video file e.g. "campus_feed.mp4"
FRAME_WIDTH = 1280
FRAME_HEIGHT = 720
FPS = 30

# ===== YOLOv8 Settings =====
YOLO_MODEL = "yolov8n.pt"  # Options: yolov8n.pt, yolov8s.pt, yolov8m.pt
CONFIDENCE_THRESHOLD = 0.5
PERSON_CLASS_ID = 0  # COCO class ID for person

# ===== Face Recognition Settings =====
FACE_MODEL = "ArcFace"  # Options: VGG-Face, Facenet, ArcFace, DeepFace
FACE_DETECTOR = "retinaface"  # Options: opencv, retinaface, mtcnn, ssd
FACE_DISTANCE_THRESHOLD = 0.6  # Lower = stricter matching
KNOWN_FACES_DIR = "data/known_faces"

# ===== Zone Definitions =====
# Each zone is a list of (x, y) polygon points (normalized 0-1)
ZONES = {
    "entrance": [(0.0, 0.4), (0.3, 0.4), (0.3, 1.0), (0.0, 1.0)],
    "exit": [(0.7, 0.4), (1.0, 0.4), (1.0, 1.0), (0.7, 1.0)],
    "restricted_lab": [(0.3, 0.0), (0.7, 0.0), (0.7, 0.3), (0.3, 0.3)],
    "classroom_1": [(0.3, 0.4), (0.7, 0.4), (0.7, 1.0), (0.3, 1.0)],
}

# ===== Entry/Exit Line =====
ENTRY_LINE_START = (0.5, 0.0)
ENTRY_LINE_END = (0.5, 1.0)

# ===== Attendance Settings =====
ATTENDANCE_DB = "data/attendance.db"
CLASS_HOURS = {
    "morning": ("09:00", "12:00"),
    "afternoon": ("13:00", "16:00"),
}
ATTENDANCE_COOLDOWN = 300  # seconds before same person can be marked again

# ===== Security Settings =====
LOITERING_THRESHOLD = 60  # seconds before loitering alert
UNKNOWN_FACE_ALERT = True
RESTRICTED_ZONES = ["restricted_lab"]

# ===== Crowd Analytics =====
HEATMAP_OUTPUT_DIR = "data/heatmaps"
HEATMAP_DECAY = 0.95
CROWD_DENSITY_ALERT = 20  # Alert if more than N people in a zone

# ===== Display Settings =====
SHOW_BOUNDING_BOXES = True
SHOW_TRACKING_IDS = True
SHOW_ZONE_OVERLAYS = True
SHOW_FACE_LABELS = True
SHOW_CROWD_COUNT = True
