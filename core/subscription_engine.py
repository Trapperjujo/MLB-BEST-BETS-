import os
import pandas as pd
from datetime import datetime
import re
from core.logger import terminal_logger as logger

class SubscriptionLedger:
    """
    Institutional Marketing Intelligence: Manages your persistent
    email subscriber list for building an audience of bettors.
    """
    
    def __init__(self, db_path="analytics/subscribers.csv"):
        self.db_path = db_path
        self._ensure_db_exists()
        
    def _ensure_db_exists(self):
        """Ensures the institutional subscriber ledger is present."""
        if not os.path.exists(os.path.dirname(self.db_path)):
            os.makedirs(os.path.dirname(self.db_path))
            
        if not os.path.exists(self.db_path):
            df = pd.DataFrame(columns=["email", "timestamp", "consent", "source"])
            df.to_csv(self.db_path, index=False)
            logger.info("Subscription Engine: Initialized new subscriber ledger.")

    def is_valid_email(self, email: str) -> bool:
        """Validative check for email format alignment."""
        pattern = r"^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+\.[a-zA-Z0-9.-]+$"
        return bool(re.match(pattern, email))

    def add_subscriber(self, email: str, consent: bool, source: str = "Terminal Sidebar") -> dict:
        """
        Appends a new lead to the institutional database.
        
        Returns:
            dict: {success: bool, message: str}
        """
        if not self.is_valid_email(email):
            return {"success": False, "message": "Invalid email format. Please check your kinetic coordinates."}
            
        if not consent:
            return {"success": False, "message": "Marketing consent is required for institutional list building."}
            
        try:
            df = pd.read_csv(self.db_path)
            
            # Duplicate Detection
            if email.lower() in df['email'].str.lower().values:
                return {"success": False, "message": "Signature already identified in the alpha ledger."}
                
            new_row = {
                "email": email.lower(),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "consent": consent,
                "source": source
            }
            
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            df.to_csv(self.db_path, index=False)
            
            logger.success(f"Subscription Engine: New lead captured: {email}")
            return {"success": True, "message": "Institutional synchronization complete. Welcome to the alpha."}
            
        except Exception as e:
            logger.error(f"Subscription Engine Error: {e}")
            return {"success": False, "message": f"Critical Synchronization Error: {e}"}

    def get_subscriber_count(self) -> int:
        """Returns the total volume of institutional leads."""
        if not os.path.exists(self.db_path):
            return 0
        df = pd.read_csv(self.db_path)
        return len(df)

if __name__ == "__main__":
    # Diagnostic Pulse
    ledger = SubscriptionLedger()
    print(f"Total Institutional Leads: {ledger.get_subscriber_count()}")
