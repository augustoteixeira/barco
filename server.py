import os
import json
import serial
import pprint
import time
pp = pprint.PrettyPrinter(indent=4)


from time import sleep

def get_serial_port():
    return "/dev/"+os.popen("dmesg | egrep ttyACM | cut -f3 -d: | tail -n1").read().strip()



XBEE_BAUD = 9600
XBEE_PORT = '/dev/ttyAMA0'
XBEE_TIMEOUT = 1

ARDU_BAUD = 9600
ARDU_PORT = get_serial_port()
ARDU_TIMEOUT = 1

xbee = serial.Serial()   # open serial port
xbee.baudrate = XBEE_BAUD
xbee.port = XBEE_PORT
xbee.timeout = XBEE_TIMEOUT
xbee.open()

ardu = serial.Serial()   # open serial port
ardu.baudrate = ARDU_BAUD
ardu.port = ARDU_PORT
ardu.timeout = ARDU_TIMEOUT

# fake interface
class fake(object):
    def __init__(self):
        print("a")
    def write(a):
        print(a)
    def readline():
        return ""

#ardu = fake()

# true arduino
ardu.open()


#print('xbee: name = ' + xbee.name + ', description = ' + xbee.description)         # check which port was really used
#print('ardu: name = ' + ardu.name + ', description = ' + ardu.description)         # check which port was really used

#ardu.write(b'hello')     # write a string
sleep(1)                # Delay for one tenth of a second
print ardu.readline()    # Read the newest output from the Arduino

state = {
        'me' : 0,
        'md' : 0,
        'se' : 0,
        'sd' : 0
        }

# commands to raspberrypi are json strings of the form
# {"s" : "me", "v" : "20", "id" : 708 }

stillrunning = True

xbeeMessage = ''

while stillrunning:
    if not xbeeMessage == '':
        xbee.write(xbeeMessage)
        xbeeMessage = ''

    # get next command from xbee
    nextcommand = xbee.readline()
    #xbee.write(b'hello\n')
    #print("A")
    if not nextcommand == '':
        xbeeMessage += "Received: " + nextcommand + "\n"
        print("Received: " + nextcommand)
        try:
            parsedcommand = json.loads(nextcommand)
            print("Parsed to:")
            pp.pprint(parsedcommand)
        except ValueError:
            outputerror = {
                'error': { 'message': 'Parse Error for message: ' + nextcommand },
                'id': None
                }
            xbeeMessage += json.dumps(outputerror) + "\n"
            continue
        if not 's' in parsedcommand:
            outputerror = {
                'error': { 'message': 'No state' },
                'id': None
                }
            xbeeMessage += json.dumps(outputerror) + "\n"
            continue
        if not 'v' in parsedcommand:
            outputerror = {
                'error': { 'message': 'No value' },
                'id': None
                }
            xbeeMessage += json.dumps(outputerror) + "\n"
            continue
        if not 'id' in parsedcommand:
            outputerror = {
                'error': { 'message': 'No id' },
                'id': None
                }
            xbeeMessage += json.dumps(outputerror) + "\n"
            continue
        if not parsedcommand['s'] in state:
            outputerror = {
                'error': { 'message': 'State not found: ' + nextcommand['s'] },
                'id': None
                }
            xbeeMessage += json.dumps(outputerror) + "\n"
            continue
        state[parsedcommand['s']] = parsedcommand['v']
        commandsent = '$ENGINE,' + str(state['se']) + ',' + str(state['sd']) + ',' + str(state['me']) + ',' + str(state['md']) + '\n'
        try:
            ardu.write(commandsent)
            print("Sent command: " + commandsent)
            time.sleep(.4)
            xbeeMessage += "Sent commnd: " + commandsent + "\n"
        except serial.SerialException:
            outputerror = {
                'error' : { 'message' : 'Not able to send data to Arduino'},
                'id': parsedcommand['id']
                }
            xbeeMessage += json.dumps(outputerror) + "\n"
            continue
        try:
            receivedstr = ardu.readline()
            print("Arduino answered: " + receivedstr)
            xbeeMessage += "Arduino answered: " + receivedstr + "\n"
        except serial.SerialException:
            outputerror = {
                'error' : { 'message' : 'Error reading from Arduino'},
                'id': parsedcommand['id']
                }
            xbeeMessage += json.dumps(outputerror) + "\n"
            continue
        outputerror = {
            'result': 'done',
            'error' : None,
            'id': parsedcommand['id']
            }
            
xbee.close()             # close port
ardu.close()             # close port







