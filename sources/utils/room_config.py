r"""
Projet : Creative Core
Equipe : Paul Baumard, Abel Bossard, Tybalt Debruyne, Taddeo Boisseuil-Marcil
                                               __ _       
                                              / _(_)      
  _ __ ___   ___  _ __ ___     ___ ___  _ __ | |_ _  __ _ 
 | '__/ _ \ / _ \| '_ ` _ \   / __/ _ \| '_ \|  _| |/ _` |
 | | | (_) | (_) | | | | | | | (_| (_) | | | | | | | (_| |
 |_|  \___/ \___/|_| |_| |_|  \___\___/|_| |_|_| |_|\__, |
                                                     __/ |
                                                    |___/ 

This module contains the default configuration for the rooms in the game.
The initialization of the rooms is done in the init_rooms() function and not directly at the top level of the module to allow for making 
copies of the rooms without reinitializing them (because shared by the main game and spectator mode).

Author: Pouchy (Paul), Leih (Abel)
"""

from utils.coord import Coord
from objects.placeable import Placeable
from core.room import Room
import ui.sprite as sprite
from pygame import Surface, SRCALPHA
import objects.placeablesubclass as subplaceable
from core.unlockmanager import UnlockManager
from utils.anim import Animation
from objects.particlesspawner import ConfettiSpawner

def init_rooms():
    """Init every rooms, whit the numbers of every round, wallpapers, placeables, stairs, inventory..."""
    # init doors
    stairs_up = subplaceable.DoorUp(
        'R1_stairs', Coord(1, (1594, 546)), Surface((335, 220)))
    stairs_down = subplaceable.DoorDown('R1_stairs_down', Coord(
        1, (1594, 516 + 33*6)), Surface((335, 220)))

    stairs_down.pair_door_up(stairs_up)
    stairs_up.pair_door_down(stairs_down)

    # floor 0
    R0 = Room(0, sprite.BG2)
    R0.placed += [stairs_up]
    R0.blacklist += [stairs_up]

    # floor 1
    R1 = Room(1, sprite.BG1)
    guichet = subplaceable.DeskPlaceable('guichet', Coord(1, (470+30, 692)), Surface((0,0)))
    collider = Placeable('collider', Coord(1, (0, 0)), Surface((798, 1080), flags=SRCALPHA), "collider", flags=['no_outline', 'no_interaction'])
    inventory = subplaceable.InvPlaceable(
        "Inventory", Coord(1, (1548, 210)), Surface((53*6, 31*6)))
    R1.placed += [guichet, stairs_up, stairs_down, inventory, collider]
    R1.blacklist += [stairs_up, stairs_down, inventory, guichet, collider]

    # floor 2
    R2 = Room(2, sprite.BG3)
    shop = subplaceable.ShopPlaceable('shop', Coord(
        2, (48, 468)), sprite.SHOP, "shop")
    R2.placed += [stairs_up, stairs_down, shop, inventory]
    R2.blacklist += [stairs_up, stairs_down, shop, inventory]

    # floor 3
    R3 = Room(3, sprite.BG4)
    color_unlock = subplaceable.ColorUnlockPlaceable('ColorUnlockPlaceable', Coord(3, (48, 468+24)), sprite.COLOR_NPC)
    R3.placed += [stairs_up, stairs_down, inventory, color_unlock]
    R3.blacklist += [stairs_up, stairs_down, inventory, color_unlock]

    # floor 4
    R4 = Room(4, sprite.BG5)
    auto_cachier = subplaceable.AutoCachierPlaceable(
        'AutoCachierPlaceable', Coord(1, (1398, 574)), sprite.CACHIER_NPC)
    R4.placed += [stairs_up, stairs_down, auto_cachier, inventory]
    R4.blacklist += [stairs_up, stairs_down, auto_cachier, inventory]

    # floor 5
    R5 = Room(5, anim=Animation(sprite.SPRITESHEET_ROOFTOP, 0, 14, 8))
    music_robot = Placeable('Johnny Hallyday 2.0', Coord(5,(240,780)), None, anim=sprite.ANIM_ROBOT_MUSIC) #Place the musician bot
    R5.placed += [stairs_down, music_robot]
    R5.blacklist += [stairs_down, music_robot]

    special_placeables = {'staires_up' : stairs_up, 'staires_down' : stairs_down, 'guichet' : guichet, 'inventory' : inventory, 'shop' : shop, 'auto_cachier' : auto_cachier, 'music_robot' : music_robot, 'color_unlock' : color_unlock} #used to access special placeables in the game loop

    return [R0, R1, R2, R3, R4, R5], special_placeables 


ROOMS, SPECIAL_PLACEABLES = init_rooms()

# Assigning rooms to variables for easier access
R0 = ROOMS[0]
R1 = ROOMS[1]
R2 = ROOMS[2]
R3 = ROOMS[3]
R4 = ROOMS[4]
R5 = ROOMS[5]

offset = -18
# IMPORTANT: THIS IS THE DEFAULT SAVE DATA
# Setup every settings for the beginning of the game 
DEFAULT_SAVE = {'gold': 10,
                "beauty": 0,
                "inventory": [],

                #Place all the items from the shop with ther price and their number of beauty
                "shop": [Placeable('buste', Coord(2, (100, 100)), sprite.SPRITE_STATUE_1, "decoration", y_constraint=882, price=50, beauty=5),
                         Placeable('statue', Coord(2, (100, 100)), sprite.SPRITE_STATUE_2, "decoration", y_constraint=900-offset, price=170, beauty=17),
                         Placeable('plante', Coord(2, (100, 100)), sprite.SPRITE_PLANT_1, "decoration", y_constraint=938-offset, price=20, beauty=2),
                         Placeable('arbuste', Coord(2, (100, 100)), sprite.SPRITE_PLANT_2, "decoration", y_constraint=876-offset, price=25, beauty=2.5),
                         Placeable('affiche', Coord(2, (100, 100)), sprite.SPRITE_POSTER, "decoration", None, price=40, beauty=4),
                         Placeable('lustre', Coord(2, (100, 100)), sprite.SPRITE_SPHERE, "decoration", y_constraint=252, price=100, beauty=10),
                         Placeable('bocal', Coord(2, (100, 100)), sprite.SPRITE_DUCK, "decoration", y_constraint=864-offset, price=5, beauty=0.5),
                         Placeable('cube', Coord(2, (100, 100)), sprite.SPRITE_CUBE, "decoration", y_constraint=996-offset, price=15, beauty=1.5),
                         Placeable('fraises', Coord(2, (100, 100)), sprite.SPRITE_STRAWBERRIES, "decoration", y_constraint=876-offset, price=80, beauty=8),
                         Placeable('botte', Coord(2, (100, 100)), sprite.SPRITE_ROB, "decoration", y_constraint=906-offset, price=35, beauty=3.5),
                         Placeable('peinture', Coord(2, (100, 100)), sprite.SPRITE_PAINTING, "decoration", None, price=60, beauty=6),
                         Placeable('fleur lumineuse', Coord(2, (100, 100)), sprite.SPRITE_FLOWER_1, "decoration", y_constraint=888-offset, price=30, beauty=3),
                         Placeable('fleur', Coord(2, (100, 100)), sprite.SPRITE_FLOWER_2, "decoration", y_constraint=814-offset, price=10, beauty=1),
                         Placeable('vase', Coord(2, (100, 100)), sprite.SPRITE_VASE_1, "decoration", y_constraint=1020-offset, price=40, beauty=4),
                         Placeable('vase ancien', Coord(2, (100, 100)), sprite.SPRITE_VASE_2, "decoration", y_constraint=1032-offset, price=60, beauty=6),
                         Placeable('vase décoré', Coord(2, (100, 100)), sprite.SPRITE_VASE_3, "decoration", y_constraint=972-offset, price=120, beauty=12),
                         Placeable('lingot', Coord(2, (100, 100)), sprite.SPRITE_GOLD, "decoration", y_constraint=996-offset, price=250, beauty=25),
                         Placeable('orbe', Coord(2, (100, 100)), sprite.SPRITE_CELL, "decoration", y_constraint=912-offset, price=70, beauty=7),
                         Placeable('plantes murales', Coord(2, (100, 100)), sprite.SPRITE_SHELF_1, "decoration", None, price=10, beauty=1),
                         Placeable('plantes', Coord(2, (100, 100)), sprite.SPRITE_SHELF_2, "decoration", None, price=15, beauty=1.5)],

                "unlocks": UnlockManager()}

# The confetti rain when starting the game
# The key is the room number
PARTICLE_SPAWNERS = {0: [], 1: [ConfettiSpawner(Coord(1, (0, 0)), 300)], 2: [], 3: [], 4: [], 5: []}
