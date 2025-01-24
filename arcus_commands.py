"""
Arcus Command Sequences
Date: 2025-01-22
Author: omgyeti
"""

INIT_SEQUENCE = [
    {"command": "$", "expected_response": "OK"},
    {"command": "RSTOP"},
    {"command": "MECLEARX"},
    {"command": "MECLEARY"},
    {"command": "I1=4204544"},
    {"command": "HSPD 24000"},
    {"command": "LSPD 9600"},
    {"command": "ACCEL 300"},
    {"command": "HOMEX-"},
    {"command": "MSTX", "expected_response": "0"}
]

GET_STATUS_SEQUENCE = [
    {"command": "MSTX"},
    {"command": "MSTY"},
    {"command": "MIOY"},
    {"command": "LSPD"},
    {"command": "HSPD"},
]

EMERGENCY_STOP_SEQUENCE = [
    {"command": "RSTOP"},
    {"command": "MSTX", "expected_response": "0"}
]