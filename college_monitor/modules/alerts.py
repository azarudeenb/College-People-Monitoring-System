"""
Alert System - Console, logging, and sound alerts
"""
import time
from datetime import datetime


class AlertManager:
    def __init__(self):
        self.alerts = []
        self.cooldowns = {}
        self.default_cooldown = 30

    def trigger(self, alert_type, message, severity="WARNING", cooldown=None):
        """Trigger an alert if not in cooldown."""
        cd = cooldown or self.default_cooldown
        now = time.time()

        if alert_type in self.cooldowns:
            if now - self.cooldowns[alert_type] < cd:
                return False

        self.cooldowns[alert_type] = now
        
        alert = {
            "type": alert_type,
            "message": message,
            "severity": severity,
            "timestamp": datetime.now().isoformat(),
        }
        self.alerts.append(alert)
        
        # Console output
        prefix = {"INFO": "[INFO]", "WARNING": "[WARN]", "CRITICAL": "[CRIT]"}
        print(f"{prefix.get(severity, '[???]')} [{alert_type}] {message}")
        
        return True

    def get_recent_alerts(self, last_n=10):
        return self.alerts[-last_n:]

    def clear(self):
        self.alerts = []
        self.cooldowns = {}
