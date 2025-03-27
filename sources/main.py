r"""
Projet : Creative Core
Equipe : Paul Baumard, Abel Bossard, Tybalt Debruyne, Taddeo Boisseuil-Marcil
  _                            _               
 | |                          | |              
 | |     __ _ _   _ _ __   ___| |__   ___ _ __ 
 | |    / _` | | | | '_ \ / __| '_ \ / _ \ '__|
 | |___| (_| | |_| | | | | (__| | | |  __/ |   
 |______\__,_|\__,_|_| |_|\___|_| |_|\___|_|   

This module loads config, initializes Pygame and starts the game.

Key Features:
-------------
- Loading screen when loading the assets.
- Loads configuration from a TOML file.
- Has multiple game modes (online and offline).
- Loads saved game data from a database.
- Saves game data to a database.

Notes:
------
The main loop is in sources/core/logic.py

Author: Pouchy (Paul), Ytyt (Tybalt) for the database branching part
"""

import pygame as pg
import tomli

# Load configuration file
with open('sources/config.toml', 'rb') as f:
    config = tomli.load(f)

def create_display():
    """
    Creates and returns the game window and a transparent surface for rendering.
    """
    if config['screen']['fullscreen']:
        win = pg.display.set_mode((0, 0), pg.FULLSCREEN)
    else:
        win = pg.display.set_mode(config['screen']['size'])
    
    transparency_win = win.convert_alpha()
    transparency_win.fill((0, 0, 0, 0))

    return win, transparency_win, load_assets(win, config) # Return the window, transparency window and the sound manager

def load_assets(win, config):
    """
    Loads the game assets and displays a loading screen while doing so.
    This is done to prevent the game from freezing while loading.
    """

    pg.mixer.init()

     # Loading backgound while the sounds and sprites load.
    win.blit(pg.image.load('data/loading_bg.png'),(0,0))
    pg.display.flip()

    import ui.sprite # Importing the sprites to load them
    import utils.sound

    return utils.sound.SoundManager(config['sound']['volume'], int) # Just to load the sounds, int is a dummy function

def place_inventory_items(game_save_dict, rooms):
    """
    Places saved inventory items in their respective rooms.
    """
    for placeable in game_save_dict['inventory']:
        if placeable.placed:
            rooms[placeable.coord.room_num].placed.append(placeable)

def start_game(game_save_dict, win, transparency_win, last_frame_of_homescreen, sound_manager):
    """
    Initializes and starts the game loop with the provided save data.
    """
    pg.init()

    pg.display.set_icon(pg.image.load('data/big_icon.png'))
    pg.display.set_caption('Creative Core')

    from core.logic import Game
    from utils.room_config import ROOMS
    
    place_inventory_items(game_save_dict, ROOMS)
    
    # Initialize the game with saved data
    game = Game(win, config, game_save_dict['inventory'], game_save_dict['shop'],
                game_save_dict['gold'], game_save_dict['unlocks'], transparency_win, last_frame_of_homescreen, sound_manager)
    
    return game.main_loop()

def main():
    """
    Oversees the game flow, handling login if necessary.
    """
    win, transparency_win,sound_manager  = create_display()

    while True:
        if not config['gameplay']['offline_mode']: # If online mode is enabled
            from core.homescreen import OnlineHomescreen
            homescreen = OnlineHomescreen(config['server']['ip'], config['server']['port']) 
            username, user_game_data, last_frame_of_homescreen = homescreen.main_loop(win) # Display online homescreen and get user's save data when they log in
            
            print('Launching game...')
            data_to_save = start_game(user_game_data, win, transparency_win, last_frame_of_homescreen, sound_manager) # Start game with user's save data
            
            print('Saving game...')
            homescreen.database.save_user_data(username, data_to_save) # Save game data to database on the right user

        else: # If offline mode is enabled
            from utils.room_config import DEFAULT_SAVE
            from core.homescreen import OfflineHomescreen
            last_frame_of_homescreen = OfflineHomescreen().main_loop(win) # Display offline homescreen
            start_game(DEFAULT_SAVE, win, transparency_win, last_frame_of_homescreen, sound_manager) # Start game with default save data

if __name__ == "__main__": 
    main() # Run the game
