"""
Person Detection using YOLOv8
"""
from ultralytics import YOLO
import numpy as np
import config


class PersonDetector:
    def __init__(self):
        self.model = YOLO(config.YOLO_MODEL)
        self.confidence = config.CONFIDENCE_THRESHOLD

    def detect(self, frame):
        """
        Detect persons in frame.
        Returns: list of detections [(x1, y1, x2, y2, confidence), ...]
        """
        results = self.model(frame, conf=self.confidence, classes=[config.PERSON_CLASS_ID], verbose=False)
        
        detections = []
        for result in results:
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    conf = float(box.conf[0])
                    detections.append((int(x1), int(y1), int(x2), int(y2), conf))
        
        return detections

    def get_detection_array(self, frame):
        """
        Returns detections in supervision-compatible format.
        Returns: numpy array of shape (N, 5) -> [x1, y1, x2, y2, conf]
        """
        detections = self.detect(frame)
        if not detections:
            return np.empty((0, 5))
        return np.array(detections)
