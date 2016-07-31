import serial
import sys
import pprint
import cmd
import time

ser = serial.Serial(sys.argv[1], 9600, timeout=1)

while True:
    time.sleep(.4)
    input = ser.readline()
    if input != '':
        print(input)

ser.close()





