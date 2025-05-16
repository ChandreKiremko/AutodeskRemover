import os
import sys
import webbrowser
import threading
import time
import logging
from app import app

# Setup logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def open_browser():
    """Open the web browser after a short delay"""
    time.sleep(1.5)  # Wait for the server to start
    url = "http://localhost:5000"
    logger.info(f"Opening browser at {url}")
    webbrowser.open(url)

def start_server():
    """Start the Flask server"""
    # Set Flask to run on localhost only
    logger.info("Starting Autodesk Uninstaller application...")
    
    # Disable Flask's default output
    import flask.cli
    flask.cli.show_server_banner = lambda *args, **kwargs: None
    
    # Set environment variable to indicate running as desktop app
    os.environ["RUNNING_AS_DESKTOP_APP"] = "1"
    
    # Run the Flask app
    app.run(host="localhost", port=5000, debug=False, use_reloader=False)

def main():
    """Main entry point for the desktop application"""
    # Start the Flask server in a separate thread
    server_thread = threading.Thread(target=start_server)
    server_thread.daemon = True
    server_thread.start()
    
    # Open the web browser
    open_browser()
    
    # Keep the main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Application closed by user")
        sys.exit(0)

if __name__ == "__main__":
    main()