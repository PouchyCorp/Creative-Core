r"""                                
  _ __ ___   ___  _ __ ___  ___ 
 | '__/ _ \ / _ \| '_ ` _ \/ __|
 | | | (_) | (_) | | | | | \__ \
 |_|  \___/ \___/|_| |_| |_|___/
                                                       
Key Features:
-------------
- Tracks placed objects and prevents editing of blacklisted items.
- Handles rendering of placed objects within the room.
- Calculates the beauty score of a room based on decorative objects.
- Supports animated background.

Author: Pouchy (Paul)
"""

from objects.placeable import Placeable
from utils.anim import Animation

class Room:
    def __init__(self, num, bg_surf = None, anim = None) -> None:
        assert bg_surf or anim, "you should define at least one of the following : bg_surf, anim"

        self.size_px = (320,180)
        self.num = num
        self.placed : list[Placeable] = []
        
        self.anim : Animation = anim
        if self.anim:
            self.bg_surf = self.anim.get_frame()
        else:
            self.bg_surf = bg_surf
        #permanent objects that can not be edited (still place in placed to render the object)
        self.blacklist : list[Placeable] = []

    def in_blacklist(self, plcbl : Placeable) -> bool:
        return (plcbl in self.blacklist)
    
    def name_exists_in_placed(self, name : str) -> bool:
        for obj in self.placed:
            if obj.name == name:
                return True
        return False
    
    def draw_placed(self, win):
        #map(self.check_coords, self.placed)
        win.blits([placeable.get_blit_args() for placeable in self.placed])
        for placeable in self.placed:
            if placeable.temporary:
                self.placed.remove(placeable)
    
    def draw_placed_foreground(self, win):
        for placeable in self.placed:
            placeable.draw_foreground(win)
    
    def get_beauty_in_room(self):
        total = 0
        for placeable in self.placed:
            if placeable.tag == "decoration":
                total += placeable.beauty
        return total
    
    def update_sprite(self):
        if self.anim:
            self.bg_surf = self.anim.get_frame()