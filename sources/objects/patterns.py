from utils.coord import Coord
import pygame as pg
from ui.button import Button
from ui.sprite import whiten, PATTERN_LIST, DRAWER_LIST, DRAWER_HOLDER
from typing_extensions import Optional

# Dictionary of patterns containing the thumbnail, the pattern, and the price
pattern_dict = { 
    "circle" : {'thumbnail' : PATTERN_LIST[0], 'pattern' : PATTERN_LIST[0], 'price' : 10}, 
    "square" : {'thumbnail' : PATTERN_LIST[1], 'pattern' : PATTERN_LIST[1], 'price' : 20},
    "triangle" : {'thumbnail' : PATTERN_LIST[2], 'pattern' : PATTERN_LIST[2], 'price' : 30},
    "star" : {'thumbnail' : PATTERN_LIST[3], 'pattern' : PATTERN_LIST[3], 'price' : 40},
    "heart" : {'thumbnail' : PATTERN_LIST[4], 'pattern' : PATTERN_LIST[4], 'price' : 50},
    "flower" : {'thumbnail' : PATTERN_LIST[5], 'pattern' : PATTERN_LIST[5], 'price' : 60},
    "cloud" : {'thumbnail' : PATTERN_LIST[6], 'pattern' : PATTERN_LIST[6], 'price' : 70},
    "moon" : {'thumbnail' : PATTERN_LIST[7], 'pattern' : PATTERN_LIST[7], 'price' : 80},
    "sun" : {'thumbnail' : PATTERN_LIST[8], 'pattern' : PATTERN_LIST[8], 'price' : 90},
    "snowflake" : {'thumbnail' : PATTERN_LIST[9], 'pattern' : PATTERN_LIST[9], 'price' : 100},
    "lightning" : {'thumbnail' : PATTERN_LIST[10], 'pattern' : PATTERN_LIST[10], 'price' : 110},
    "fire" : {'thumbnail' : PATTERN_LIST[11], 'pattern' : PATTERN_LIST[11], 'price' : 120},
    "water" : {'thumbnail' : PATTERN_LIST[12], 'pattern' : PATTERN_LIST[12], 'price' : 130},
    "earth" : {'thumbnail' : PATTERN_LIST[13], 'pattern' : PATTERN_LIST[13], 'price' : 140},
    "air" : {'thumbnail' : PATTERN_LIST[14], 'pattern' : PATTERN_LIST[14], 'price' : 150},
}

class Pattern:
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
        buttons = []
        drawer_sprites = DRAWER_LIST # List of sprites for the drawers
        # Respective coordinates for each drawer
        drawer_coords = [(10*6,8*6), (36*6,8*6), (10*6,34*6), (43*6,34*6), (10*6,62*6), (35*6,62*6), (61*6,62*6), (10*6,85*6), (35*6,85*6), (61*6,85*6), (35*6,129*6), (10*6,108*6), (10*6,121*6), (35*6,108*6), (61*6,108*6)] # Respect the order of the sprites, please

        for i in range(15):
            button = Button(drawer_coords[i], self.hold_pattern, whiten(drawer_sprites[i]), drawer_sprites[i], [i]) # Create a button for each drawer
            buttons.append(button)

        return buttons

    def hold_pattern(self, pattern_id):
        """Transfers the pattern from the drawer to the cursor.
        The logic is passed to the Canva object because of a drawing order dilemma."""
        self.canva.game.sound_manager.items.play()
        self.canva.hold_pattern_from_drawer(self.patterns[pattern_id])

    def handle_event(self, event : pg.event.Event):
        for button in self.drawers:
            button.handle_event(event)
    
    def draw(self, win : pg.Surface):
        for button in self.drawers:
            button.draw(self.surf, button.rect.collidepoint(pg.mouse.get_pos()))
        win.blit(self.surf, self.coord.xy)
