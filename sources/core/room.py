r"""          
Projet : Creative Core
Equipe : Paul Baumard, Abel Bossard, Tybalt Debruyne, Taddeo Boisseuil-Marcil                      
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
        """Initializes a Room object with a number, background surface, and optional animation for the backgroudn.
        Blacklist is a list of permanent objects that cannot be edited (they still need to be in self.placed to render the object)."""
        assert bg_surf or anim, "You should define at least one of : bg_surf, anim."

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
        """Check if a Placeable object is in the blacklist."""
        return (plcbl in self.blacklist)
    
    def name_exists_in_placed(self, name : str) -> bool:
        """Check if a Placeable object with a specific name exists in the placed list."""
        for obj in self.placed:
            if obj.name == name:
                return True
        return False
    
    def draw_placed(self, win):
        """Draw all placed objects in the room."""
        win.blits([placeable.get_blit_args() for placeable in self.placed])
    
    def draw_placed_foreground(self, win):
        """Draw special foreground part of some objects (like the register) in the room."""
        for placeable in self.placed:
            placeable.draw_foreground(win)
    
    def get_beauty_in_room(self):
        """Calculate the total beauty score of the room based on decorative objects."""
        total = 0
        for placeable in self.placed:
            if placeable.tag == "decoration":
                total += placeable.beauty
        return total
    
    def update_sprite(self):
        """Update the background sprite of the room.
        Needs to be called every frame."""
        if self.anim:
            self.bg_surf = self.anim.get_frame()