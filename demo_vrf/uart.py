import serial
import time

## Modify based on your machine & connection
# dev = '/dev/ttyUSB1' ## ubuntu syntax
dev = 'COM4'		 ## windows syntax
## BAUD Rate USB-UART
baud = 9600
## serial python objcet
ser = serial.Serial(dev, baud, timeout=0.5)

t = True
rcv = b''
while rcv != "e164":
	rcv = b''
	while rcv == b'':
		rcv = ser.read(2)
	addr = rcv.hex()
	addr = addr[2:]+addr[:2]
	print(addr)