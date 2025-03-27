r"""
Projet : Creative Core
Equipe : Paul Baumard, Abel Bossard, Tybalt Debruyne, Taddeo Boisseuil-Marcil
              _   _                    _           _     _           
             | | | |                  | |         | |   | |          
  _ __   __ _| |_| |_ ___ _ __ _ __   | |__   ___ | | __| | ___ _ __ 
 | '_ \ / _` | __| __/ _ \ '__| '_ \  | '_ \ / _ \| |/ _` |/ _ \ '__|
 | |_) | (_| | |_| ||  __/ |  | | | | | | | | (_) | | (_| |  __/ |   
 | .__/ \__,_|\__|\__\___|_|  |_| |_| |_| |_|\___/|_|\__,_|\___|_|   
 | |                                                                 
 |_|                                                                 

Key Features:
-------------
- Manages the drawers containing the patterns.
- Allows the player to select a pattern and move it anywhere !
- Works along with the Canva object to place the pattern on the canvas.
- The Pattern class handles the pattern's behavior and drawing.

Author: Ytyt (Tybalt), refactored by Pouchy (Paul)
"""


from utils.coord import Coord
import pygame as pg
from ui.button import Button
from ui.sprite import whiten, THUMBNAIL_LIST, DRAWER_LIST, DRAWER_HOLDER, PATTERN_LIST
from typing_extensions import Optional

# Dictionary of patterns containing the thumbnail, the pattern, and the price
# The pattern needs to be a transparent image with the pattern in white (the opacity may vary)
# The thumbnail is the image that will be shown at the place where the pattern is going to be placed
pattern_dict = { 
    "big_circle" : {'thumbnail' : THUMBNAIL_LIST[0], 'pattern' : PATTERN_LIST[0], 'price' : 5}, 
    "circle" : {'thumbnail' : THUMBNAIL_LIST[1], 'pattern' : PATTERN_LIST[1], 'price' : 10},  
    "square" : {'thumbnail' : THUMBNAIL_LIST[2], 'pattern' : PATTERN_LIST[2], 'price' : 15}, #end stage 1 
    "little_square" : {'thumbnail' : THUMBNAIL_LIST[3], 'pattern' : PATTERN_LIST[3], 'price' : 25},  
    "diamond" : {'thumbnail' : THUMBNAIL_LIST[4], 'pattern' : PATTERN_LIST[4], 'price' : 30},  
    "flower" : {'thumbnail' : THUMBNAIL_LIST[5], 'pattern' : PATTERN_LIST[5], 'price' : 40}, #end stage 2
    "cloud" : {'thumbnail' : THUMBNAIL_LIST[6], 'pattern' : PATTERN_LIST[6], 'price' : 50}, 
    "moon" : {'thumbnail' : THUMBNAIL_LIST[7], 'pattern' : PATTERN_LIST[7], 'price' : 75},
    "sun" : {'thumbnail' : THUMBNAIL_LIST[8], 'pattern' : PATTERN_LIST[8], 'price' : 100},
    "snowflake" : {'thumbnail' : THUMBNAIL_LIST[9], 'pattern' : PATTERN_LIST[9], 'price' : 150},#end stage 3
    "lightning" : {'thumbnail' : THUMBNAIL_LIST[10], 'pattern' : PATTERN_LIST[10], 'price' : 200}, 
    "fire" : {'thumbnail' : THUMBNAIL_LIST[11], 'pattern' : PATTERN_LIST[11], 'price' : 250},
    "water" : {'thumbnail' : THUMBNAIL_LIST[12], 'pattern' : PATTERN_LIST[12], 'price' : 300},
    "earth" : {'thumbnail' : THUMBNAIL_LIST[13], 'pattern' : PATTERN_LIST[13], 'price' : 400},
    "air" : {'thumbnail' : THUMBNAIL_LIST[14], 'pattern' : PATTERN_LIST[14], 'price' : 500},#end stage 4
}

class Pattern:
    """Class to manage every patterns """
    def __init__(self, name, coord, thumbnail : pg.Surface, true_pattern, price, beauty):
        self.name = name
        self.thumbnail = thumbnail
        self.true_pattern = true_pattern
        self.rect = self.thumbnail.get_rect(topleft = coord)
        self.price = price
        self.beauty = beauty
    
    def draw(self, win : pg.Surface):
        win.blit(self.thumbnail, self.rect.topleft)

    def get_effect(self):
        return self.true_pattern.copy()
    
    def copy(self):
        return Pattern(self.name, self.rect.topleft, self.thumbnail, self.true_pattern ,self.price, self.beauty)

class PatternHolder:
    """Permit to place, blite and draw every patterns"""
    def __init__(self, coord : Coord, canva):
        self.patterns : list[Pattern] = [Pattern(name, coord.xy, pattern_dict[name]['thumbnail'],
                                                  pattern_dict[name]['pattern'], pattern_dict[name]['price'],
                                                    pattern_dict[name]['price']/10) for name in pattern_dict] # List of patterns, the bauty is 10% of the price
        self.coord = coord 
        self.surf = DRAWER_HOLDER.copy()
        self.drawers : list[Button] = self.init_buttons()
        self.holded_pattern : Optional[Pattern]= None

        from objects.canva import Canva
        self.canva : Canva = canva

    def init_buttons(self):
        """Put away all the patterns in drawers, and give the good patterns when we click on it"""
        buttons = []
        drawer_sprites = DRAWER_LIST # List of sprites for the drawers
        # Respective coordinates for each drawer
        drawer_coords = [(10*6,8*6), #1
        (36*6,8*6), #2
        (10*6,34*6), #3
        (43*6,34*6), #4
        (10*6,62*6), #5
        (35*6,62*6), #6
        (61*6,62*6), #7
        (10*6,85*6), #8
        (35*6,85*6), #9
        (61*6,85*6), #10
        (10*6,108*6), #11
        (10*6,121*6), #12
        (35*6,108*6), #13
        (35*6,129*6), #14
        (61*6,108*6) #15
        
        ] # Respect the order of the sprites, please

        for i in range(15):
            button = Button((drawer_coords[i][0]+self.coord.x, drawer_coords[i][1]+self.coord.y), self.hold_pattern, whiten(drawer_sprites[i]), drawer_sprites[i], [i]) # Create a button for each drawer
            buttons.append(button) #Ajoute les patterns aux drawers

        return buttons

    def hold_pattern(self, pattern_id):
        """Transfers the pattern from the drawer to the cursor.
        The logic is passed to the Canva object because of a drawing order dilemma."""
        self.canva.game.sound_manager.items.play()
        self.canva.hold_pattern_from_drawer(self.patterns[pattern_id])

    def handle_event(self, event : pg.event.Event):
        """Check Events"""
        for button in self.drawers:
            button.handle_event(event)
    
    def draw(self, win : pg.Surface):
        """Blit the patterns at the middle of our cursors to slide them on the canva"""
        win.blit(self.surf, self.coord.xy)
        for button in self.drawers:
            button.draw(win, button.rect.collidepoint(pg.mouse.get_pos()))
