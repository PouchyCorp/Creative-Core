r"""
Projet : Creative Core
Equipe : Paul Baumard, Abel Bossard, Tybalt Debruyne, Taddeo Boisseuil-Marcil
   _____       _          _                         
  / ____|     | |        | |                        
 | (___  _   _| |__   ___| | __ _ ___ ___  ___  ___ 
  \___ \| | | | '_ \ / __| |/ _` / __/ __|/ _ \/ __|
  ____) | |_| | |_) | (__| | (_| \__ \__ \  __/\__ \
 |_____/ \__,_|_.__/ \___|_|\__,_|___/___/\___||___/
                                                    
Module dedicated to the subclass of the Placeable class.

Key Features:
-------------
    - DoorUp and DoorDown classes for the door objects.
    - BotPlaceable for the clickable inline bot.
    - ShopPlaceable for the shop placeable at floor 2.
    - InvPlaceable for the inventory placeable at floor 1.
    - AutoCachierPlaceable for the automatic cash register unlock at floor 4.
    - SpectatorPlaceable for the spectator placeable at floor 5.

Author: Pouchy (Paul), with contributions from Tioh (Taddeo)
"""

from placeable import Placeable
import ui.sprite as sprite
from utils.anim import Animation
from typing import Optional
from utils.timermanager import TimerManager
from core.unlockmanager import UnlockManager
from pygame.transform import grayscale 
from pygame import Surface
from utils.fonts import TERMINAL_FONT, STANDARD_COLOR

class DoorUp(Placeable):
    """Class for the door up placeable.  
    Only one instance of this class is shared between all floors."""
    def __init__(self, name, coord, surf, tag = None):
        super().__init__(name, coord, surf, tag)
        self.anim_close = Animation(sprite.SPRITESHEET_BAS, 0, 9, 4, False)     #download closing animation
        self.anim_open = Animation(sprite.SPRITESHEET_HAUT, 0, 17, 4, False)    #download oppening animation
        self.anim_blink = Animation(sprite.SPRITESHEET_DOOR_BLINK, 0, 10)       #download blinking animation
        self.anim = self.anim_close
        _rect = self.anim.get_frame().get_rect()
        self.rect.width, self.rect.height = _rect.width, _rect.height
        self.anim.reset_frame()
        self.door_down : Optional[DoorDown] = None
        self.locked = True

        self.locked_surf = sprite.get_locked_surface(sprite.SPRITESHEET_DOOR_BLINK.get_img((0,0)))       #create a locked door surface
        
    
    def update_lock_status(self, unlock_manager : UnlockManager, current_room):
        if unlock_manager.is_floor_unlocked(str(current_room.num+1)):
            self.locked = False
        else:
            self.locked = True
    
    def pair_door_down(self, door_down):
        self.door_down = door_down

    def update_sprite(self, is_hovered : bool, color : tuple = (150, 150, 255)):
        """Update the sprite of the door by playing the animation."""
        if self.anim != self.anim_open and self.anim_close.is_finished():     # Check if the animation is finished
            if is_hovered:
                self.anim = self.anim_blink
            else:           # Delete the blinking animation after closing when the mouse isn't on the door
                self.surf = sprite.SPRITESHEET_DOOR_BLINK.get_img((0,0))
                self.anim = None
    
        super().update_sprite(is_hovered, color)

        if is_hovered:
            label_surf = TERMINAL_FONT.render("Monter", False, STANDARD_COLOR)
            label_surf_rect = label_surf.get_rect(center = self.surf.get_rect().center)
            self.temp_surf.blit(label_surf, label_surf_rect)

        if self.locked:
            self.temp_surf.blit(self.locked_surf, (3,3) if is_hovered else (0,0)) # Draw the lock on the door (offset if hovered because of the outline)
    
    def interaction(self, timer : TimerManager):
        """Interaction with the door.  
        This method is called when the player clicks on the door.
        It links to the other door and plays the animation."""
        self.anim_open.reset_frame()        #reset all animations when the mouse is on the door to expect the change of floor
        self.anim_close.reset_frame()
        self.anim = self.anim_open
        self.door_down.anim_open.reset_frame()
        self.door_down.anim_close.reset_frame()
        self.door_down.anim = self.door_down.anim_open
        

        timer.create_timer(1.5, self.set_attribute, arguments=('anim', self.anim_close))        #set the duration of the animation
        timer.create_timer(1.5, self.door_down.set_attribute, arguments=('anim', self.door_down.anim_close))

class DoorDown(Placeable):
    """Class for the door down placeable.  
    Only one instance of this class is shared between all floors."""
    def __init__(self, name, coord, surf, tag = None):
        super().__init__(name, coord, surf, tag)
        self.anim_close = Animation(sprite.SPRITESHEET_BAS_FLIP, 0, 9, 4, False)        #download closing animation
        self.anim_open = Animation(sprite.SPRITESHEET_HAUT_FLIP, 0, 7, 4, False)        #download oppening animation
        self.anim_blink = Animation(sprite.SPRITESHEET_DOOR_BLINK_FLIP, 0, 10)          #download blink animation
        self.anim = self.anim_close
        _rect = self.anim.get_frame().get_rect()
        self.rect.width, self.rect.height = _rect.width, _rect.height
        self.door_up : Optional[DoorUp] = None
        self.locked = True

        self.locked_surf = sprite.get_locked_surface(sprite.SPRITESHEET_DOOR_BLINK_FLIP.get_img((0,0)))       #create a locked door surface

    def update_lock_status(self, unlock_manager : UnlockManager, current_room):
        if unlock_manager.is_floor_unlocked(str(current_room.num-1)):
            self.locked = False
        else:
            self.locked = True
    
    def pair_door_up(self, door_up):
        self.door_up = door_up
    
    def update_sprite(self, is_hovered : bool, color : tuple = (150, 150, 255)):
        if self.anim != self.anim_open and self.anim_close.is_finished():       #check if the animation is finish
            if is_hovered:
                self.anim = self.anim_blink
            else:           #delete the blinking animation after closing when the mouse isn't on the door
                self.surf = sprite.SPRITESHEET_DOOR_BLINK_FLIP.get_img((0,0))
                self.anim = None
    
        super().update_sprite(is_hovered, color)

        if is_hovered: # simple label on the door
            label_surf = TERMINAL_FONT.render("Decendre", False, STANDARD_COLOR)
            label_surf_rect = label_surf.get_rect(center = self.surf.get_rect().center)
            self.temp_surf.blit(label_surf, label_surf_rect)

        if self.locked:
            self.temp_surf.blit(self.locked_surf, (3,3) if is_hovered else (0,0)) # Draw the lock on the door (offset if hovered because of the outline)
    
    def interaction(self, timer : TimerManager):
        """Interaction with the door.  
        This method is called when the player clicks on the door.  
        It links to the other door and plays the animation."""
        self.anim_open.reset_frame()        #reset all animations when the mouse is on the door to expect the change of floor
        self.anim_close.reset_frame()
        self.anim = self.anim_open
        self.door_up.anim_open.reset_frame()
        self.door_up.anim_close.reset_frame()
        self.door_up.anim = self.door_up.anim_open
        

        timer.create_timer(1.5, self.set_attribute, arguments=('anim', self.anim_close))        #set the duration of the animation
        timer.create_timer(1.5, self.door_up.set_attribute, arguments=('anim', self.door_up.anim_close))
        

class BotPlaceable(Placeable):
    """Class for the clickable inline bot."""
    pass

class ShopPlaceable(Placeable):
    """Class for the shop placeable at floor 2."""
    pass

class InvPlaceable(Placeable):
    """Class for the inventory placeable at floor 1."""
    def __init__(self, name, coord, surf, tag = None):
        super().__init__(name, coord, surf, tag)
        self.blink_anim = Animation(sprite.SPRITESHEET_INVENTORY, 0, 7)
        self.surf = self.blink_anim.get_frame()
    
    def update_sprite(self, is_hovered, color = (150, 150, 255)):
        if is_hovered:
            self.surf = self.blink_anim.get_frame()
        else:
            self.surf = sprite.SPRITESHEET_INVENTORY.get_img((0,0))

        super().update_sprite(is_hovered, color)

        if is_hovered: # simple label on the inventory
            label_surf = TERMINAL_FONT.render("Inventaire", False, STANDARD_COLOR)
            label_surf_rect = label_surf.get_rect(center = self.surf.get_rect().center)
            self.temp_surf.blit(label_surf, label_surf_rect)

class AutoCachierPlaceable(Placeable):
    """Class for the automatic cash register unlock at floor 4."""
    pass

class ColorUnlockPlaceable(Placeable):
    """Class for the color unlock placeable at floor 3."""
    pass

class SpectatorPlaceable(Placeable):
    def __init__(self, name, coord, surf, config, tag = None):
        super().__init__(name, coord, surf, tag)
        from ui.userlist import UserList
        from utils.database import Database
        self.database = Database(config['server']['ip'], config['server']['port'], []) # Create to the database to fetch for spectator data
        self.user_list = UserList(self.coord.xy, self.database.fetch_all_user_data()) # Create the user list needed for the spectator
        self.open = False
        
    def interaction(self):
        self.open = not self.open # Toggle the spectator window
        if self.open:
            self.user_list.init(self.database.fetch_all_user_data()) # Fetch the data from the database

class DeskPlaceable(Placeable):
    """Class for the unique desk placeable at floor 1."""
    def __init__(self, name, coord, surf, tag = None):
        super().__init__(name, coord, surf, tag)
        self.auto_cachier_unlocked = False

        self.anim_bg = Animation(sprite.DESK_BG, 0, 14, speed=3, repeat=False)
        self.anim_fg = Animation(sprite.DESK_FG, 0, 14, speed=3, repeat=False)
        self.special_auto_guichet_bg = Animation(sprite.DESK_ROBOT_BG, 0, 14, speed=3, repeat=False)
        self.surf = self.anim_bg.reset_frame()
        self.fg_surf = self.anim_fg.reset_frame()

        self.surf.blit(self.fg_surf, (0,0))

        self.active = False

    def update_sprite(self, is_hovered, color = ...):
        """Update the sprite of the desk by playing the animation."""
        if self.auto_cachier_unlocked:
            self.anim_bg = self.special_auto_guichet_bg

        if self.anim_bg.is_finished():
            self.active = False
            self.surf = self.anim_bg.reset_frame()
            self.fg_surf = self.anim_fg.reset_frame()

        if self.active:
            self.surf = self.anim_bg.get_frame()
            self.fg_surf = self.anim_fg.get_frame()
        
        self.surf.blit(self.fg_surf, (0,0))
        
        self.temp_surf = self.surf.copy()
        self.temp_rect = self.rect.copy()
    
    def draw_foreground(self, win : Surface):
        """Draws the special foreground of the desk.  
        Needed because this part needs to be drawn on top of the bots."""
        win.blit(self.fg_surf, self.coord.xy)


