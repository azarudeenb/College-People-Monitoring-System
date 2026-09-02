"""
Face Recognition using DeepFace
"""
import os
import cv2
import numpy as np
from deepface import DeepFace
import config


class FaceRecognizer:
    def __init__(self):
        self.known_faces_dir = config.KNOWN_FACES_DIR
        self.model = config.FACE_MODEL
        self.detector = config.FACE_DETECTOR
        self.threshold = config.FACE_DISTANCE_THRESHOLD
        self.embeddings = {}  # name -> embedding
        self._load_known_faces()

    def _load_known_faces(self):
        """Load and encode all known faces from directory."""
        if not os.path.exists(self.known_faces_dir):
            os.makedirs(self.known_faces_dir)
            print(f"[FaceRecognizer] Created {self.known_faces_dir}/ - add person folders with images.")
            return

        for person_name in os.listdir(self.known_faces_dir):
            person_dir = os.path.join(self.known_faces_dir, person_name)
            if not os.path.isdir(person_dir):
                continue

            for img_file in os.listdir(person_dir):
                img_path = os.path.join(person_dir, img_file)
                try:
                    embedding = DeepFace.represent(
                        img_path=img_path,
                        model_name=self.model,
                        detector_backend=self.detector,
                    )
                    if embedding:
                        self.embeddings[person_name] = embedding[0]["embedding"]
                        print(f"[FaceRecognizer] Enrolled: {person_name}")
                        break
                except Exception as e:
                    print(f"[FaceRecognizer] Failed to encode {img_path}: {e}")

    def enroll_face(self, name, image):
        """Enroll a new face from an image (numpy array)."""
        person_dir = os.path.join(self.known_faces_dir, name)
        os.makedirs(person_dir, exist_ok=True)
        
        img_path = os.path.join(person_dir, f"{name}_01.jpg")
        cv2.imwrite(img_path, image)
        
        try:
            embedding = DeepFace.represent(
                img_path=img_path,
                model_name=self.model,
                detector_backend=self.detector,
            )
            if embedding:
                self.embeddings[name] = embedding[0]["embedding"]
                print(f"[FaceRecognizer] Enrolled: {name}")
                return True
        except Exception as e:
            print(f"[FaceRecognizer] Enrollment failed: {e}")
        return False

    def recognize(self, face_image):
        """
        Recognize a face from cropped face image.
        Returns: (name, distance) or ("Unknown", None)
        """
        if not self.embeddings:
            return "Unknown", None

        try:
            embedding = DeepFace.represent(
                img_path=face_image,
                model_name=self.model,
                detector_backend=self.detector,
                enforce_detection=False,
            )
            if not embedding:
                return "Unknown", None

            query_emb = np.array(embedding[0]["embedding"])

            best_match = "Unknown"
            best_distance = float("inf")

            for name, known_emb in self.embeddings.items():
                distance = np.linalg.norm(query_emb - np.array(known_emb))
                if distance < best_distance:
                    best_distance = distance
                    best_match = name

            if best_distance < self.threshold:
                return best_match, best_distance
            else:
                return "Unknown", best_distance

        except Exception:
            return "Unknown", None

    def detect_faces(self, frame):
        """Detect faces in frame and return bounding boxes."""
        try:
            faces = DeepFace.extract_faces(
                img_path=frame,
                detector_backend=self.detector,
                enforce_detection=False,
            )
            regions = []
            for face in faces:
                area = face.get("facial_area", {})
                if area:
                    regions.append((area["x"], area["y"], area["w"], area["h"]))
            return regions
        except:
            return []
