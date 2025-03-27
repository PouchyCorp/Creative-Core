r"""
Projet : Creative Core
Equipe : Paul Baumard, Abel Bossard, Tybalt Debruyne, Taddeo Boisseuil-Marcil
                   __ _                      _   _                 
                  / _(_)                    | | (_)                
   ___ ___  _ __ | |_ _ _ __ _ __ ___   __ _| |_ _  ___  _ __  ___ 
  / __/ _ \| '_ \|  _| | '__| '_ ` _ \ / _` | __| |/ _ \| '_ \/ __|
 | (_| (_) | | | | | | | |  | | | | | | (_| | |_| | (_) | | | \__ \
  \___\___/|_| |_|_| |_|_|  |_| |_| |_|\__,_|\__|_|\___/|_| |_|___/

Key Features:
-------------
- Handles the creation of a confirmation popup.
- Draws a question and yes / no buttons for user interaction.
- Each button can be assigned a function to be executed on click, usually to confirm or cancel an action.
- Just need to be inserted by anything into Game class's confirmation_popups attribute, and it will be handled automatically.

Author: Pouchy (Paul)
"""


import pygame as pg
from utils.coord import Coord
from ui.sprite import WINDOW, nine_slice_scaling, YES_BUTTON, NO_BUTTON
from utils.fonts import TERMINAL_FONT_BIG, STANDARD_COLOR

class ConfirmationPopup:
    def __init__(self, screen : pg.Surface, question : str, yes_func, no_func = None, yes_func_args : list = [], no_func_args : list = []):
        """
        Initialize the confirmation popup.  
        yes_func and no_func are the functions to be executed when the respective buttons are clicked.  
        yes_func_args and no_func_args are the arguments to be passed to the functions.
        """
        self.screen = screen
        self.question = question
        self.font = TERMINAL_FONT_BIG
        self.background : pg.Surface = nine_slice_scaling(WINDOW,(600,200), (12, 12, 12, 12))
        
        self.yes_button = self._create_button(yes_func, yes_func_args, YES_BUTTON)
        self.no_button = self._create_button(no_func, no_func_args ,NO_BUTTON)

        self.width, self.height = self.background.get_rect().width, self.background.get_rect().height

        self.rect = pg.Rect(
            (screen.get_width() - self.width) // 2,
            (screen.get_height() - self.height) // 2,
            self.width,
            self.height
        )

        self.yes_button["rect"].center = (
            self.rect.centerx - self.rect.width // 4, 
            self.rect.centery + self.rect.height // 6
        )
        self.no_button["rect"].center = (
            self.rect.centerx + self.rect.width // 4, 
            self.rect.centery + self.rect.height // 6
        )

    def _create_button(self, button_func, action_args : list, image : pg.Surface, hover_image = None) -> dict:
        """Create a button dictionary with image, hover image, and action."""
        return {
            "image": image,
            "hover_image": hover_image if hover_image else image,
            "action": button_func,
            "action_args" : action_args,
            "rect": image.get_rect()
        }

    def draw(self, mouse_pos : Coord):
        """Draw the popup, including background, question, and buttons."""
        self.screen.blit(self.background, self.rect.topleft)

        question_surface = self.font.render(self.question, True, STANDARD_COLOR)
        question_rect = question_surface.get_rect(center=(self.rect.centerx, self.rect.top + self.rect.height // 3))
        self.screen.blit(question_surface, question_rect)

        # Draw buttons
        for button in [self.yes_button, self.no_button]:
            image = button["hover_image"] if button["rect"].collidepoint(mouse_pos.xy) else button["image"]
            self.screen.blit(image, button["rect"].topleft)

    def handle_click(self, mouse_pos : Coord):
        """Handle mouse events for the buttons. 
        Returns True if 'yes' clicked
                False if 'no' clicked
                None if no event"""
        for button in [self.yes_button, self.no_button]:
            if button["rect"].collidepoint(mouse_pos.xy):
                if button["action"] and button['action_args']:
                    button["action"](*button['action_args'])
                elif button["action"]:
                    button["action"]()
                return True if button is self.yes_button else False
        return None
