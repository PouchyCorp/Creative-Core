r"""
Projet : Creative Core
Equipe : Paul Baumard, Abel Bossard, Tybalt Debruyne, Taddeo Boisseuil-Marcil
   _____            _ _            
  / ____|          (_) |           
 | (___  _ __  _ __ _| |_ ___  ___ 
  \___ \| '_ \| '__| | __/ _ \/ __|
  ____) | |_) | |  | | ||  __/\__ \
 |_____/| .__/|_|  |_|\__\___||___/
        | |                        
        |_|                        

This module contains all the sprite assets used in the game.

Key Features:
-------------
- Nine-slice algorithm scaling for UI elements.
- Whiten effect for surfaces, to be used as activated button sprites (to avoid having unnecessary files).

Author: Tioh (Taddeo), with some help from Ytyt for the inverse_kinematics function.
"""

from pygame import image, Surface, transform, SRCALPHA, BLEND_RGBA_MAX, display, Rect, BLEND_RGB_ADD, BLEND_RGBA_MULT, Vector2, surfarray
from math import sin, pi, sqrt, acos, atan2, degrees, cos
import utils.anim as anim
from objects.particlesspawner import ParticleSpawner, LineParticleSpawner
from utils.coord import Coord


if not display.get_init():
    display.set_mode((0,0))

def invert_alpha(surface):
    """
    Invert the alpha values of a surface.
    Intended to be used for the canva next_surf computing.
    Behaves unintuitively with not fully opaque or fully transparent pixels.
    
    This function takes a Pygame surface and inverts its alpha values, making
    fully transparent pixels fully opaque and vice versa.
    """
    alpha_array = surfarray.pixels_alpha(surface) # Uses Numpy arrays for performance reasons, Numpy is very useful for image processing

    """ 
    This works, but is too slow for large surfaces
    for i in range(len(alpha_array)):
        for j in range(len(alpha_array[i])):
            alpha_array[i][j] = 255 - alpha_array[i][j] 
    """
    
    alpha_array[:] = 255 - alpha_array[:] # This works better, but it's less readable, it's a Numpy feature called "broadcasting" that allows to apply an operation to all elements of an array at once (here, invert the alpha values) without using loops

def load_image(path : str):
    """ Custom routine to load, resize and optimize all sprites."""
    sprite = image.load(path)
    sized_sprite = transform.scale_by(sprite, 6)
    return sized_sprite.convert_alpha()

def load_spritesheet_image(path) -> tuple[list[Surface], int]:
    """ resize and optimize cutscene spritesheets.
    Row is the row of the spritesheet to load.  
    Images need to be spritesheets with a size of 320x180 per frame.  
    This is sadly needed because of a limit in the pygame.transform.scale function, so the sprite need to be loaded and resized frame by frame."""

    sprite = image.load(path).convert_alpha()
    size = sprite.get_size()

    lenght = size[0]//320

    sprites = []
    for i in range(lenght): #iterate over the number of frames in the spritesheet
        subsprite = sprite.subsurface(Rect(i*320, 0, 320, 180)) #take the frame at the i-th position 
        sized_subsprite = transform.scale_by(subsprite, 6) #resize the frame
        sprites.append(sized_subsprite.convert_alpha()) #add the frame to the list of frames
    
    return sprites, lenght # the lenght is often used by the calling function to know how many frames are in the spritesheet

def whiten(surface : Surface):
    """Whiten a surface to simulate a button press effect."""
    dest_surf = surface.copy()
    dest_surf.fill((60,60,60), special_flags=BLEND_RGB_ADD)
    return dest_surf

def nine_slice_scaling(surface, target_size, margins):
    """
    Scale an image using nine-slice scaling.
    Inspired by https://en.wikipedia.org/wiki/9-slice_scaling
    
    Basically, the image is divided into 9 slices:
    - 4 corner slices (top-left, top-right, bottom-left, bottom-right) which keep their original size
    - 4 edge slices (top, bottom, left, right) which are stretched horizontally or vertically
    - 1 center slice which is stretched both horizontally and vertically

    This permits to scale the image to any size without distorting the corners and edges (allows stretchable patterns).
    """

    original_width, original_height = surface.get_size()
    target_width, target_height = target_size
    left, right, top, bottom = margins
    
    # Calculate the coordinates for the slices
    center_width = original_width - left - right
    center_height = original_height - top - bottom
    target_center_width = target_width - left - right
    target_center_height = target_height - top - bottom

    # Create a new surface for the scaled image
    scaled_image = Surface(target_size, SRCALPHA)
    
    # Define the slices
    slices = [
        (Rect(0, 0, left, top), (0, 0)),  # Top-left
        (Rect(left, 0, center_width, top), (left, 0, target_center_width, top)),  # Top-center
        (Rect(original_width - right, 0, right, top), (target_width - right, 0)),  # Top-right
        
        (Rect(0, top, left, center_height), (0, top, left, target_center_height)),  # Middle-left
        (Rect(left, top, center_width, center_height), (left, top, target_center_width, target_center_height)),  # Middle-center
        (Rect(original_width - right, top, right, center_height), (target_width - right, top, right, target_center_height)),  # Middle-right
        
        (Rect(0, original_height - bottom, left, bottom), (0, target_height - bottom)),  # Bottom-left
        (Rect(left, original_height - bottom, center_width, bottom), (left, target_height - bottom, target_center_width, bottom)),  # Bottom-center
        (Rect(original_width - right, original_height - bottom, right, bottom), (target_width - right, target_height - bottom)),  # Bottom-right
    ]
    
    # Blit each slice into the new surface
    for src_rect, dest_coords in slices:
        if len(dest_coords) == 2:
            # For corner slices (which have fixed size)
            dest_rect = Rect(dest_coords[0], dest_coords[1], src_rect.width, src_rect.height)
            scaled_image.blit(surface.subsurface(src_rect), dest_rect.topleft)
        else:
            # For scalable slices (center and edges)
            dest_rect = Rect(dest_coords[0], dest_coords[1], dest_coords[2], dest_coords[3])
            scaled_image.blit(transform.scale(surface.subsurface(src_rect), dest_rect.size), dest_rect.topleft)

    
    return scaled_image

def get_outline(surf, color):
    """Returns a surface with an outline around the input surface.
    Home-made algorithm, not the most efficient but it works."""
    outline_width = 3

    width, height = surf.get_size()
    outline_surface = Surface((width + outline_width * 2, height + outline_width * 2), SRCALPHA)

    for dx in range(-outline_width, outline_width + 1):
        for dy in range(-outline_width, outline_width + 1):
            if abs(dx) + abs(dy) == outline_width:
                outline_surface.blit(surf, (dx + outline_width, dy + outline_width))

    outline_surface.fill(color+tuple([0]), special_flags=BLEND_RGBA_MAX)
    outline_surface.fill(color, special_flags=BLEND_RGBA_MULT)
    return outline_surface

def get_locked_surface(surf : Surface):
    """Returns a grey surface with a lock on it."""
    locked_surf = surf.copy()       #create a locked door surface
    locked_surf = transform.grayscale(locked_surf)
    lock = LOCK
    lock_rect = lock.get_rect(center=locked_surf.get_rect().center)    #center the lock on the door
    locked_surf.blit(lock, lock_rect)
    return locked_surf


def fondu(surfs : list[Surface], incr ,speed) -> Surface:
    """Speed is a float between 0 and 1, incr is a float between 0 and pi.
    A good speed is 0.0125, always start with incr = 0.
    The function does a fade in/out effect on a list of surface using the sinus function.
    Home-made algorithm."""
    if incr <= pi: #fade in
        speed = pi*speed
        for surf in surfs:
            rect = surf.get_rect() #get the rect of the surface
            black_surf = Surface((rect.w, rect.h), SRCALPHA) #create a black surface with the same size
            color = (0,0,0,round(255*sin(incr))) #calculate the opacity of the black surface
            black_surf.fill(color) #fill the black surface with the calculated color
            surf.blit(black_surf, (0,0))
        incr += speed 
    
    return incr

def point_rotate(image, origin, pivot, angle):
    """
    Rotate an image around a pivot point.
    This is needed because of the weird way pygame rotates sprites.
    https://stackoverflow.com/questions/15098900/how-to-set-the-pivot-point-center-of-rotation-for-pygame-transform-rotate
    Parameters:
    - image: The image to be rotated.
    - origin: The top-left corner of the image before rotation.
    - pivot: The point around which the image will be rotated.
    - angle: The angle of rotation in degrees.
    """
    # Get the rectangle of the image with the top-left corner at the origin adjusted by the pivot
    image_rect = image.get_rect(topleft=(origin[0] - pivot[0], origin[1] - pivot[1]))
    
    # Calculate the offset from the center of the image to the pivot point
    offset_center_to_pivot = Vector2(origin) - image_rect.center
    
    # Rotate the offset by the negative angle
    rotated_offset = offset_center_to_pivot.rotate(-angle)
    
    # Calculate the new center of the rotated image
    rotated_image_center = (origin[0] - rotated_offset.x, origin[1] - rotated_offset.y)
    
    # Rotate the image
    rotated_image = transform.rotate(image, angle)
    
    # Get the rectangle of the rotated image with the new center
    rotated_image_rect = rotated_image.get_rect(center=rotated_image_center)
    
    return rotated_image, rotated_image_rect

def inverse_kinematics(target, root, length1, length2):
    """Compute the angles needed to reach the target using 2D inverse kinematics 
        Algorithm inspired by https://www.alanzucconi.com/2018/05/02/ik-2d-1/
        Slight use of chatGPT to debug the code."""
    dx = target[0] - root[0]
    dy = target[1] - root[1]
    distance = sqrt(dx**2 + dy**2)

    # Constrain target distance
    distance = min(distance, length1 + length2)

    # Compute angle for the second joint using the Law of Cosines
    cos_angle2 = (dx**2 + dy**2 - length1**2 - length2**2) / (2 * length1 * length2)
    angle2 = acos(max(-1, min(1, cos_angle2)))  # Clamp to valid range

    # Compute angle for the first joint using the Law of Sines
    k1 = length1 + length2 * cos(angle2)
    k2 = length2 * sin(angle2)
    angle1 = atan2(dy, dx) - atan2(k2, k1)

    # Transform into global angles
    return degrees(angle1), degrees(angle2 + angle1)

# Backgrounds
BG1 = load_image("data/backgrounds/R1.png")
BG2 = load_image("data/backgrounds/R0.png")
BG3 = load_image("data/backgrounds/R2.png")
BG4 = load_image("data/backgrounds/R3.png")
BG5 = load_image("data/backgrounds/R4.png")
BG6 = load_image("data/backgrounds/R5.png")
PRETTY_BG = load_image("data/backgrounds/joli_background.png")

# UI Elements
CANVA_UI_PAINT = load_image('data/ui_canva_1.png')
CANVA_UI_NAME = load_image('data/ui_canva2.png')
PAINT_BUTTON = load_image('data/buttons/bouton_canva_ui_paint.png')
SAVE_BUTTON = load_image('data/buttons/bouton_canva_ui_name.png')
WINDOW = load_image('data/bord.png')
YES_BUTTON = load_image("data/buttons/oui.png")
NO_BUTTON = load_image("data/buttons/non.png")
LOGIN_BUTTON = load_image("data/buttons/login.png")
QUIT_BUTTON = load_image("data/buttons/quit.png")
PLAY_BUTTON = load_image('data/buttons/jouer.png')
CLOSE_BUTTON = load_image("data/buttons/close.png")
REGISTER_BUTTON = load_image("data/buttons/register.png")
CONFIRM_BUTTON = load_image("data/buttons/confirm.png")
DESTRUCTION_BUTTON = load_image("data/buttons/destruciotn_button.png")
BUILD_MODE_BORDER = load_image("data/bordure_construction.png")
DESTRUCTION_MODE_BORDER = load_image("data/bordure_destruction.png")
DIALBOX = load_image("data/pop_up_dialogue.png")
ARROW_LEFT = load_image("data/buttons/fleche_gauche.png")
ARROW_RIGHT = load_image("data/buttons/fleche_droite.png")
LOCK = load_image("data/cadena.png")
BEAUTY_LABEL_ANIMATION = anim.Animation(anim.Spritesheet(load_image("data/conteur_beaute.png"), (30*6, 30*6)), 0, 14)
MONEY_LABEL_ANIMATION = anim.Animation(anim.Spritesheet(load_image("data/argent_ui_30x28_25frames.png"), (30*6, 28*6)), 0, 25)
COLOR_BUTTON_BG = load_image("data/couleurs_uii.png")
TITLE = load_image("data/titre_234x82.png")
FRAME_PAINTING = load_image("data/cadre.png")

# Spritesheets
SPRITESHEET_INVENTORY = anim.Spritesheet(load_image('data/etagere.png'), (53*6, 31*6))
SPRITESHEET_HAUT = anim.Spritesheet(load_image("data/prt_haut.png"), (42*6, 29*6))
SPRITESHEET_BAS = anim.Spritesheet(load_image("data/prt_bas.png"), (42*6, 29*6))
SPRITESHEET_DOOR_BLINK = anim.Spritesheet(load_image("data/prt_anim_blink.png"), (42*6, 29*6))
SPRITESHEET_HAUT_FLIP = anim.Spritesheet(transform.flip(load_image("data/prt_haut.png"),False, True), (42*6, 29*6))
SPRITESHEET_BAS_FLIP = anim.Spritesheet(transform.flip(load_image("data/prt_bas.png"),False, True), (42*6, 29*6))
SPRITESHEET_DOOR_BLINK_FLIP = anim.Spritesheet(transform.flip(load_image("data/prt_anim_blink.png"),False, True), (42*6, 29*6))
SPRITESHEET_ROOFTOP = anim.Spritesheet(load_image('data/rooftop.png'), (320*6,180*6))
EXCLAMATION_SPRITESHEET = anim.Spritesheet(load_image("data/exclamation_2x9.png"),(2*6,9*6))

# Desks
DESK_FG = anim.Spritesheet(load_image('data/guichet_1.png'), (57*6,66*6))
DESK_BG = anim.Spritesheet(load_image('data/guichet_2.png'), (57*6,66*6))
DESK_ROBOT_BG = anim.Spritesheet(load_image('data/guichet_robot.png'), (57*6,66*6))

# Props
SHOP = load_image("data/shop_placeable.png")

SPRITE_STATUE_1 = load_image('data/props/statue.png')
SPRITE_STATUE_2 = load_image("data/props/think.png")
SPRITE_PLANT_1 = load_image("data/props/plant_1.png")
SPRITE_PLANT_2 = load_image("data/props/plant_2.png")
SPRITE_POSTER = load_image("data/props/poster.png")
SPRITE_SPHERE = load_image("data/props/familiar_sphere.png")
SPRITE_DUCK = load_image("data/props/duck.png")
SPRITE_CUBE = load_image("data/props/strange_cube.png")
SPRITE_STRAWBERRIES = load_image("data/props/strawberries.png")
SPRITE_ROB = load_image("data/props/walle.png")
SPRITE_PAINTING = load_image("data/props/munch.png")
SPRITE_FLOWER_1 = load_image("data/props/karma_flower.png")
SPRITE_FLOWER_2 = load_image("data/props/red_flower.png")
SPRITE_VASE_1 = load_image("data/props/vase_1.png")
SPRITE_VASE_2 = load_image("data/props/vase_2.png")
SPRITE_VASE_3 = load_image("data/props/vase_3.png")
SPRITE_GOLD =  load_image("data/props/gold_ingot.png")
SPRITE_CELL = load_image("data/props/cell.png")
SPRITE_SHELF_1 = load_image("data/props/shelf_1.png")
SPRITE_SHELF_2 = load_image("data/props/shelf_2.png")
TELESCOPE = load_image("data/telescope.png")


# Robots
#---------------------------------------------
#       The format for the robot anim is:
#line 1 - Walk Right
#line 2 - Walk Left
#line 3 - Idle Right
#line 4 - Watch Wall
#dict is the particle + the relative offset from the origin of the bot
#---------------------------------------------
dust = ParticleSpawner(Coord(0,(0,0)), Vector2(0,0), (50,50,50,100), 60, dir_randomness=2, density=1, speed=0.1)
none_particle = ParticleSpawner(Coord(0,(0,0)), Vector2(0,0), (0,0,0,0), 0, dir_randomness=0, density=0, speed=0)

SPRITESHEET_ROBOT_1_PACK = (anim.Spritesheet(load_image('data/robots/robot_1.png'),(24*6,46*6)), [8, 8, 8, 8],
                             {"right_dust" :(dust.copy(), (4*6,46*6)),
                              "left_dust" :(dust.copy(), (20*6,46*6)),
                              "light" :(ParticleSpawner(Coord(0,(0,0)), Vector2(0,0), (26,80,90,200), 60, dir_randomness=0, density=1, speed=0, radius=(4,4)), (13*6,30*6))})

SPRITESHEET_ROBOT_2_PACK = (anim.Spritesheet(load_image('data/robots/robot_2.png'),(31*6,43*6)), [8, 8, 8, 8],
                            {"right_dust" :(dust.copy(), (6*6,43*6)),
                              "left_dust" :(dust.copy(), (23*6,43*6))})

SPRITESHEET_ROBOT_3_PACK = (anim.Spritesheet(load_image('data/robots/robot_3.png'),(27*6,39*6)), [14, 14, 11, 17],
                            {"right_dust" :(dust.copy(), (4*6,39*6)),
                              "left_dust" :(dust.copy(), (21*6,39*6))})

SPRITESHEET_ROBOT_4_PACK = (anim.Spritesheet(load_image('data/robots/robot_4.png'),(26*6,38*6)), [8, 8, 8, 8],
                            {"right_dust" :(dust.copy(), (5*6,38*6)),
                              "left_dust" :(dust.copy(), (17*6,38*6))})

SPRITESHEET_ROBOT_5_PACK = (anim.Spritesheet(load_image('data/robots/robot_5.png'),(31*6,48*6)), [8, 8, 8, 8],
                            {"right_dust" :(dust.copy(), (11*6,48*6)),
                              "left_dust" :(dust.copy(), (26*6,48*6))})

SPRITESHEET_ROBOT_6_PACK = (anim.Spritesheet(load_image('data/robots/robot_6.png'),(32*6,48*6)), [8, 8, 17, 23],
                            {"right_dust" :(none_particle.copy(), (11*6,48*6)),
                              "left_dust" :(none_particle.copy(), (26*6,48*6)),
                              "levitation" : (LineParticleSpawner(Coord(0,(0,0)), Vector2(1,0), Vector2(0,-1), (150,150,150,200), 25, dir_randomness=0, density=5, speed=1, radius=(4,4), line_length=96), (8*6, 48*6))})

ANIM_ROBOT_MUSIC = anim.Animation(anim.Spritesheet(load_image('data/robots/robot_musique.png'),(48*6,32*6)), 0, 8)

LIST_SPRITESHEET_ROBOT = [SPRITESHEET_ROBOT_1_PACK, SPRITESHEET_ROBOT_2_PACK, SPRITESHEET_ROBOT_3_PACK, SPRITESHEET_ROBOT_4_PACK, SPRITESHEET_ROBOT_5_PACK, SPRITESHEET_ROBOT_6_PACK]

# NPC Sprites
MAIN_CHARACTER = load_image("data/pnj_principal.png")
SHOPKEEPER = load_image("data/shop_pnj.png")
CROWD = load_image("data/foule_pnj.png")
CACHIER_NPC = load_image("data/guichet_pnj.png")
COLOR_NPC = load_image("data/distrid_46x78.png")
TUTORIAL_NPC = load_image("data/deb_pnj.png")

# Arm and Sprayer for the canva
ARM = load_image("data/bra_articuler_1.png")
SPRAYER = load_image("data/buse.png")

# Frame and Patterns
DRAWER_HOLDER = load_image("data/etagere_canva.png")
THUMBNAIL_LIST = [load_image("data/pattern_storage/pattern_"+str(num)+".png") for num in range(1,16)]
PATTERN_LIST = [load_image("data/pattern_storage/pattern_"+str(num)+"_frame.png") for num in range(1,16)]
DRAWER_LIST = [load_image("data/drawers/bouton_"+str(num)+".png") for num in range(1,16)]

# Cutscenes
# The format for the cutscenes is:
# - The cutscene
# - The name of the main dialogue
# - The name of the introspecive dialogue
# Cutscenes are called by the unlock manager when a floor is discovered for the first time
CUTSCENES : dict[str, (anim.Animation, str)] = {"floor0" : {"dialogue" : ("0", TUTORIAL_NPC, "tutor"), "introspec" : "introspec_0"},
                                                "floor1" : {'anim' : "data/anim_deb_57_frames.png", "dialogue" : ("1", TUTORIAL_NPC, "tutor"),'introspec' : "introspec_1"},
                                                "floor2" : {"anim" : "data/anim.png", "dialogue" : ("2",SHOPKEEPER,'cashy'), "introspec" : "introspec_2"},
                                                "floor3" : {"dialogue" : ("3", COLOR_NPC, "colr"), "introspec" : "introspec_3"},
                                                "floor4" : {"anim" : "data/caissier_anim_30frmaes.png", "dialogue" : ("4", CACHIER_NPC, 'rob'), "introspec" : "introspec_4"},
                                                "floor5" : {"anim" : "data/anim_haut_65frames.png", "dialogue" : ("5", CROWD, 'crowd'), "introspec" : "introspec_5"}}



INTRO_CUTSCENE : list[Surface] = [load_image(f'data/anim_intro/frame{i}.png') for i in range(1,6)]