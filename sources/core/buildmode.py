from objects.placeable import Placeable
from core.room import Room
from utils.coord import Coord
from pygame import Surface, BLEND_RGBA_ADD
from typing import Optional

class BuildMode():
    """class for handling the build mode"""
    def __init__(self) -> None:
        """if i have the courage to do so, i will refactor this class"""
        self.selected_placeable : Optional[Placeable] = None
        self.ghost_rect = None
    
    def show_room_holograms(self, win : Surface, room : Room):
        """shows the hologram of the hologram of all objects in the room, to be seen when placing a new object"""
        room_rects = [placeable.rect for placeable in room.placed]
        rect_surfs = []
        for rect in room_rects:
            hologram_rect_surf : Surface = Surface((rect.width, rect.height))
            hologram_rect_surf.set_alpha(50)        
            hologram_rect_surf.fill((0,0,200,50))
            rect_surfs.append(hologram_rect_surf)
        
        assert len(room_rects) == len(rect_surfs)
        win.blits((rect_surfs[i], room_rects[i]) for i in range(len(room_rects)))

        

    def show_hologram(self, win : Surface, mouse_pos : Coord):
        """shows the hologram of the selected placeable and takes care of the placing constraints"""
        pixel_perfect_mouse_pos = list(mouse_pos.get_pixel_perfect())

        if not self.ghost_rect:
            self.ghost_rect = self.selected_placeable.rect.copy()
        
        self.ghost_rect.topleft = pixel_perfect_mouse_pos

        # x constraint
        if self.selected_placeable.y_constraint:
            self.ghost_rect.y = self.selected_placeable.y_constraint # snap to y constraint

        
        # blue hologram surface and rect
        hologram_rect_surf : Surface = Surface((self.selected_placeable.rect.width, self.selected_placeable.rect.height))
        hologram_rect_surf.set_alpha(50)        
        hologram_rect_surf.fill((0,0,200,50))

        hologram : Surface = self.selected_placeable.surf.copy()
        hologram.set_alpha(150)
        hologram.fill((0,0,200,0),special_flags=BLEND_RGBA_ADD)

        win.blits([(hologram_rect_surf, self.ghost_rect.topleft), (hologram, self.ghost_rect.topleft)])

    def get_width(self) -> int:
        if self.selected_placeable:
            return self.selected_placeable.rect.width
        
    def get_height(self) -> int:
        if self.selected_placeable:
            return self.selected_placeable.rect.height
        
    def can_place(self, room : Room) -> bool:
        """check if the placeable can be placed without colliding with other objects"""
        room_rects = [placeable.rect for placeable in room.placed]
        if self.ghost_rect.collidelistall(room_rects):
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
