"""
Kiosk Service Controller
Date: 2025-01-22 17:25:52
Author: omgyeti
"""

import logging
from arcus import ArcusController
from arcus_commands import INIT_SEQUENCE

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,  # Changed to DEBUG for more detailed logs
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('kiosk_service.log'),
        logging.StreamHandler()
    ]
)

class KioskService:
    def __init__(self):
        self.arcus = ArcusController()
        
    def start(self):
        logging.info("Starting Kiosk Service")
        
        # Connect to Arcus board
        logging.info("Connecting to Arcus board...")
        error = self.arcus.connect()
        if error:
            logging.error(f"Failed to connect to Arcus board: {error}")
            return False
        
        # Run initialization sequence
        logging.info("Running initialization sequence...")
        error = self.arcus.run_sequence(INIT_SEQUENCE)
        if error:
            logging.error(f"Initialization failed: {error}")
            self.arcus.close()
            return False
            
        logging.info("Initialization completed successfully")
        return True
        
    def shutdown(self):
        logging.info("Shutting down Kiosk Service")
        self.arcus.close()

if __name__ == "__main__":
    kiosk = KioskService()
    try:
        if kiosk.start():
            logging.info("Kiosk Service started successfully")
        else:
            logging.error("Failed to start Kiosk Service")
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
    finally:
        kiosk.shutdown()