import json
import serial

from time import sleep

XBEE_BAUD = 9600
XBEE_PORT = 'COM1'
XBEE_TIMEOUT = 1

ARDU_BAUD = 9600
ARDU_PORT = '/dev/ttyACM0'
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
ardu.open()

print('xbee: name = ' + xbee.name + ', description = ' + xbee.description)         # check which port was really used
print('ardu: name = ' + ardu.name + ', description = ' + ardu.description)         # check which port was really used

ardu.write(b'hello')     # write a string
sleep(.3)                # Delay for one tenth of a second
print ardu.readline()    # Read the newest output from the Arduino

stillrunning = True

state = {
        'me' : 0,
        'md' : 0,
        'se' : 0,
        'sd' : 0
        }

# commands to raspberrypi are json strings of the form
# {'s' : 'me', 'v' : '20', 'id' : 708 }

while stillrunning:
    # get next command from xbee
    nextcommand = xbee.readline()
    if not nextcommand == '':
        try:
            parsedcommand = json.loads(nextcommand)
        except ValueError:
            outputerror = {
                'error': { 'message': 'Parse Error for message: ' + nextcommand },
                'id': None
                }
            xbee.write(json.dumps(outputerror))
            continue
        if not 's' in nextcommand:
            outputerror = {
                'error': { 'message': 'No state' },
                'id': None
                }
            xbee.write(json.dumps(outputerror))
            continue
        if not 'v' in nextcommand:
            outputerror = {
                'error': { 'message': 'No value' },
                'id': None
                }
            xbee.write(json.dumps(outputerror))
            continue
        if not 'id' in nextcommand:
            outputerror = {
                'error': { 'message': 'No id' },
                'id': None
                }
            xbee.write(json.dumps(outputerror))
            continue
        if not nextcommand['s'] in state:
            outputerror = {
                'error': { 'message': 'State not found: ' + nextcommand['s'] },
                'id': None
                }
            xbee.write(json.dumps(outputerror))
            continue
        state[nextcommand['s']] = nextcommand['v']
        commandsent = '$ENGINE,' + state['se'] + ',' + state['sd'] + ',' + state['me'] + ',' + state['md'] + '\n'
        try:
            ardu.write(commandsent)
        except ValueError:
            output = {
                'error' : { 'message' : 'Not able to send to Arduino'},
                'id': nextcommand['id']
                }
            continue
        output = {
            'result': 'done',
            'error' : null,
            'id': nextcommand['id']
            }
            
xbee.close()             # close port
ardu.close()             # close port







