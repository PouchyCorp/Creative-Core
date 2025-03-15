r"""
  _                            _               
 | |                          | |              
 | |     __ _ _   _ _ __   ___| |__   ___ _ __ 
 | |    / _` | | | | '_ \ / __| '_ \ / _ \ '__|
 | |___| (_| | |_| | | | | (__| | | |  __/ |   
 |______\__,_|\__,_|_| |_|\___|_| |_|\___|_|   

This module loads config, initializes Pygame and starts the game.

Key Features:
-------------
- Loads configuration from a TOML file.
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
    return win, transparency_win

def setup_window():
    """
    Sets the window icon and title.
    """
    pg.display.set_icon(pg.image.load('data/big_icon.png'))
    pg.display.set_caption('Creative Core')

def place_inventory_items(game_save_dict, rooms):
    """
    Places saved inventory items in their respective rooms.
    """
    for placeable in game_save_dict['inventory']:
        if placeable.placed:
            rooms[placeable.coord.room_num].placed.append(placeable)

def start_game(game_save_dict):
    """
    Initializes and starts the game loop with the provided save data.
    """
    pg.init()
    pg.mixer.init()

    win, transparency_win = create_display()
    setup_window()
    from core.logic import Game
    from utils.room_config import ROOMS
    
    place_inventory_items(game_save_dict, ROOMS)
    
    # Initialize the game with saved data
    game = Game(win, config, game_save_dict['inventory'], game_save_dict['shop'],
                game_save_dict['gold'], game_save_dict['unlocks'], transparency_win)
    
    return game.main_loop()

def main():
    """
    Oversees the game flow, handling login if necessary.
    """
    if not config['gameplay']['offline_mode']:
        from core.homescreen import OnlineHomescreen
        homescreen = OnlineHomescreen(config['server']['ip'], config['server']['port'])
        username, user_game_data = homescreen.main_loop()
        
        print('Launching game...')
        data_to_save = start_game(user_game_data)
        
        print('Saving game...')
        homescreen.database.save_user_data(username, data_to_save)

    else:
        from utils.room_config import DEFAULT_SAVE
        from core.homescreen import OfflineHomescreen
        OfflineHomescreen().main_loop()
        start_game(DEFAULT_SAVE)

if __name__ == "__main__":
    main()
