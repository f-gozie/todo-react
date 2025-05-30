import logging
import sys
import os

LOG_FILE_PATH = "music_sync.log"
# Consider placing in a logs directory:
# LOGS_DIR = "logs"
# LOG_FILE_PATH = os.path.join(LOGS_DIR, "music_sync.log")

def setup_logging(debug_mode: bool = False):
    """
    Sets up logging to both console and a file.
    """
    # if LOGS_DIR not in os.listdir(): # Ensure logs directory exists
    #     try:
    #         os.makedirs(LOGS_DIR)
    #     except OSError as e:
    #         # Fallback to current directory if logs dir creation fails
    #         print(f"Warning: Could not create logs directory '{LOGS_DIR}'. Logging to current directory. Error: {e}")
    #         global LOG_FILE_PATH
    #         LOG_FILE_PATH = "music_sync.log"


    log_level = logging.DEBUG if debug_mode else logging.INFO

    # Basic configuration
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] [%(name)s] [%(module)s.%(funcName)s:%(lineno)d]: %(message)s",
        handlers=[
            logging.FileHandler(LOG_FILE_PATH, mode='a'), # Append mode
            logging.StreamHandler(sys.stdout)
        ],
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Set lower levels for noisy libraries if not in debug mode
    if not debug_mode:
        logging.getLogger("spotipy").setLevel(logging.WARNING)
        logging.getLogger("spotipy.oauth2").setLevel(logging.WARNING)
        logging.getLogger("googleapiclient").setLevel(logging.WARNING)
        logging.getLogger("google.auth.transport.requests").setLevel(logging.WARNING)
        logging.getLogger("urllib3").setLevel(logging.WARNING)
        logging.getLogger("requests").setLevel(logging.WARNING)
        logging.getLogger("schedule").setLevel(logging.INFO) # Schedule logs when jobs run

    # Get the root logger and set its level.
    # This ensures that even if a specific logger isn't configured,
    # messages of this level and above from any part of the app will be processed by basicConfig.
    # logging.getLogger().setLevel(log_level) # Already set by basicConfig's level

    # Example of getting a specific logger for a module
    # logger = logging.getLogger(__name__) # or logging.getLogger("music_sync_app.main") etc.
    # logger.info("Logging setup complete.")

    # Initial log message
    logging.info(f"Logging initialized. Log level: {logging.getLevelName(log_level)}. Log file: {LOG_FILE_PATH}")

if __name__ == "__main__":
    setup_logging(debug_mode=True)
    logging.debug("This is a debug message.")
    logging.info("This is an info message.")
    logging.warning("This is a warning message.")
    logging.error("This is an error message.")
    logging.getLogger("spotipy").warning("Spotipy test warning.") # Should show if level is WARNING or lower

    # Test another module's logger
    test_logger = logging.getLogger("my_test_module")
    test_logger.info("Info from my_test_module") # Will use root logger settings
    test_logger.debug("Debug from my_test_module") # Will show if debug_mode=True

    print(f"Check '{LOG_FILE_PATH}' for output.")
