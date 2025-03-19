r"""
Projet : Creative Core
Equipe : Paul Baumard, Abel Bossard, Tybalt Debruyne, Taddeo Boisseuil-Marcil
  _                   _     _               
 (_)                 | |   | |              
  _ _ __  _ __  _   _| |_  | |__   _____  __
 | | '_ \| '_ \| | | | __| | '_ \ / _ \ \/ /
 | | | | | |_) | |_| | |_  | |_) | (_) >  < 
 |_|_| |_| .__/ \__,_|\__| |_.__/ \___/_/\_\
         | |                                
         |_|                                

Key Features:
-------------
- Handles text input from the user.
- Need to be used in a controlled environment to avoid conflicts with other input boxes or key maps.
- Used in the title screen for the player to input their name and password, or in canvas for the player to input the name of their masterpiece ^^.

Author: Ytyt (Tybalt)
"""


import pygame as pg
from utils.fonts import TERMINAL_FONT

COLOR_ACTIVE = (255, 212, 163)
COLOR_INACTIVE = (168, 112, 62)
class InputBox:
    def __init__(self, x, y, w, h, text=''):
        self.rect = pg.Rect(x, y, w, h)
        self.color = COLOR_INACTIVE
        self.text = text
        self.txt_surface = TERMINAL_FONT.render(text, False, self.color)
        self.active = False

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONUP:
            # If the user clicked on the input_box rect.
            if self.rect.collidepoint(event.pos):
                # Toggle the active variable.
                self.active = not self.active
            else:
                self.active = False
            # Change the current color of the input box.
            self.color = COLOR_ACTIVE if self.active else COLOR_INACTIVE
            
        if event.type == pg.KEYDOWN and self.active:
            if event.key == pg.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                self.text += event.unicode
            # Re-render the text.
            self.txt_surface = TERMINAL_FONT.render(self.text, False, self.color)

    def update(self):
        # Resize the box if the text is too long.
        width = max(200, self.txt_surface.get_width()+10)
        self.rect.w = width

    def draw(self, screen):
        # Blit the text.
        screen.blit(self.txt_surface, (self.rect.x+12, self.rect.y+12))
        # Blit the rect.
        pg.draw.rect(screen, self.color, self.rect, 2)