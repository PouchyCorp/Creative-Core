r"""
Projet : Creative Core
Equipe : Paul Baumard, Abel Bossard, Tybalt Debruyne, Taddeo Boisseuil-Marcil
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

author of this module: Leih (Abel), Pouchy (Paul), Tioh (Taddeo)
"""


from objects.dialogue import DialogueManager
import pygame as pg
from ui.sprite import load_spritesheet_image, MAIN_CHARACTER
from typing_extensions import TYPE_CHECKING
from math import pi, sin
from utils.coord import Coord
from utils.fonts import TERMINAL_FONT_VERYBIG, STANDARD_COLOR

# Very ugly, but it's the only way to avoid circular imports
if TYPE_CHECKING:
    from core.logic import Game 

class CinematicPlayer:
    """Class for playing cinematics."""
    def __init__(self, config_dict : dict[str, tuple[str, str, str]]):

        if "anim" in config_dict:
            self.anim_lst, self.anim_len = load_spritesheet_image(config_dict["anim"])
            self.cutscene_surf = self.anim_lst[0]
        else:
            self.anim_lst = None

            # setups the final surface like in __play_anim for the cutscene if there is no animation
            self.cutscene_final_surf = pg.Surface((1920, 1080), pg.SRCALPHA)
            band_size = (1920, 120)
            black_band = pg.Surface(band_size)
            self.cutscene_final_surf.blit(black_band, (0, 0))
            self.cutscene_final_surf.blit(black_band, (0, 1080 - band_size[1]))
            self.cutscene_final_surf = pg.transform.grayscale(self.cutscene_final_surf)
            

        if "dialogue" in config_dict:
            self.dialogue_name, self.npc_icon, self.npc_name = config_dict["dialogue"]
        else:
            self.dialogue_name = None
        
        if "introspec" in config_dict:
            self.introspection_dialogue = config_dict["introspec"]
        else:
            self.introspection_dialogue = None
            
        self.dialogue = DialogueManager()
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
        band_size = (game.win.get_width(), 120)
        black_band = pg.Surface(band_size)
        clock = pg.time.Clock()
        anim_incr = 0        # Loop until the animation is finished or the cinematic is marked as finished
        while anim_incr//10 < self.anim_len and not self.is_finished:
            clock.tick(60)  # Cap the frame rate at 60 FPS
            for event in pg.event.get():
                # Handle status events like quitting or pressing escape
                self.get_status_event(event, game)

            # Get the current frame of the animation
            self.cutscene_surf = self.anim_lst[anim_incr//10]
            anim_incr += 1
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
            self.dialogue.update(self.npc_name)
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
            self.dialogue.update("self")
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
                # Second half of the transition: draw the normal game background
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
        if self.anim_lst:
            self.__play_anim(game)

        # If there is a dialogue name, play the dialogue sequence
        if self.dialogue_name:
            self.dialogue.special_dialogue(self.dialogue_name)
            self.dialogue.npc_icon = self.npc_icon
            self.__play_dialogue(game)

        # Play the transition sequence
        self.__play_transition(game)

        # If there is an introspection dialogue, play the introspection dialogue sequence
        if self.introspection_dialogue:
            self.dialogue.special_dialogue(self.introspection_dialogue)
            self.dialogue.npc_icon = MAIN_CHARACTER
            self.__play_introspection_dialogue(game)

        # Mark the cinematic as finished
        self.is_finished = True

    

class IntroCutscene:
    """Simple class for playing the intro IntroCutscene."""
    def __init__(self, frames : list[pg.Surface]):
        self.frames = frames

    def transition(self, game : 'Game', current_frame : pg.Surface, next_frame : pg.Surface, time : float = 2):
        """Simple fade-in-out transition between one frame to another, can be easily used at other places.  
        Reimplementation of the __play_transition method above"""
        clock = pg.time.Clock()
        mask = pg.Surface((game.win.get_width(), game.win.get_height()))
        mask.fill((0, 0, 0))
        incr = 0
        step_count = time * 60  # Number of steps for the transition

        while incr < pi:
            clock.tick(60)
            incr += pi / step_count  # Increment the angle for the sine function

            if incr < pi / 2:
                # First half of the transition: draw the current cutscene and dialogue
                game.win.blit(current_frame, (0,0))
            else:
                # Second half of the transition: draw the normal game background
                game.win.blit(next_frame, (0,0))

            # Use the sine function to create a smooth fade out effect
            # sin(incr) varies from 0 to 1 as incr goes from 0 to pi/2, and from 1 to 0 as incr goes from pi/2 to pi
            mask.set_alpha(sin(incr) * 255)
            game.win.blit(mask, (0, 0))
            pg.display.flip()
        
        return next_frame
    
    def play(self, game : 'Game', initial_background : pg.Surface):
        """Plays the intro cutscene."""
        frame_ind = 0
        current_frame = self.frames[frame_ind]
        skip_label = TERMINAL_FONT_VERYBIG.render("Cliquez pour passer", False, STANDARD_COLOR)
        
        clock = pg.time.Clock()

        self.transition(game, initial_background, current_frame, 3) # transition from the home screen to the first frame
         
        while frame_ind < len(self.frames):
            clock.tick(60)
            for event in pg.event.get():
                if event.type == pg.KEYDOWN or event.type == pg.MOUSEBUTTONDOWN:
                    frame_ind += 1
                    if frame_ind >= len(self.frames): # if we reached the end of the frames
                        break

                    current_frame = self.transition(game, current_frame, self.frames[frame_ind], 1.5) # transition between the frames
            
            game.win.blit(current_frame, (0,0))
            game.win.blit(skip_label, (0,0))
            # Draw the background and the current state of the introspection dialogue
            pg.display.flip()
        
        self.transition(game, current_frame, pg.Surface((1920, 1080)), 3) # transition to the game background

            
    
