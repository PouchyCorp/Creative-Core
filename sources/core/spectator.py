r"""
Projet : Creative Core
Equipe : Paul Baumard, Abel Bossard, Tybalt Debruyne, Taddeo Boisseuil-Marcil
                      _        _             
                     | |      | |            
  ___ _ __   ___  ___| |_ __ _| |_ ___  _ __ 
 / __| '_ \ / _ \/ __| __/ _` | __/ _ \| '__|
 \__ \ |_) |  __/ (__| || (_| | || (_) | |   
 |___/ .__/ \___|\___|\__\__,_|\__\___/|_|   
     | |                                     
     |_|          

Key Features:
-------------
- Launches a separate autonomous window to spectate a game save.
- Handles navigation between unlocked floors but not interaction. 
- Uses the same game save as the normal game, to enhance usability.

Author: Ytyt (Tybalt)
"""


import pygame as pg
import tomli
from utils.coord import Coord
from utils.room_config import init_rooms
from ui.sprite import ARROW_LEFT, ARROW_RIGHT, whiten, QUIT_BUTTON
from ui.button import Button
from ui.infopopup import InfoPopup

class Spectator:
    """Class to manage all the spectator mode :
    It create the museum with no functionality except moving inter floors"""
    def __init__(self, game_save_dict):
        self.username, self.game_save_dict = game_save_dict
        print("spectating : ", self.username)
        
        self.rooms = init_rooms()[0] # Initialize the rooms from the room_config module
        self.current_room = self.rooms[1]
        
        self.run = True

        with open('sources/config.toml', 'rb') as f:
            self.config = tomli.load(f)
        
        # Set up the display window with specified resolution using the config file
        if self.config['screen']['fullscreen']:
            self.WIN = pg.display.set_mode((0, 0), pg.FULLSCREEN)
        else:
            self.WIN = pg.display.set_mode(self.config['screen']['size'])

        pg.display.set_icon(pg.image.load('data/big_icon.png'))

        self.CLOCK = pg.time.Clock()
        pg.display.set_caption('Creative Core')

        self.popups : list[InfoPopup] = []
        #to floor up
        self.up_button = Button((10,10), self.go_floor_up, 
                        whiten(pg.transform.rotate(ARROW_RIGHT, 90)), 
                        pg.transform.rotate(ARROW_RIGHT, 90))
        #to floor down
        self.down_button = Button((10,100), self.go_floor_down, 
                            whiten(pg.transform.rotate(ARROW_LEFT, 90)), 
                            pg.transform.rotate(ARROW_LEFT, 90))
        #Allow to quit
        self.quit_button = Button((0, self.WIN.get_rect().bottom-QUIT_BUTTON.get_height()), self.quit,   
                            whiten(QUIT_BUTTON), 
                            QUIT_BUTTON)

        # Places placeables in room from inventory
        for placeable in self.game_save_dict['inventory']:
            if placeable.placed:
                self.rooms[placeable.coord.room_num].placed.append(placeable)
    
    def quit(self):
        """Quit the game"""
        self.run=False
        print("quitting spectating : ", self.username)

    def go_floor_up(self):
        """to move up : 1
            to move down : -1"""
        if self.game_save_dict["unlocks"].is_floor_unlocked(str(self.current_room.num + 1)):
            self.current_room = self.rooms[self.current_room.num + 1]  # Move to the previous room
        else:
            self.popups.append(InfoPopup("you can't go off limits"))  # Show popup if trying to go below limits

    def go_floor_down(self):
        """to move up : 1
            to move down : -1"""
        if self.game_save_dict["unlocks"].is_floor_unlocked(str(self.current_room.num - 1)):
            self.current_room = self.rooms[self.current_room.num - 1]  # Move to the previous room
        else:
            self.popups.append(InfoPopup("you can't go off limits"))  # Show popup if trying to go below limits


    def start_spectating(self):
        # Open config file and dump it in a dict
        pg.init()

        fps = self.config['gameplay']['fps']  # Frame rate
        while self.run:
            self.CLOCK.tick(fps)  # Maintain frame rate
            # Create a coordinate object for the mouse position
            mouse_pos: Coord = Coord(self.current_room.num, pg.mouse.get_pos())
            events = pg.event.get()  # Get all events from the event queue

            for event in events:
                if event.type == pg.QUIT:  # Check for quit event
                    self.run = False

                self.up_button.handle_event(event)
                self.down_button.handle_event(event)
                self.quit_button.handle_event(event)

            for plbl in self.current_room.placed:
                plbl.update_sprite(False)
            
            self.WIN.blit(self.current_room.bg_surf, (0, 0))
            self.current_room.draw_placed(self.WIN)
            self.up_button.draw(self.WIN, self.up_button.rect.collidepoint(mouse_pos.xy))
            self.down_button.draw(self.WIN, self.down_button.rect.collidepoint(mouse_pos.xy))
            self.quit_button.draw(self.WIN, self.quit_button.rect.collidepoint(mouse_pos.xy))

            for popup in self.popups:
                if popup.lifetime <= 0:
                    self.popups.remove(popup)
                else:
                    popup.draw(self.WIN)

            pg.display.flip()  # Update the display

