import os # os: For file/directory management (like creating log folders).
import logging # logging: Python’s built-in module for logging events.

from datetime import datetime # datetime: Used to create timestamped log files.

import structlog # structlog: Library for structured (JSON) logging with rich context



import os
import logging
from datetime import datetime
import structlog

class CustomLogger:
    def __init__(self, log_dir="logs"):
        # Compose the full path to the log directory inside the current working directory
        self.logs_dir = os.path.join(os.getcwd(), log_dir)
        # Create the directory if it doesn't already exist (no error if it does)
        os.makedirs(self.logs_dir, exist_ok=True)
        # Create a unique, timestamped filename for the log file using current date and time
        log_file = f"{datetime.now().strftime('%m_%d_%Y_%H_%M_%S')}.log"
        # Store the full file path for use in logging handlers
        self.log_file_path = os.path.join(self.logs_dir, log_file)

    def get_logger(self, name=__file__):
        # Extract the filename part from the provided name (default is current file’s path)
        logger_name = os.path.basename(name)

        # Create a file handler to write logs to the timestamped file path
        file_handler = logging.FileHandler(self.log_file_path)
        # Set log level to INFO (only INFO and more severe logs will be recorded)
        file_handler.setLevel(logging.INFO)
        # Set output format as raw message text (JSON lines) so structlog output is not altered
        file_handler.setFormatter(logging.Formatter("%(message)s"))

        # Create a console (stream) handler to output logs to the terminal (stdout)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        # Use the same raw message formatter to preserve structured JSON output on console
        console_handler.setFormatter(logging.Formatter("%(message)s"))

        # Apply global logging configuration:
        # Logs will be at INFO level or higher
        # Logs will go both to console and the log file via the handlers above
        # Formatting is plain because structlog will generate JSON formatting for each log event
        logging.basicConfig(
            level=logging.INFO,
            format="%(message)s",
            handlers=[console_handler, file_handler]
        )

        # Configure structlog for structured JSON logs with rich context metadata
        structlog.configure(
            processors=[
                # Add a timestamp field in ISO 8601 UTC format
                structlog.processors.TimeStamper(fmt="iso", utc=True, key="timestamp"),
                # Add the log level (e.g., info, warning) to every event
                structlog.processors.add_log_level,
                # Rename the standard log message field from "event" to "event" (explicit)
                structlog.processors.EventRenamer(to="event"),
                # Render all log entries as JSON strings (for machine-friendly logs)
                structlog.processors.JSONRenderer()
            ],
            # Use the standard library Logger factory for compatibility with Python logging
            logger_factory=structlog.stdlib.LoggerFactory(),
            # Cache the logger object for improved performance on repeated use
            cache_logger_on_first_use=True,
        )

        # Return a structlog logger instance named after the file or provided name
        return structlog.get_logger(logger_name)


# --- Usage Example ---
if __name__ == "__main__":
    logger = CustomLogger().get_logger(__file__)
    logger.info("customer logger intialized")
    logger.info("User uploaded a file", user_id=123, filename="report.pdf")
    logger.error("Failed to process PDF", error="File not found", user_id=123)