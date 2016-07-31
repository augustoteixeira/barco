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
        """ Receives a dict like { "se" : 10, "me" : 20} and updates state """
        global state
        for key in dict:
            state[key] = dict[key]

state = {
    'me' : 30,
    'md' : 80,
    'se' : 40,
    'sd' : 70
}

rpc = JsonRpc()


def get_serial_port():
    return "/dev/" + os.popen("dmesg | egrep ttyUSB | rev | cut -c -7 | rev | head -n 1").read().strip()

ser = serial.Serial(get_serial_port(), 9600, timeout=1)

pygame.init()

inter_message_time = 1

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

height = 500
width = 800

DISPLAYSURF = pygame.display.set_mode((width, height))
pygame.display.set_caption('Interface barco')

old_state = {
    'me' : -1,
    'md' : -1,
    'se' : -1,
    'sd' : -1
}

tradutor = {
    'me' : 'Motor esquerdo',
    'md' : 'Motor direito',
    'se' : 'Servo esquerdo',
    'sd' : 'Servo direito'
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

while True:
    DISPLAYSURF.fill(color1)

    puttext("Arrow keys: control    c: -><-    d: <-->    v: /\\\\/    f: \\//\\", (5, 5))

    # send modification in states
    ellapsed_seconds = (pygame.time.get_ticks() - current_time) / 1000.0
    if (ellapsed_seconds > inter_message_time):
        changes = message(state, old_state)
        if bool(changes):
            request = pyjsonrpc.create_request_json("set", changes)
            print request

        # mes = message(state, old_state)
        # for m in mes:
        #     ser.write(m + '\n')
        #     time.sleep(.8)
        #     for key in state:
        #         old_state[key] = state[key]

        bytesToRead = ser.inWaiting()
        try:
            output = ser.read(bytesToRead)
            #output = ser.readline()
        except ValueError:
            print 'Did not manage to read output'
            continue
        # print output

        current_time = pygame.time.get_ticks()

    putangle("Servo E", state['se'], 100, 150)
    putangle("Servo D", state['sd'], 250, 150)

    putbar("Motor E", state['me'], 100, 300)
    putbar("Motor D", state['md'], 250, 300)

    clock.tick(20)
    keys = pygame.key.get_pressed()
    if (keys[K_LEFT] and state['se'] > 0 and state['sd'] > 0):
        state['se'] -= 1
        state['sd'] -= 1
    if (keys[K_RIGHT] and state['se'] < 100 and state['sd'] < 100):
        state['se'] += 1
        state['sd'] += 1
    if (keys[K_DOWN] and state['me'] > 0 and state['md'] > 0):
        state['me'] -= 1
        state['md'] -= 1
    if (keys[K_UP] and state['me'] < 100 and state['md'] < 100):
        state['me'] += 1
        state['md'] += 1
    if (keys[K_c] and state['se'] < 100 and state['sd'] > 0):
        state['se'] += 1
        state['sd'] -= 1
    if (keys[K_d] and state['se'] > 0 and state['sd'] < 100):
        state['se'] -= 1
        state['sd'] += 1
    if (keys[K_v] and state['me'] < 100 and state['md'] > 0):
        state['me'] += 1
        state['md'] -= 1
    if (keys[K_f] and state['me'] > 0 and state['md'] < 100):
        state['me'] -= 1
        state['md'] += 1

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    pygame.display.update()

