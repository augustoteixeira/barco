import os
import json
import yaml
import serial
import pprint
import time
pp = pprint.PrettyPrinter(indent=4)

import pyjsonrpc

from time import sleep

def get_serial_port():
    return "/dev/"+os.popen("dmesg | egrep ttyACM | cut -f3 -d: | tail -n1").read().strip()

state = {
        'ml' : 100,
        'mr' : 100,
        'sl' : 100,
        'sr' : 100
        }

class JsonRpc(pyjsonrpc.JsonRpc):

    @pyjsonrpc.rpcmethod
    def set(self, dict):
        """ Receives a dict like { "sl" : 10, "ml" : 20} and updates state """
        global state
        for key in dict:
            state[key] = dict[key]

rpc = JsonRpc()

XBEE_BAUD = 9600
XBEE_PORT = '/dev/ttyAMA0'
XBEE_TIMEOUT = 10

ARDU_BAUD = 9600
ARDU_PORT = '/dev/ttyACM1' # get_serial_port()
ARDU_TIMEOUT = 10

xbee = serial.Serial()   # open serial port
xbee.baudrate = XBEE_BAUD
xbee.port = XBEE_PORT
xbee.timeout = XBEE_TIMEOUT
xbee.open()

# fake interface
#class fake(object):
#    def __init__(self):
#        print("a")
#    def write(a):
#        print(a)
#    def readline():
#        return ""
#ardu = fake()

ardu = serial.Serial()   # open serial port
ardu.baudrate = ARDU_BAUD
ardu.port = ARDU_PORT
ardu.timeout = ARDU_TIMEOUT
#try:
ardu.open()
#except serial.SerialException:
#    ardu = xbee


sleep(1)                # Delay for one second

bytesToRead = ardu.inWaiting()
try:
    print(ardu.read(bytesToRead))
except ValueError:
    print 'Did not manage to read output'

#print ardu.readline()    # Read the newest output from the Arduino

stillrunning = True

xbeeMessage = ''

while stillrunning:

    # get next command from xbee
    nextcommand = xbee.readline()
    #xbee.write(b'hello\n')
    #print("A")

    if not nextcommand == '':
        #a = yaml.safe_load(nextcommand)
        #print(a)
        response_json = rpc.call(nextcommand)

        #print(json.dumps(state))
        b = '{"sl":"'+str(state["sl"])+'","sr":"'+str(state["sr"])+'","ml":"'+str(state["ml"])+'","mr":"'+str(state["mr"])+'"}'
        ardu.write(b + "\n")
        print(b)
	#sleep(1)

        #bytesToRead = ardu.inWaiting()
        #try:
        #    output = ardu.read(bytesToRead)
        #except ValueError:
        #    print 'Did not manage to read output'
        #    continue
        output = ardu.readline()

	xbee.write(output)
        xbee.write(response_json)
        time.sleep(.2)



xbee.close()             # close port
ardu.close()             # close port


import sys
sys.exit()

while True:
    if not xbeeMessage == '':
        xbee.write(xbeeMessage)
        xbeeMessage = ''

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


