import pygame
import sys
from pygame.locals import *

pygame.init()

color1 = pygame.Color(105,210,231)
color2 = pygame.Color(167,219,216)
color3 = pygame.Color(224,228,204)
color4 = pygame.Color(243,134,48)
color5 = pygame.Color(250,105,0)

font = pygame.font.Font('paraaminobenzoic.ttf', 20)

height = 500
width = 800

DISPLAYSURF = pygame.display.set_mode((width, height))
pygame.display.set_caption('Interface barco')
while True: # main game loop
    DISPLAYSURF.fill(color1)
    #textSurfaceObj = fontObj.render('Bla world!', True, color2, color3)
    #textSurfaceObj.center(10, 10)

    text = font.render("Motor esquerdo", 1, color3)
    DISPLAYSURF.blit(text, (100, 50))

    # DISPLAYSURF.blit(textSurfaceObj)
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
    pygame.draw.rect(DISPLAYSURF, color4, (200, 100, 10, 200))
    pygame.draw.rect(DISPLAYSURF, color4, (230, 100, 10, 200))
    pygame.draw.rect(DISPLAYSURF, color4, (260, 100, 10, 200))
    pygame.display.update()

