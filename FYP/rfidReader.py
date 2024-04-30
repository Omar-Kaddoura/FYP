import serial
import time

def getUID():
    ser = serial.Serial('COM10', 9600, timeout=1)
    try:
        while True:
            response = ser.readline().decode().strip()
            if response.startswith("UID: "):
                uid = response.split(": ")[1]
                return uid
            time.sleep(1)
    finally:
        ser.close()
