import pygame
import sys
import math
from pygame.locals import *

pygame.init()

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

state = {
    'me' : 30,
    'md' : 80,
    'se' : 40,
    'sd' : 70
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
    puttext(name, (posx + 10, posy))
    puttext(str(size), (posx + 15, posy + 80))
    pygame.draw.rect(DISPLAYSURF, color4, (posx + 55, posy + 100, 10, -(size/2)))
    pygame.draw.rect(DISPLAYSURF, color5, (posx, posy - 20, 100, 140), 5)



while True: # main game loop
    DISPLAYSURF.fill(color1)
    #textSurfaceObj = fontObj.render('Bla world!', True, color2, color3)
    #textSurfaceObj.center(10, 10)

    offset = 0
    for key in state:
        #puttext(" " + tradutor[key] + ": ", (100, 50 + offset))
        #puttext(str(state[key]), (350, 50 + offset))
        offset = offset + 20


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

    # DISPLAYSURF.blit(textSurfaceObj)
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

            # if event.key == pygame.K_LEFT:
            #     state['se'] -= 5
            #     state['sd'] -= 5





    pygame.display.update()

