import pygame
import sys
import math
import serial
import os
import time
from pygame.locals import *

import pyjsonrpc

class JsonRpc(pyjsonrpc.JsonRpc):

    @pyjsonrpc.rpcmethod
    def set(self, dict):
        """ Receives a dict like { "SL" : 10, "ML" : 20} and updates state """
        global state
        for key in dict:
            state[key] = dict[key]

state = {
    'ml' : 30,
    'mr' : 80,
    'sl' : 40,
    'sr' : 70
}

rpc = JsonRpc()


def get_serial_port():
    return "/dev/" + os.popen("dmesg | egrep ttyUSB | rev | cut -c -7 | rev | head -n 1").read().strip()

ser = serial.Serial(get_serial_port(), 9600, timeout=1)

pygame.init()

inter_message_time = .2

color1 = pygame.Color(105,210,231)
color2 = pygame.Color(167,219,216)
color3 = pygame.Color(224,228,204)
color4 = pygame.Color(243,134,48)
color5 = pygame.Color(250,105,0)

color1 = pygame.Color(93,65,87)
color2 = pygame.Color(131,134,137)
color3 = pygame.Color(168,202,186)
color4 = pygame.Color(202,215,178)
color5 = pygame.Color(235,227,170)

clock = pygame.time.Clock()

font = pygame.font.Font('paraaminobenzoic.ttf', 20)

height = 650
width = 1000

DISPLAYSURF = pygame.display.set_mode((width, height))
pygame.display.set_caption('Interface barco')

old_state = {
    'ml' : -1,
    'mr' : -1,
    'sl' : -1,
    'sr' : -1
}

tradutor = {
    'ml' : 'Motor esquerdo',
    'mr' : 'Motor direito',
    'sl' : 'Servo esquerdo',
    'sr' : 'Servo direito'
}

def puttext(string, pos):
    text = font.render(string, 1, color3)
    DISPLAYSURF.blit(text, pos)

def putangle(name, angle, posx, posy):
    # angle between 0 and 100
    puttext(name, (posx + 15, posy))
    angletop = math.pi/2
    angledrive = angletop + math.pi/4 * (50 - angle) / 20.0
    minangle = min(angletop, angledrive)
    maxangle = max(angletop, angledrive)
    pygame.draw.arc(DISPLAYSURF, color4, (posx + 10, posy + 50, 80, 80), minangle, maxangle, 10)
    puttext(str(angle), (posx + 40, posy + 80))
    pygame.draw.rect(DISPLAYSURF, color5, (posx, posy - 20, 100, 140), 5)

def putbar(name, size, posx, posy):
    # size between 0 and 100
    puttext(name, (posx + 10, posy))
    puttext(str(size), (posx + 15, posy + 80))
    pygame.draw.rect(DISPLAYSURF, color4, (posx + 55, posy + 100, 10, -(size/2)))
    pygame.draw.rect(DISPLAYSURF, color5, (posx, posy - 20, 100, 140), 5)

def message(state, old_state):
    # get modification in states
    output = {}
    for key in state:
        if (state[key] != old_state[key]):
            # output.append("{'s' : '" + key + "', 'v' : '" + str(state[key]) + "', 'id' : " + str(message_id) + " }")
            output[key] = state[key]
            old_state[key] = state[key]
    return output

current_time = pygame.time.get_ticks()
received_buffer = "\n\n\n"
sent_buffer = "\n\n\n"

while True:
    DISPLAYSURF.fill(color1)

    puttext("Arrow keys: control    c: -><-    d: <-->    v: /\\\\/    f: \\//\\", (5, 5))

    # send modification in states
    ellapsed_seconds = (pygame.time.get_ticks() - current_time) / 1000.0
    if (ellapsed_seconds > inter_message_time):
        changes = message(state, old_state)
        if bool(changes):
            request = pyjsonrpc.create_request_json("set", changes) + "\n"
            ser.write(request)
            sent_buffer += request

        bytesToRead = ser.inWaiting()
        try:
            output = ser.read(bytesToRead)
        except ValueError:
            print 'Did not manage to read output'
            continue
        if output != "":
            received_buffer += output + "\n"

        current_time = pygame.time.get_ticks()

    temp = sent_buffer.split('\n')
    puttext("Last sent", (30, 450))
    puttext(temp[-3], (50, 470))
    puttext(temp[-2], (50, 490))
    temp = received_buffer.split('\n')
    puttext("Last received", (30, 530))
    puttext(temp[-3], (50, 550))
    puttext(temp[-2], (50, 570))

    putangle("Servo E", state['sl'], 100, 150)
    putangle("Servo D", state['sr'], 250, 150)

    putbar("Motor E", state['ml'], 100, 300)
    putbar("Motor D", state['mr'], 250, 300)

    clock.tick(20)
    keys = pygame.key.get_pressed()
    if (keys[K_LEFT] and state['sl'] > 0 and state['sr'] > 0):
        state['sl'] -= 1
        state['sr'] -= 1
    if (keys[K_RIGHT] and state['sl'] < 100 and state['sr'] < 100):
        state['sl'] += 1
        state['sr'] += 1
    if (keys[K_DOWN] and state['ml'] > 0 and state['mr'] > 0):
        state['ml'] -= 1
        state['mr'] -= 1
    if (keys[K_UP] and state['ml'] < 100 and state['mr'] < 100):
        state['ml'] += 1
        state['mr'] += 1
    if (keys[K_c] and state['sl'] < 100 and state['sr'] > 0):
        state['sl'] += 1
        state['sr'] -= 1
    if (keys[K_d] and state['sl'] > 0 and state['sr'] < 100):
        state['sl'] -= 1
        state['sr'] += 1
    if (keys[K_v] and state['ml'] < 100 and state['mr'] > 0):
        state['ml'] += 1
        state['mr'] -= 1
    if (keys[K_f] and state['ml'] > 0 and state['mr'] < 100):
        state['ml'] -= 1
        state['mr'] += 1

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    pygame.display.update()

