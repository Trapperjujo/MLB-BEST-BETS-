import json
import os
from datetime import datetime
from typing import Dict, Any, Optional
from core.logger import logger

class AlphaTracker:
    """Institutional Analytics Tracker for Decision Logging."""
    
    LOG_DIR = "analytics"
    LOG_FILE = os.path.join(LOG_DIR, "decision_log.json")
    
    def __init__(self):
        if not os.path.exists(self.LOG_DIR):
            os.makedirs(self.LOG_DIR)
        if not os.path.exists(self.LOG_FILE):
            with open(self.LOG_FILE, "w") as f:
                json.dump([], f)

    def track_event(self, event_name: str, properties: Optional[Dict[str, Any]] = None):
        """
        Logs an analytical event following the object_action_context pattern.
        Example: signal_depth_viewed
        """
        payload = {
            "timestamp": datetime.now().isoformat(),
            "event": event_name,
            "properties": properties or {}
        }
        
        try:
            with open(self.LOG_FILE, "r+") as f:
                data = json.load(f)
                data.append(payload)
                f.seek(0)
                json.dump(data[-1000:], f, indent=2) # Keep last 1000 decisions
            
            logger.debug(f"Analytics logged: {event_name}")
        except Exception as e:
            logger.error(f"Failed to log alpha event: {e}")

# Global instance for app-wide instrumentation
tracker = AlphaTracker()
