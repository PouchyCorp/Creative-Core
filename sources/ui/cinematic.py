r"""
             _                                
            | |                               
   ___ _   _| |_ ___  ___ ___ _ __   ___  ___ 
  / __| | | | __/ __|/ __/ _ \ '_ \ / _ \/ __|
 | (__| |_| | |_\__ \ (_|  __/ | | |  __/\__ \
  \___|\__,_|\__|___/\___\___|_| |_|\___||___/

Key Features:
-------------
- Plays animations for cinematics using a configurable dictionary.
- Customizes the dialogue, animation, and additional post-cutscene dialogue for each cinematic.
- Handles transitions with sinus function for smooth fade-out effects.
- Is used for:
    introspection dialogues for character development.
    cutscenes for story progression.

- Triggered by the game logic when a cinematic is required.
- Uses logic.py Game class methods to simulate the main game loop.
- Uses the DialogueManager class to handle dialogue interactions.

Cutscene stored in ui/sprite.py with the format:
    (name : (animation, dialogue_name, introspection_dialogue_name))

author: Leih (Abel)
"""


from objects.dialogue import DialogueManager
from utils.anim import Animation
import pygame as pg
from typing_extensions import TYPE_CHECKING
from math import pi, sin
from utils.coord import Coord

# Very ugly, but it's the only way to avoid circular imports
if TYPE_CHECKING:
    from core.logic import Game 

class CinematicPlayer:
    """Class for playing cinematics.
    Attributes need to be passed in strict order but can be omitted.
    However, if an attribute is omitted, the following attributes must be omitted as well. (Important because of the way the cinematics are stored in the game save file)"""
    def __init__(self, anim : Animation = None, dialogue_name = None, introspection_dialogue_name = None):
        self.anim = anim

        self.dialogue = DialogueManager()
        self.dialogue_name = dialogue_name
        self.introspection_dialogue = introspection_dialogue_name

        if self.anim:
            self.cutscene_surf = self.anim.reset_frame()
        else:
            self.cutscene_surf = pg.Surface((320*6, 180*6), pg.SRCALPHA) # Create a blank surface if there is no animation so that the dialogue can be drawn on it
        self.is_finished = False
    
    def get_status_event(self, event, game):
        """Handle status events like quitting or pressing escape."""
        if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
            self.is_finished = True
        elif event.type == pg.QUIT:
            game.quit()
    
    def get_dialogue_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            return self.dialogue.click_interaction()
            
    def __play_anim(self, game : 'Game'): # 'Game' is a forward reference (PEP 18)
        """Play the animation sequence."""
        # Define the size of the black bands at the top and bottom of the screen
        band_size = (game.win.get_width(), 140)
        black_band = pg.Surface(band_size)
        clock = pg.time.Clock()
        
        # Loop until the animation is finished or the cinematic is marked as finished
        while not self.anim.is_finished() and not self.is_finished:
            clock.tick(60)  # Cap the frame rate at 60 FPS
            for event in pg.event.get():
                # Handle status events like quitting or pressing escape
                self.get_status_event(event, game)

            # Get the current frame of the animation
            self.cutscene_surf = self.anim.get_frame()
            # Draw black bands at the top and bottom of the screen
            self.cutscene_surf.blit(black_band, (0, 0))
            self.cutscene_surf.blit(black_band, (0, 1080 - band_size[1]))
            
            # Draw the background and the current frame of the animation
            game.draw_background()
            game.win.blit(self.cutscene_surf, (0, 0))
            pg.display.flip()
        
        # Convert the final frame to grayscale
        self.cutscene_final_surf = pg.transform.grayscale(self.cutscene_surf)
    
    def __play_dialogue(self, game : 'Game'):
        """Play the dialogue sequence."""
        clock = pg.time.Clock()
        finised_reading = False
        while not finised_reading and not self.is_finished:
            # Cap the frame rate at 60 FPS
            clock.tick(60)
            for event in pg.event.get():
                # Handle status events like quitting or pressing escape
                self.get_status_event(event, game)
                # Handle dialogue events like mouse clicks and check if finished reading
                finised_reading = self.get_dialogue_event(event)
            
            # Update the dialogue state
            self.dialogue.update()
            # Draw the background and the current state of the dialogue
            game.draw_background()
            game.win.blit(self.cutscene_final_surf, (0,0))
            self.dialogue.draw(game.win)
            pg.display.flip()
        

    
    def __play_introspection_dialogue(self, game : 'Game'):
        """Play the introspection dialogue."""
        clock = pg.time.Clock()
        while not self.dialogue.selected_dialogue.is_on_last_part() and not self.is_finished:
            clock.tick(60)
            for event in pg.event.get():
                # Handle status events like quitting or pressing escape
                self.get_status_event(event, game)
                # Handle dialogue events like mouse clicks
                self.get_dialogue_event(event)
            
            # Update the dialogue state
            self.dialogue.update()
            # Draw the background and the current state of the introspection dialogue
            game.draw(Coord(0, (0, 0)))
            self.dialogue.draw(game.win)
            pg.display.flip()

    def __play_transition(self, game : 'Game'):
        """Play a simple fade out transition"""
        clock = pg.time.Clock()
        mask = pg.Surface((game.win.get_width(), game.win.get_height()))
        mask.fill((0, 0, 0))
        incr = 0
        step_count = 2 * 60  # Number of steps for the transition

        while incr < pi and not self.is_finished:
            clock.tick(60)
            incr += pi / step_count  # Increment the angle for the sine function

            for event in pg.event.get():
                self.get_status_event(event, game)

            if incr < pi / 2:
                # First half of the transition: draw the current cutscene and dialogue
                game.draw_background()
                game.win.blit(self.cutscene_final_surf, (0, 0))
                self.dialogue.draw(game.win)
            else:
                # Second half of the transition: draw the introspection dialogue
                game.draw(Coord(0, (0, 0)))

            # Use the sine function to create a smooth fade out effect
            # sin(incr) varies from 0 to 1 as incr goes from 0 to pi/2, and from 1 to 0 as incr goes from pi/2 to pi
            mask.set_alpha(sin(incr) * 255)
            game.win.blit(mask, (0, 0))
            pg.display.flip()

    def play(self, game : 'Game'):
        """Plays the cutscene sequence.
        The sequence is played in this order:
        - Animation (with black bands at the top and bottom of the screen)
        - Main dialogue (with last frame of the animation in the background)
        - Transition (fade in-out effect)
        - Introspection dialogue (with the normal game background)
        """
        # Play the animation sequence
        if self.anim:
            self.__play_anim(game)

        # If there is a dialogue name, play the dialogue sequence
        if self.dialogue_name:
            self.dialogue.special_dialogue(self.dialogue_name)
            self.__play_dialogue(game)

        # Play the transition sequence
        self.__play_transition(game)

        # If there is an introspection dialogue, play the introspection dialogue sequence
        if self.introspection_dialogue:
            self.dialogue.special_dialogue(self.introspection_dialogue)
            self.__play_introspection_dialogue(game)

        # Mark the cinematic as finished
        self.is_finished = True
    
