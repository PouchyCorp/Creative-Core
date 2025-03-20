r"""
Projet : Creative Core
Equipe : Paul Baumard, Abel Bossard, Tybalt Debruyne, Taddeo Boisseuil-Marcil
        _                      _     _      
       | |                    | |   | |     
  _ __ | | __ _  ___ ___  __ _| |__ | | ___ 
 | '_ \| |/ _` |/ __/ _ \/ _` | '_ \| |/ _ \
 | |_) | | (_| | (_|  __/ (_| | |_) | |  __/
 | .__/|_|\__,_|\___\___|\__,_|_.__/|_|\___|
 | |                                        
 |_|                                        

Key Features:
-------------
- Placeables are all the things placed in a room that can be edited and interacted with.
- Supports static surfaces and animations with frame updates.
- Pixelization and hover-based outline effects.
- Custom pickling for object persistence.

Author: Pouchy (Paul), with contributions from Tioh (Taddeo) for visual effects.
"""

from pygame import Surface, Rect, transform, image, BLEND_RGBA_MIN
import sys
import os
from random import randint
#do not remove
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.coord import Coord
from utils.anim import Animation
from ui.sprite import get_outline

class Placeable:
    def __init__(self, name: str, coord: Coord, surf: Surface, tag: str | None = None, anim: Animation | None = None, y_constraint: int | None = None, price : int = 0, beauty : float = 0, flags : list = []) -> None:
        """Initializes a Placeable object with a name, coordinates, surface, and optional tag, animation, and y_constraint.
        Flags are :
        - "no_outline" : the object won't have an outline when hovered
        - "temporary" : the object will be removed after a certain time
        - "no_interaction" : the object won't have any interaction when clicked
        - "static" : the outline will be calculated only once, very important for performance of big sprites"""

        self.name = name
        self.id = randint(0, 10000000)  # Generates a random ID for the Placeable instance
        self.coord = coord
        self.coord.xy = self.coord.get_pixel_perfect()  # Obtains pixel-perfect coordinates
        self.coord.x, self.coord.y = self.coord.xy

        # Select either the animation frame or the provided surface for rendering
        if anim:
            self.surf = anim.get_frame()
        else:
            self.surf = surf
        self.anim = anim
        self.temp_surf = self.surf.copy()  # Create a temporary copy of the surface

        self.tag = tag

        self.rect: Rect = self.surf.get_rect()  # Get the rectangular area of the surface
        self.rect.x, self.rect.y = self.coord.xy  # Set rectangle's position
        self.temp_rect = self.rect.copy()

        # Snap to x-axis if a y_constraint is provided
        self.y_constraint = y_constraint
        self.placed = False  # Indicates if the Placeable object has been placed in a room

        self.price = price
        self.beauty = beauty

        for flag in flags:
            setattr(self, flag, True)

        if "static" in flags:
            self.precalculated_outline = get_outline(self.surf, (255,255,255)) # white outline, that will be used for the whole time
            # white because a filter will be applied to the outline to change its color

    def get_blit_args(self):
        """Returns the surface and rectangle for blitting."""
        return self.temp_surf, self.temp_rect
    
    def draw_foreground(self, win):
        """Placeholder method for foreground sprite; meant to be overridden in subclasses."""
        pass

    def draw_outline(self, win: Surface, color: tuple):
        """Draws an outline around the surface on the given window."""
        win.blit(get_outline(self.surf, color), (self.rect.x-3, self.rect.y-3))
    
    def move(self, coord: Coord):
        """Updates the position of the Placeable object based on new coordinates."""
        self.coord = coord
        self.coord.xy = coord.get_pixel_perfect()  # Ensure the coordinates are pixel-perfect
        self.rect.topleft = self.coord.xy  # Update the rectangle's position

    def pixelise(self):
        """Applies a pixel art shader effect by scaling the surface down and then back up."""
        self.surf = transform.scale_by(self.surf, 1/6)
        self.surf = transform.scale_by(self.surf, 6)

    def __repr__(self) -> str:
        """Returns a string representation of the Placeable object."""
        return str(self.__dict__)
    
    def interaction(self, args):
        """Placeholder method for interaction logic; meant to be overridden in subclasses."""
        pass

    def update_sprite(self, is_hovered: bool, color: tuple = (170,170,230)):
        """Updates the sprite based on hover state and modifies visual aspects if necessary."""
        if self.anim:
            self.surf = self.anim.get_frame()  # Update the surface if an animation is used

        if is_hovered and not hasattr(self, "no_outline"):
            # Create an outline if the sprite is hovered over
            if hasattr(self, "static"): # If the object is static, use the precalculated outline
                outline = self.precalculated_outline
                outline.fill(color, special_flags=BLEND_RGBA_MIN) # Change the color of the white outline
            else:
                outline = get_outline(self.surf, color)
            
            # Position of the sprite is offsetted to account for the 3-pixel border of the outline
            self.temp_surf = outline # Use the outline (solid color) as the temporary surface
            self.temp_surf.blit(self.surf, (3, 3))  # Blit the original surface onto the outline
            self.temp_rect = self.rect.copy()
            self.temp_rect.x -= 3  # Adjust position for outline
            self.temp_rect.y -= 3
        else:
            self.temp_surf = self.surf.copy()  # Use the normal surface when not hovered
            self.temp_rect = self.rect.copy()  # Retain original rectangle dimensions
    
    def set_attribute(self, attribute_name, value):
        """Dynamically sets an attribute if it exists; raises an attribute error otherwise."""
        if hasattr(self, attribute_name):  # Check if the attribute exists
            setattr(self, attribute_name, value)  # Dynamically set the attribute
        else:
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{attribute_name}'") # My first good error handling !
    
    def __getstate__(self):
        """Custom pickling method to save the object's state."""
        state = self.__dict__.copy()
        state["surf"] = (image.tostring(self.surf, "RGBA"), self.surf.get_size())
        state['temp_surf'] = state['surf']
        return state
    
    def __setstate__(self, state : dict):
        """Custom unpickling method to restore the object's state."""
        self.__dict__ = state
        self.surf = image.frombuffer(self.surf[0], self.surf[1], "RGBA")
        self.temp_surf = self.surf.copy()