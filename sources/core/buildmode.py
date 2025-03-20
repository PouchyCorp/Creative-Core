r"""
Projet : Creative Core
Equipe : Paul Baumard, Abel Bossard, Tybalt Debruyne, Taddeo Boisseuil-Marcil
  _           _ _     _       __      _           _                   _   
 | |         (_) |   | |     / /     | |         | |                 | |  
 | |__  _   _ _| | __| |    / /    __| | ___  ___| |_ _ __ _   _  ___| |_ 
 | '_ \| | | | | |/ _` |   / /    / _` |/ _ \/ __| __| '__| | | |/ __| __|
 | |_) | |_| | | | (_| |  / /    | (_| |  __/\__ \ |_| |  | |_| | (__| |_ 
 |_.__/ \__,_|_|_|\__,_| /_/      \__,_|\___||___/\__|_|   \__,_|\___|\__|
                                                               
Key Features:
-------------
*Build mode* 
- Handles the build mode and destruction mode.
- Shows holograms of objects to be placed for better UX.
- Handles constraints like grid snapping and y-axis constraints.
- Checks if an object can be placed in a room without collision.
- Pretty overlay made by Tioh.

*Destruction mode*
- Removes objects from the room when in destruction mode.
- Returns the object to the inventory.
- Pretty overlay made by Tioh.

Author: Pouchy (Paul)
"""


from objects.placeable import Placeable
from core.room import Room
from utils.coord import Coord
from pygame import Surface, BLEND_RGBA_ADD
from typing import Optional

class BuildMode():
    """class for handling the build mode"""
    def __init__(self) -> None:
        """if i have the courage to do so, i will refactor this class, it was done early in the project and is a little obsolete compared to the rest of the code"""
        self.selected_placeable : Optional[Placeable] = None
        self.ghost_rect = None
    
    def show_room_holograms(self, win : Surface, room : Room):
        """shows the hologram of the hologram of all objects in the room, to be seen when placing a new object"""
        room_rects = [placeable.rect for placeable in room.placed]
        rect_surfs = []
        for rect in room_rects: # blue hologram surface and rect
            hologram_rect_surf : Surface = Surface((rect.width, rect.height))
            hologram_rect_surf.set_alpha(50) # transparency
            hologram_rect_surf.fill((0,0,200,50))
            rect_surfs.append(hologram_rect_surf)
        
        assert len(room_rects) == len(rect_surfs)
        win.blits((rect_surfs[i], room_rects[i]) for i in range(len(room_rects))) # blit all holograms using win.blits for performance (thanks Tioh)

        

    def show_hologram(self, win : Surface, mouse_pos : Coord):
        """shows the hologram of the selected placeable and takes care of the placing constraints"""
        pixel_perfect_mouse_pos = list(mouse_pos.get_pixel_perfect())

        if not self.ghost_rect:
            self.ghost_rect = self.selected_placeable.rect.copy() # create a ghost rect if it doesn't exist
        
        self.ghost_rect.topleft = pixel_perfect_mouse_pos

        # x constraint
        if self.selected_placeable.y_constraint:
            self.ghost_rect.bottom = self.selected_placeable.y_constraint # snap to y constraint

        
        # blue hologram surface and rect
        hologram_rect_surf : Surface = Surface((self.selected_placeable.rect.width, self.selected_placeable.rect.height))
        hologram_rect_surf.set_alpha(50)        
        hologram_rect_surf.fill((0,0,200,50))

        hologram : Surface = self.selected_placeable.surf.copy()
        hologram.set_alpha(150)
        hologram.fill((0,0,200,0),special_flags=BLEND_RGBA_ADD)

        win.blits([(hologram_rect_surf, self.ghost_rect.topleft), (hologram, self.ghost_rect.topleft)])

    def get_width(self) -> int:
        """returns the width of the selected placeable"""
        if self.selected_placeable:
            return self.selected_placeable.rect.width
        
    def get_height(self) -> int:
        """returns the height of the selected placeable"""
        if self.selected_placeable:
            return self.selected_placeable.rect.height
        
    def can_place(self, room : Room) -> bool:
        """check if the placeable can be placed without colliding with other objects"""
        room_rects = [placeable.rect for placeable in room.placed]
        if self.ghost_rect.collidelistall(room_rects) or room.num in [0, 5]:
            return False
        else:
            return True

    def get_configured_placeable(self, room_num) -> Placeable:
        """get the configured placeable with proper coordinates, to be placed in the room""" 
        self.selected_placeable.move(Coord(room_num, self.ghost_rect.topleft))
        self.selected_placeable.placed = True
        return self.selected_placeable
    
class DestructionMode():   
    """class for handling the destruction mode"""                                                 
    def __init__(self) -> None: 
        self.in_destruction_mode : bool = False

    def remove_from_room(self, placeable : Placeable, room : Room):
        """removes the placeable from the room"""
        if placeable not in room.blacklist:
            placeable.placed = False
            room.placed.remove(placeable)
    
    def toggle(self):
        """toggles the destruction mode"""
        self.in_destruction_mode = not self.in_destruction_mode
