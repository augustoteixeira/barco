import serial
import sys
import pprint
import cmd
import time

ser = serial.Serial(sys.argv[1], 9600, timeout=1)

pp = pprint.PrettyPrinter(indent=4)

bytesToRead = ser.inWaiting()
try:
    output = ser.read(bytesToRead)
except ValueError:
    print 'Nothing to read at start...'

while True:
    command = raw_input('>')
    #print 'Received the following command (type, commmand)'
    #print type(command)
    #pp.pprint(command)
    if command == 'exit':
        break
    ser.write(command + '\n')
    time.sleep(.4)
    bytesToRead = ser.inWaiting()
    try:
        output = ser.read(bytesToRead)
    except ValueError:
        print 'Did not manage to read output'
        continue

    print output

ser.close()





