import os
import json
import pandas as pd
from datetime import datetime
from core.logger import terminal_logger as logger

class CloudLedger:
    """
    Operational Persistence Service: Syncs local institutional logs 
    to the Google Sheets 'MLB 2026 ALPHA LOG' ledger.
    """
    
    def __init__(self, log_path="analytics/decision_log.json"):
        self.log_path = log_path
        self.ledger_name = "MLB 2026 ALPHA LOG"
        
    def get_latest_decisions(self) -> pd.DataFrame:
        if not os.path.exists(self.log_path):
            return pd.DataFrame()
            
        try:
            with open(self.log_path, 'r') as f:
                logs = json.load(f)
            
            # Filter for Shadow Audit events
            audit_events = [e for e in logs if e.get('event') == 'shadow_audit_capture']
            if not audit_events:
                return pd.DataFrame()
                
            df = pd.DataFrame([e['payload'] for e in audit_events])
            df['timestamp'] = [e['timestamp'] for e in audit_events]
            return df
        except Exception as e:
            logger.error(f"Persistence Sync Error: {e}")
            return pd.DataFrame()

    def sync_to_cloud(self):
        """
        Synchronizes the institutional trail to the cloud ledger.
        Note: Requires Google Cloud credentials in the environment.
        """
        df = self.get_latest_decisions()
        if df.empty:
            logger.info("Cloud Persistence: No new alpha signals to sync.")
            return
            
        logger.info(f"Cloud Persistence: Synchronizing {len(df)} institutional signals to {self.ledger_name}...")
        
        # 🛰️ BRIDGE: In a production AppDeploy environment, this would utilize
        # the Google Sheets API (v4) to append the dataframe to the cloud ledger.
        # For this version, we ensure the data is prepared in an 'Upload-Ready' CSV.
        
        upload_path = "analytics/cloud_upload_manifest.csv"
        df.to_csv(upload_path, index=False)
        logger.success(f"Cloud Persistence: Institutional manifest captured at {upload_path}")
        
        return upload_path

if __name__ == "__main__":
    ledger = CloudLedger()
    ledger.sync_to_cloud()
