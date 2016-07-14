import os
import json
import serial
import pprint
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
ardu.open()

#print('xbee: name = ' + xbee.name + ', description = ' + xbee.description)         # check which port was really used
#print('ardu: name = ' + ardu.name + ', description = ' + ardu.description)         # check which port was really used

#ardu.write(b'hello')     # write a string
#sleep(.3)                # Delay for one tenth of a second
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
        print("Received" + nextcommand)
        try:
            parsedcommand = json.loads(nextcommand)
            print("Parsed to:")
            pp.pprint(parsedcommand)
        except ValueError:
            outputerror = {
                'error': { 'message': 'Parse Error for message: ' + nextcommand },
                'id': None
                }
            xbee.write(json.dumps(outputerror))
            continue
        if not 's' in parsedcommand:
            outputerror = {
                'error': { 'message': 'No state' },
                'id': None
                }
            xbee.write(json.dumps(outputerror))
            continue
        if not 'v' in parsedcommand:
            outputerror = {
                'error': { 'message': 'No value' },
                'id': None
                }
            xbee.write(json.dumps(outputerror))
            continue
        if not 'id' in parsedcommand:
            outputerror = {
                'error': { 'message': 'No id' },
                'id': None
                }
            xbee.write(json.dumps(outputerror))
            continue
        if not parsedcommand['s'] in state:
            outputerror = {
                'error': { 'message': 'State not found: ' + nextcommand['s'] },
                'id': None
                }
            xbee.write(json.dumps(outputerror))
            continue
        state[parsedcommand['s']] = parsedcommand['v']
        commandsent = '$ENGINE,' + str(state['se']) + ',' + str(state['sd']) + ',' + str(state['me']) + ',' + str(state['md']) + '\n'
        try:
            ardu.write(commandsent)
            print("Sent command: " + commandsent)
            xbee.write("Sent commnd: " + commandsent)
        except ValueError:
            outputerror = {
                'error' : { 'message' : 'Not able to send to Arduino'},
                'id': parsedcommand['id']
                }
            xbee.write(json.dumps(outputerror))
            continue
        outputerror = {
            'result': 'done',
            'error' : None,
            'id': parsedcommand['id']
            }
            
xbee.close()             # close port
ardu.close()             # close port







