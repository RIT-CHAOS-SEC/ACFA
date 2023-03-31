import serial
import time

dev = '/dev/ttyACM1'
baud = 115200
ser = serial.Serial(dev, baud, timeout=1)

# ser.bytesize = 8                    # Number of data bits = 8
# ser.parity   = 'N'                  # No parity
# ser.stopbits = 1                    # Number of Stop bits = 1

ackByte = b'\x61'
readyByte = ser.read()
while readyByte != ackByte:	
	readyByte = ser.read()
	print(readyByte)
ser.write(ackByte)