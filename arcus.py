# arcus.py

import time
import serial
from connections import ARCUS_PORT, ARCUS_BAUD

###############################################################################
# Arcus Startup Script
###############################################################################
ARCUS_STARTUP_SCRIPT = [
    # Example: Check if board responds with OK
    {"command": "$",       "expect_response": True,  "expected_response": "OK"},

    {"command": "RSTOP",   "expect_response": False},
    {"command": "MECLEARX","expect_response": False},
    {"command": "MECLEARY","expect_response": False},

    {"command": "I1=4204544", "expect_response": False},
    {"command": "I7=10",      "expect_response": False},
    {"command": "I11=2",      "expect_response": False},
    {"command": "HSPD 24000", "expect_response": False},
    {"command": "LSPD 9600",  "expect_response": False},
    {"command": "ACCEL 300",  "expect_response": False},

    {"command": "ACCEL", "expect_response": True},

    {"command": "HOMEX-",  "expect_response": False},

    {
      "command": "MSTX",
      "poll": True,
      "expected_response": "0",
      "timeout": 30
    }
]

###############################################################################
# Module-Level Variable for Open Port
###############################################################################
_arcus_ser = None

###############################################################################
# Initialization Function
###############################################################################
def init_arcus():
    """
    Opens the Arcus serial port, runs the ARCUS_STARTUP_SCRIPT,
    and stores the serial port in _arcus_ser.
    Returns True if successful, False otherwise.
    """
    global _arcus_ser
    if _arcus_ser is not None:
        print("[Arcus] Already initialized.")
        return True

    try:
        ser = serial.Serial(ARCUS_PORT, ARCUS_BAUD, timeout=1)
        print(f"[Arcus] Opened port {ARCUS_PORT} at {ARCUS_BAUD} baud.")

        # Flush buffers
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        time.sleep(0.1)

        # Run each command from the startup script
        for step in ARCUS_STARTUP_SCRIPT:
            cmd            = step["command"]
            poll_enabled   = step.get("poll", False)
            expect_resp    = step.get("expect_response", False)
            expected_resp  = step.get("expected_response", None)
            timeout        = step.get("timeout", 30)  # default 30s if not specified

            if not poll_enabled:
                # Single-send command
                ser.write((cmd + "\r").encode("utf-8"))
                print(f"[Arcus] >> {cmd}")

                if expect_resp:
                    resp_line = ser.readline().decode("utf-8", errors="replace").rstrip("\r\x04").strip()
                    print(f"[Arcus] << {resp_line}")

                    # Compare to expected response if specified
                    if expected_resp and resp_line.upper() != expected_resp.upper():
                        print(f"[Arcus] WARNING: Expected '{expected_resp}', got '{resp_line}'")
                else:
                    # If no immediate response expected, brief delay
                    time.sleep(0.05)

            else:
                # Polling step: repeatedly send the same command until we see the expected_response or time out
                print(f"[Arcus] Polling with '{cmd}', expecting '{expected_resp}' for up to {timeout}s.")
                start_time = time.time()

                while True:
                    ser.write((cmd + "\r").encode("utf-8"))
                    time.sleep(0.1)  # give the device time to respond

                    line_raw  = ser.readline()
                    resp_line = line_raw.decode("utf-8", errors="replace").rstrip("\r\x04").strip()
                    print(f"[Arcus] << {resp_line}")

                    if resp_line == expected_resp:
                        print(f"[Arcus] Poll matched '{expected_resp}'.")
                        break

                    # Check if we've exceeded the timeout
                    if time.time() - start_time > timeout:
                        print(f"[Arcus] Poll timed out after {timeout}s, never saw '{expected_resp}'.")
                        # Decide if you want to abort or continue
                        break

        # Store the open port
        _arcus_ser = ser
        print("[Arcus] Startup script completed.")
        return True

    except serial.SerialException as e:
        print(f"[Arcus] Serial error on {ARCUS_PORT}: {e}")
        return False

###############################################################################
# Generic Command-Send Function
###############################################################################
def arcus_send_command(cmd, expect_response=False):
    """
    Send a single command to the Arcus board (if open).
    If expect_response=True, read a single line of response and return it.
    """
    global _arcus_ser
    if not _arcus_ser or not _arcus_ser.is_open:
        print("[Arcus] Port not open.")
        return None

    _arcus_ser.write((cmd + "\r\n").encode("utf-8"))
    print(f"[Arcus] >> {cmd}")

    if expect_response:
        line_raw = _arcus_ser.readline()
        resp = line_raw.decode("utf-8", errors="replace").rstrip("\r\x04").strip()
        print(f"[Arcus] << {resp}")
        return resp
    else:
        return None

###############################################################################
# Close Function
###############################################################################
def close_arcus():
    """
    Close the Arcus serial port if open.
    """
    global _arcus_ser
    if _arcus_ser and _arcus_ser.is_open:
        _arcus_ser.close()
        print("[Arcus] Port closed.")
    _arcus_ser = None
