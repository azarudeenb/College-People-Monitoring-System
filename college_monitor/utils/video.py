"""
Video I/O utilities - camera and file handling
"""
import cv2
import config


class VideoStream:
    def __init__(self, source=None):
        self.source = source or config.CAMERA_SOURCE
        self.cap = None
        self.frame_count = 0

    def start(self):
        """Open video stream."""
        self.cap = cv2.VideoCapture(self.source)
        if not self.cap.isOpened():
            raise RuntimeError(f"Cannot open video source: {self.source}")
        
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.FRAME_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.FRAME_HEIGHT)
        print(f"[VideoStream] Opened: {self.source}")
        return self

    def read(self):
        """Read next frame."""
        if self.cap is None:
            return False, None
        ret, frame = self.cap.read()
        if ret:
            self.frame_count += 1
        return ret, frame

    def stop(self):
        """Release video stream."""
        if self.cap:
            self.cap.release()
            print("[VideoStream] Released.")

    def get_fps(self):
        if self.cap:
            return self.cap.get(cv2.CAP_PROP_FPS)
        return config.FPS

    def get_frame_size(self):
        if self.cap:
            w = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            h = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            return w, h
        return config.FRAME_WIDTH, config.FRAME_HEIGHT

    def __enter__(self):
        return self.start()

    def __exit__(self, *args):
        self.stop()
