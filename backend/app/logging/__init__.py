import logging
import os
import re
import sys
import json

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
SENSITIVE_PATTERNS = [
    re.compile(r"sk-[a-zA-Z0-9]{20,}"),
    re.compile(r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b"),
    re.compile(r"\b\d{3}[- ]?\d{2}[- ]?\d{4}\b"),
]

class _RedactFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        msg = record.getMessage()
        for pat in SENSITIVE_PATTERNS:
            msg = pat.sub("[REDACTED]", msg)
        record.msg = msg
        record.args = ()
        return True

class _JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "time": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
        }
        return json.dumps(log_entry)

def setup_logging() -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(_JsonFormatter())
    handler.addFilter(_RedactFilter())
    root = logging.getLogger()
    root.setLevel(LOG_LEVEL)
    root.addHandler(handler)
