"""
Global debug logging for diagnostic purposes.
Used to trace lifecycle events and identify crash points.
"""

import sys
from datetime import datetime


def debug_log(message: str):
    """
    Print debug message with timestamp to stdout.
    
    Safe to call from any thread or event handler.
    """
    try:
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        print(f"[{timestamp}] DEBUG >>> {message}", flush=True)
        sys.stdout.flush()
    except Exception as e:
        try:
            sys.stderr.write(f"DEBUG_LOG_ERROR: {e}\n")
        except:
            pass
