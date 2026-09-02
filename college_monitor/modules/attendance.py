"""
Attendance System - auto-marks attendance based on face recognition
"""
import sqlite3
import time
from datetime import datetime
import config


class AttendanceManager:
    def __init__(self):
        self.db_path = config.ATTENDANCE_DB
        self.cooldown = config.ATTENDANCE_COOLDOWN
        self.class_hours = config.CLASS_HOURS
        self.last_marked = {}
        self._init_db()

    def _init_db(self):
        """Initialize SQLite database."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                person_name TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                zone TEXT,
                session TEXT,
                date TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS daily_summary (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                total_present INTEGER,
                total_absent INTEGER,
                session TEXT
            )
        """)
        conn.commit()
        conn.close()

    def is_class_time(self):
        """Check if current time is within class hours."""
        now = datetime.now().strftime("%H:%M")
        for session, (start, end) in self.class_hours.items():
            if start <= now <= end:
                return True, session
        return False, None

    def mark_attendance(self, person_name, zone="classroom_1"):
        """Mark attendance for a recognized person."""
        is_class, session = self.is_class_time()
        if not is_class:
            return False, "Not class time"

        now = time.time()
        if person_name in self.last_marked:
            elapsed = now - self.last_marked[person_name]
            if elapsed < self.cooldown:
                return False, f"Cooldown ({int(self.cooldown - elapsed)}s remaining)"

        self.last_marked[person_name] = now
        today = datetime.now().strftime("%Y-%m-%d")
        
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            "INSERT INTO attendance (person_name, zone, session, date) VALUES (?, ?, ?, ?)",
            (person_name, zone, session, today)
        )
        conn.commit()
        conn.close()

        return True, f"Marked: {person_name} ({session})"

    def get_today_attendance(self):
        """Get all attendance records for today."""
        today = datetime.now().strftime("%Y-%m-%d")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute(
            "SELECT person_name, timestamp, zone, session FROM attendance WHERE date = ?",
            (today,)
        )
        records = cursor.fetchall()
        conn.close()
        return records

    def export_csv(self, output_path="data/attendance_export.csv"):
        """Export attendance records to CSV."""
        import csv
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("SELECT * FROM attendance ORDER BY timestamp DESC")
        records = cursor.fetchall()
        conn.close()

        with open(output_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Name", "Timestamp", "Zone", "Session", "Date"])
            writer.writerows(records)

        return output_path
