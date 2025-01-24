"""
Arcus Board Controller
Date: 2025-01-22 17:31:14
Author: omgyeti
"""

import serial
import time
import logging
from connections import ARCUS_PORT, ARCUS_BAUD
from arcus_commands import INIT_SEQUENCE, GET_STATUS_SEQUENCE, EMERGENCY_STOP_SEQUENCE

class ArcusController:
    def __init__(self):
        self.serial = None
        self.responses = []

    def connect(self):
        try:
            self.serial = serial.Serial(
                port=ARCUS_PORT,
                baudrate=ARCUS_BAUD,
                timeout=2
            )
            time.sleep(2)
            self.serial.reset_input_buffer()
            self.serial.reset_output_buffer()
            return None
        except Exception as e:
            return f"Connection error: {str(e)}"

    def send_command(self, command, expected_response=None):
        if not self.serial or not self.serial.is_open:
            return "Serial port not open"

        try:
            full_command = f"{command}\r\n"
            self.serial.write(full_command.encode())
            self.serial.flush()
            logging.debug(f"Sent: {repr(full_command)}")
            
            time.sleep(0.1)
            raw_response = self.serial.readline().decode()
            response = raw_response.strip().replace('\r', '').replace('\x04', '')
            logging.debug(f"Received raw: {repr(raw_response)}")
            logging.debug(f"Cleaned response: {repr(response)}")
            
            # If we expect a specific response, verify it
            if expected_response is not None:
                if response != expected_response:
                    return f"Expected {expected_response}, got {response}"
            
            self.responses.append(response)
            return None

        except Exception as e:
            return f"Command error: {str(e)}"

    def wait_for_motion_complete(self, timeout=30):
        """
        Poll MSTX command until it returns '0' or timeout is reached
        Returns None on success, error message on failure
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            error = self.send_command("MSTX")
            if error:
                return error
                
            if self.responses[-1] == "0":
                logging.info("Motion complete (MSTX=0)")
                return None
                
            time.sleep(0.5)  # Wait half second between polls
            
        return f"Timeout waiting for motion to complete after {timeout} seconds"

    def run_sequence(self, sequence):
        self.responses = []
        
        for cmd in sequence:
            logging.info(f"Executing command: {cmd['command']}")
            
            # Special handling for MSTX when expecting '0'
            if cmd["command"] == "MSTX" and cmd.get("expected_response") == "0":
                error = self.wait_for_motion_complete()
                if error:
                    return error
                continue
                
            # Normal command handling
            error = self.send_command(
                cmd["command"], 
                cmd.get("expected_response")
            )
            if error:
                return error
                
        return None

    def close(self):
        if self.serial and self.serial.is_open:
            self.serial.close()

    def get_responses(self):
        return self.responses
        return self.responses