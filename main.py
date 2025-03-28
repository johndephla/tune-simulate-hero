
import os
import sys
import logging
import threading
import time
import uvicorn
from api_server import app
from browser_automation import SunoAutomation
from config import get_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("suno_automation.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def start_api_server():
    """Start the FastAPI server in a separate thread"""
    uvicorn.run(app, host="127.0.0.1", port=8000)

if __name__ == "__main__":
    logger.info("Starting Suno.ai Automation")
    
    # Load configuration
    config = get_config()
    
    # Create automation instance
    automation = SunoAutomation(
        email=config["EMAIL"],
        password=config["PASSWORD"],
        headless=config.get("HEADLESS", "False").lower() == "true"
    )
    
    # Store automation instance in app state for API access
    app.state.automation = automation
    
    # Start API server in a separate thread
    server_thread = threading.Thread(target=start_api_server, daemon=True)
    server_thread.start()
    
    logger.info(f"API server started at http://127.0.0.1:8000")
    logger.info("Press Ctrl+C to exit")
    
    try:
        # Keep main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        automation.close()
        sys.exit(0)
