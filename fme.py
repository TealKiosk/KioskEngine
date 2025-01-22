# fme.py

import time
import serial
from connections import FME_PORT, FME_BAUD

FME_STARTUP_SCRIPT = [
    {"command": "$", "expect_response": True, "expected_response": "OK"},
    {"command": "RSTOP", "expect_response": False},
    # ... more FME init commands if needed
]

_fme_ser = None

def init_fme():
    global _fme_ser
    if _fme_ser is not None:
        print("[FME] Already initialized.")
        return True

    try:
        ser = serial.Serial(FME_PORT, FME_BAUD, timeout=1)
        print(f"[FME] Opened port {FME_PORT} at {FME_BAUD} baud.")

        ser.reset_input_buffer()
        ser.reset_output_buffer()
        time.sleep(0.1)

        for step in FME_STARTUP_SCRIPT:
            cmd = step["command"]
            expect_resp = step.get("expect_response", False)
            expected_resp = step.get("expected_response", None)

            ser.write((cmd + "\r").encode("utf-8"))
            print(f"[FME] >> {cmd}")

            if expect_resp:
                resp_line = ser.readline().decode("utf-8", errors="replace").rstrip("\r\x04").strip()
                print(f"[FME] << {resp_line}")

                if expected_resp and resp_line.upper() != expected_resp.upper():
                    print(f"[FME] WARNING: Expected '{expected_resp}', got '{resp_line}'")
            else:
                time.sleep(0.05)

        _fme_ser = ser
        print("[FME] Startup script completed.")
        return True

    except serial.SerialException as e:
        print(f"[FME] Serial error on {FME_PORT}: {e}")
        return False


def fme_send_command(cmd, expect_response=False):
    global _fme_ser
    if not _fme_ser or not _fme_ser.is_open:
        print("[FME] Port not open.")
        return None

    _fme_ser.write((cmd + "\r").encode("utf-8"))
    print(f"[FME] >> {cmd}")

    if expect_response:
        line_raw = _fme_ser.readline()
        resp = line_raw.decode("utf-8", errors="replace").rstrip("\r\x04").strip()
        print(f"[FME] << {resp}")
        return resp
    else:
        return None

def close_fme():
    global _fme_ser
    if _fme_ser and _fme_ser.is_open:
        _fme_ser.close()
        print("[FME] Port closed.")
    _fme_ser = None
