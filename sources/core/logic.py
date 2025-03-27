r"""
                  _         _             _      
                 (_)       | |           (_)     
  _ __ ___   __ _ _ _ __   | | ___   __ _ _  ___ 
 | '_ ` _ \ / _` | | '_ \  | |/ _ \ / _` | |/ __|
 | | | | | | (_| | | | | | | | (_) | (_| | | (__ 
 |_| |_| |_|\__,_|_|_| |_| |_|\___/ \__, |_|\___|
                                     __/ |       
                                    |___/        

This game loop operates with a FSM (Finite State Machine), transitionning between states such as interaction,
building, destruction, inventory management, painting, placing patterns, dialogue, and shop navigation.

Each frame (60fps):
-------------
1. Event Handling: Processes player inputs to update the game state.
                            |
                            v
2. Update: Advances timers, updates AI behaviors, and refreshes objects based on the current state.
                            |
                            v
3. Rendering: Draws objects, UI elements, and overlays according to the active state.

Certain states, like confirmation prompts and transitions, override standard interactions.

Author: Pouchy (Paul), Ytyt (Tybalt), Leih (Abel), Tioh (Taddeo), but heavily refactored by Pouchy"""

from enum import Enum, auto
class State(Enum):
    """Enumeration of the different GUI states.  
    User by the game's FSM to manage the different states of the game."""
    INTERACTION = auto() # value is irrelevant for an FSM so it is set to auto()
    BUILD = auto()
    DESTRUCTION = auto()
    INVENTORY = auto()
    DIALOG = auto()
    TRANSITION = auto()
    CONFIRMATION = auto()
    SHOP = auto()
    PAUSED = auto()

# system 
import pygame as pg
from math import pi #used for the transition effect

# core game elements
from core.buildmode import BuildMode, DestructionMode
from core.unlockmanager import UnlockManager
from objects.bot import Hivemind, BotDistributor
from objects.canva import Canva
from objects.dialogue import DialogueManager
from objects.particlesspawner import ParticleSpawner
from objects.patterns import PatternHolder
from objects.placeable import Placeable
import objects.placeablesubclass as subplaceable

# ui elements
from ui.button import Button
from ui.cinematic import CinematicPlayer, IntroCutscene
from ui.confirmationpopup import ConfirmationPopup
from ui.infopopup import InfoPopup
from ui.inventory import Inventory, Shop
import ui.sprite as sprite

# misc
from utils.coord import Coord
from utils.fonts import TERMINAL_FONT_BIG
from utils.room_config import R1, R4, ROOMS, Room, PARTICLE_SPAWNERS, SPECIAL_PLACEABLES
from utils.sound import SoundManager
from utils.timermanager import TimerManager

class Game:
    def __init__(self, win : pg.Surface, config : dict, inventory, shop, gold, unlock_manager, transparency_win, last_frame_of_homescreen : pg.Surface, sound_manager : SoundManager):
        """Initializes the game with the provided configuration and save data."""
        self.config = config
        self.win : pg.Surface = win
        self.timer : TimerManager = TimerManager()

        
        self.transparency_win = transparency_win
        self.sound_manager = sound_manager
        self.sound_manager.timer = self.timer
        self.sound_manager.play_random_ambiant_sound()
        self.clock : pg.time.Clock = pg.time.Clock()
        self.popups : list[InfoPopup] = []
        self.confirmation_popups : list[ConfirmationPopup] = [] # Stack of confirmation popups
        self.gui_state = State.INTERACTION
        self.hivemind : Hivemind = Hivemind(60, 600, self.timer, self.sound_manager)
        self.inventory : Inventory = Inventory(self.change_floor, self.reset_guistate, title= "Inventaire", content = inventory) # Inventory
        self.shop : Shop = Shop(None, self.reset_guistate, title= "Shop", content = shop) 
        self.inventory.sound_manager = self.sound_manager
        self.shop.sound_manager = self.sound_manager
        self.build_mode : BuildMode= BuildMode()
        self.destruction_mode : DestructionMode= DestructionMode()
        self.bot_distributor : BotDistributor = BotDistributor(self.timer, self.hivemind, self)
        self.dialogue_manager : DialogueManager = DialogueManager()
        self.current_room : Room = R1 # Starter room always in floor 1.
        self.incr_fondu = 0
        self.money : int = gold
        self.beauty : float = self.process_total_beauty()
        self.unlock_manager : UnlockManager = unlock_manager
        self.canva : Canva = Canva(Coord(0,(618,24)), self)
        self.pattern_holder : PatternHolder = PatternHolder(Coord(0, (36, self.canva.coord.y+72)), canva=self.canva)
        self.paused = False

        self.particle_spawners : dict[int,list] = PARTICLE_SPAWNERS

        self.guichet = SPECIAL_PLACEABLES['guichet']

        # Initialize unlocks effects.
        for unlocked_feature in self.unlock_manager.unlocked_features: # If the auto cachier is unlocked
            self.unlock_effect(unlocked_feature) # Apply the unlock effect
            
        if not self.unlock_manager.is_floor_discovered("1") and not config['gameplay']['no_story']: # If the first floor is not discovered (equivalent to the 1st time the player enters the game)
            self.sound_manager.music_begin.play(-1) # Play the intro music
            IntroCutscene(sprite.INTRO_CUTSCENE).play(self, last_frame_of_homescreen) # Launch the intro cutscene
            self.unlock_manager.discovered_floors.append("1")
            CinematicPlayer(sprite.CUTSCENES["floor1"]).play(self) # Launch the first floor tutorial
            self.sound_manager.music_begin.fadeout(2000) # Fade out the intro music
        
        self.sound_manager.music_ambiant.play(-1)
        self.timer.create_timer(5, self.play_random_ambiant_sound, repeat=True, repeat_time_interval=[1, 13]) # Play a random ambiant sound every now and then
            
        self.update_all_locked_status() # Update doors lock state

        if not self.config['gameplay']['offline_mode']: # If the player is not in the no_login mode, don't initialize the spectating placeable
            self.configure_online_mode()
    
    def unlock_effect(self, feature_name):
        """Handles the unlock effects of the feature"""
        match feature_name:
            case "Auto Cachier":
                self.timer.create_timer(3, self.accept_bot, True) # Accept a bot every 3 seconds (effect of the auto cachier unlock)
                self.guichet.auto_cachier_unlocked = True # To display the auto cachier effect on the guichet
                R4.placed.remove(SPECIAL_PLACEABLES['auto_cachier']) # Remove the auto cachier from the room
            case "Color":
                self.canva.color_buttons = self.canva.init_color_buttons(True) # Initialize again the color buttons with the color feature unlocked this time
                self.canva.color_buttons_unlocked = True
    
    def configure_online_mode(self):
        """ Handles the changes necessary to play in online mode"""
        self.spectating_placeable = subplaceable.SpectatorPlaceable('spectating_placeable', Coord(5,(1032, 678)), sprite.TELESCOPE, self.config)
        ROOMS[5].placed.append(self.spectating_placeable)
        ROOMS[5].blacklist.append(self.spectating_placeable)

    def change_floor(self, direction):
        """ Changes the current room to the next one in the given direction 
        (1 for up, -1 for down)"""

        # Check if the next room is within the limits and unlocked
        if 0 <= self.current_room.num + direction <= 5 and (self.unlock_manager.is_floor_unlocked(self.current_room.num + direction) or self.config['gameplay']['cheats']):

            self.current_room = ROOMS[self.current_room.num + direction]  # Move to the next room
            self.update_all_locked_status() # Update doors lock state

            # Checks if floor already visited and launches dialogue if not
            if not self.unlock_manager.is_floor_discovered(self.current_room.num):
                self.unlock_manager.discovered_floors.append(str(self.current_room.num))
                self.reset_guistate()
                if not self.config['gameplay']['no_story']:
                    CinematicPlayer(sprite.CUTSCENES[f"floor{self.current_room.num}"]).play(self)
            
               
        else:
            self.popups.append(InfoPopup("you can't go off limits"))  # Show popup if trying to go below limits
    
    def update_all_locked_status(self):
        """ Updates the locked status of all unlockable placeable in the current room
        Intended to be called when a new floor is discovered or when a new feature is unlocked"""
        for door in self.current_room.placed:
            if type(door) in [subplaceable.DoorUp, subplaceable.DoorDown]:
                door.update_lock_status(self.unlock_manager, self.current_room)

    def launch_random_dialogue(self, bot_anim):
        """ Function to initiate dialogue easily passed to other functions
        Intended to be called when a reacting bot is clicked"""
        self.gui_state = State.DIALOG
        self.paused = True
        self.temp_bg = pg.transform.grayscale(self.win) # Grayscale the background
        self.dialogue_manager.random_dialogue()  # Trigger a random dialogue
        self.dialogue_manager.npc_icon = bot_anim.copy()  # Copy the bot's surface for display
    
    def launch_special_dialogue(self, dialogue_name):
        """ Function to initiate dialogue easily passed to other functions
        Intended to be called when a unique dialogue from the story is triggered"""
        self.gui_state = State.DIALOG
        self.paused = True
        self.temp_bg = pg.transform.grayscale(self.win) # Grayscale the background
        if dialogue_name=='0':
            self.popups.append(InfoPopup("ATTENDEZ !! "))
            self.timer.create_timer(1, self.dialogue_manager.special_dialogue, arguments=[dialogue_name])  # Trigger a random dialogue with a delay
            self.dialogue_manager.npc_icon = None # TO DO : Add a special animation for this dialogue
        else:
            self.dialogue_manager.special_dialogue(dialogue_name)  # Trigger a random dialogue.
            self.dialogue_manager.npc_icon = None # TO DO : Add a special animation for this dialogue

    def pause(self):
        """ Pauses the game and displays the pause menu"""
        self.gui_state = State.PAUSED
        self.paused = True
        self.temp_bg = pg.transform.grayscale(self.win) # Grayscale the background
        self.quit_button = Button((0,0), self.quit, sprite.whiten(sprite.QUIT_BUTTON), sprite.QUIT_BUTTON)
        self.quit_button.rect.center = self.win.get_rect().center
        
    def quit(self):
        print('Quitting game ...')
        pg.event.post(pg.event.Event(pg.QUIT))
    
    def reset_guistate(self):
        self.paused = False
        self.gui_state = State.INTERACTION

    def process_total_beauty(self):
        """ Sums the overall beauty score to be used by the Bot_Manager"""
        total = 0
        for room in ROOMS:
            total += room.get_beauty_in_room()
        return total
    
    def accept_bot(self):
        """ When liberating a bot, add the proper money amount given by hivemind.free_last_bot (which updates the bots logic)"""
        accepted_bot_money_amount = self.hivemind.free_last_bot(R1)
        if accepted_bot_money_amount: # Attempt to free the last bot and checks output
            self.money += accepted_bot_money_amount  # Increment currency
        SPECIAL_PLACEABLES['guichet'].active = True
        
    def launch_transition(self):
        """ Launches the transition effect when changing floors"""
        self.gui_state = State.TRANSITION  # Set the GUI to the transition state
        self.incr_fondu = 0  # Reset the transition variable
    
    def render_popups(self):  
        """ Render all infopopups on the window """
        # Iterate over existing popups to render and manage their lifetime
        for popup in self.popups:
            if popup.lifetime <= 0:
                self.popups.remove(popup)  # Remove expired popups
            else:
                popup.draw(self.win)  # Render the popup on the window
                popup.lifetime -= 1  # Decrement popup's lifetime

#    ____              __    
#   / __/  _____ ___  / /____
#  / _/| |/ / -_) _ \/ __(_-<
# /___/|___/\__/_//_/\__/___/
                           
    def event_handler(self, event: pg.event.Event, mouse_pos: Coord):
        """
        Manages all events, eventually dispatching to sub functions like placeable_interaction_handler
        or keydown_handler
        """
        if event.type == pg.KEYDOWN:
            self.keydown_handler(event)

        if hasattr(self, "spectating_placeable") and self.spectating_placeable.open and self.current_room.num == 5:
            self.spectating_placeable.user_list.handle_event(event)

        if event.type == pg.MOUSEBUTTONDOWN:
            self.handle_mouse_button_down(event, mouse_pos)
        
        if self.current_room.num == 0:
            self.pattern_holder.handle_event(event)
            self.canva.handle_event(event)

# -----------------------------
# Keydown event handler
# -----------------------------

    def keydown_handler(self, event : pg.event.Event):
        """Passes the key event to the proper handler based on the current GUI state"""
        if self.config['gameplay']['cheats']:
            self.handle_cheat_keys(event.key)
        self.handle_regular_keys(event.key)

    def handle_regular_keys(self, key):
        match key:
            case pg.K_SPACE:
                self.toggle_inventory()
            case pg.K_ESCAPE:
                self.handle_escape_key()

    def handle_cheat_keys(self, key):
        """Grant the player the ability to access cheats.  
        Cheats are available in the config file.  
        Match case are very useful for this kind of feature :)"""
        match key:
            case pg.K_UP:
                self.change_floor(1)
            case pg.K_DOWN:
                self.change_floor(-1)
            case pg.K_b:
                self.hivemind.add_bot()
            case pg.K_BACKSPACE:
                self.toggle_destruction_mode()
            case pg.K_n:
                self.hivemind.free_last_bot(self.current_room)
            case pg.K_s:
                self.toggle_shop()
            case pg.K_i:
                self.save_canva()
            case pg.K_g:
                self.money += 1000
            case pg.K_b:
                self.beauty += 1

    def toggle_inventory(self):
        """ Toggles the inventory GUI state
        If the inventory is already open, it will close it and return to the interaction state"""
        if self.gui_state is State.INTERACTION:
            self.gui_state = State.INVENTORY
            self.inventory.init()
        elif self.gui_state is State.INVENTORY:
            self.reset_guistate()

    def toggle_destruction_mode(self):
        """ Toggles the destruction mode GUI state
        If the destruction mode is already open, it will close it and return to the interaction state
        Destruction mode have a custom quit button to return to the interaction state"""
        if self.gui_state is State.INTERACTION or self.gui_state is State.INVENTORY:
            self.gui_state = State.DESTRUCTION
            self.destruction_quit_button = Button((0,0), self.reset_guistate, sprite.whiten(sprite.QUIT_BUTTON), sprite.QUIT_BUTTON)
            self.destruction_quit_button.rect.bottomleft = self.win.get_rect().bottomleft
        else:
            self.reset_guistate()

    def handle_escape_key(self):
        """Handles the escape key event based on the current GUI state
        If the game is in interaction state, it will pause the game"""
        if self.gui_state not in [State.TRANSITION, State.CONFIRMATION, State.INTERACTION]:
            self.reset_guistate()
        elif self.gui_state is State.INTERACTION:
            self.pause()

    def save_canva(self):
        self.inventory.inv.append(self.canva.get_placeable())
        self.popups.append(InfoPopup("Vous avez sauvegardé votre toile dans l'inventaire !"))

    def toggle_shop(self):
        if self.gui_state is State.INTERACTION:
            self.gui_state = State.SHOP
            self.sound_manager.shop.play()
            self.shop.init()
        elif self.gui_state is State.SHOP:
            self.reset_guistate()

# -----------------------------
# Placeable interaction handler
# -----------------------------
    def placeable_interaction_handler(self, placeable : Placeable):
        """ Dispatches to the proper interaction function based on the placeable type"""
        match type(placeable):
            case subplaceable.DoorDown:
                self.handle_door_down_interaction(placeable)
            case subplaceable.DoorUp:
                self.handle_door_up_interaction(placeable)
            case subplaceable.BotPlaceable:
                self.accept_bot()
            case subplaceable.ShopPlaceable:
                self.handle_shop_interaction()
            case subplaceable.InvPlaceable:
                self.handle_inventory_interaction()
            case subplaceable.AutoCachierPlaceable:
                self.handle_auto_cachier_interaction()
            case subplaceable.SpectatorPlaceable:
                self.handle_spectator_interaction(placeable)
            case subplaceable.ColorUnlockPlaceable:
                self.handle_color_placeable_interaction()
            case _:
                if not hasattr(placeable, 'no_interaction'):
                    self.popups.append(InfoPopup(placeable.name))

                       


    def handle_door_down_interaction(self, placeable):
        if self.unlock_manager.is_floor_unlocked(self.current_room.num-1): # Check if the next floor is unlocked
            self.timer.create_timer(0.75, self.change_floor, arguments=[-1]) # Change floor
            self.sound_manager.down.play() # Play sound
            self.launch_transition() # Launch transition
            placeable.interaction(self.timer)
        else:
            self.unlock_manager.try_to_unlock_floor(self.current_room.num-1, self) # Try to unlock the next floor

    def handle_door_up_interaction(self, placeable):
        if self.unlock_manager.is_floor_unlocked(self.current_room.num+1): # Check if the next floor is unlocked
            self.timer.create_timer(0.75, self.change_floor, arguments=[1]) # Change floor
            self.sound_manager.up.play() # Play sound
            self.launch_transition() # Launch transition
            placeable.interaction(self.timer)
        else: 
            self.unlock_manager.try_to_unlock_floor(self.current_room.num+1, self) # Try to unlock the next floor

    def handle_shop_interaction(self):
        if not self.unlock_manager.is_feature_discovered("shop"): # Check if the shop is discovered
            self.unlock_manager.discovered_features.append("shop")
            self.launch_special_dialogue("shop Discovery") # Launch tutorial dialogue
            return
        
        if self.gui_state is not State.SHOP:
            self.gui_state = State.SHOP
            self.shop.init()

    def handle_inventory_interaction(self):
        if not self.unlock_manager.is_feature_discovered("inventory"):
            self.unlock_manager.discovered_features.append("inventory")
            self.launch_special_dialogue("inventory Discovery")
            return

        if self.gui_state is not State.INVENTORY:
            self.gui_state = State.INVENTORY
            self.inventory.init()

    def handle_auto_cachier_interaction(self):
        if self.unlock_manager.is_feature_discovered("Auto Cachier"):
            self.unlock_manager.try_to_unlock_feature("Auto Cachier", self)
        else:
            self.unlock_manager.discovered_features.append("Auto Cachier")
            self.launch_special_dialogue("Auto Cachier Discovery")
    
    def handle_color_placeable_interaction(self):
        if self.unlock_manager.is_feature_discovered("Color"):
            self.unlock_manager.try_to_unlock_feature("Color", self)
        else:
            self.unlock_manager.discovered_features.append("Color")
            self.launch_special_dialogue("Color Discovery")

    def handle_spectator_interaction(self, placeable):
        if not self.unlock_manager.is_feature_discovered("spectator"):
            self.unlock_manager.discovered_features.append("spectator")
            self.launch_special_dialogue("spectator Discovery")
            return
        
        placeable.interaction()
        if placeable.open:
            self.popups.append(InfoPopup("Cliquez sur les fenetres pour visiter le musée d'un autre joueur !"))

# -----------------------------
# Mouse button up event handler
# -----------------------------

    def handle_mouse_button_down(self, event: pg.event.Event, mouse_pos: Coord):
        """
        Handles mouse button release events based on the current GUI state.
        """
        match self.gui_state:
            case State.BUILD:
                self.handle_build_mode()

            case State.INVENTORY:
                self.handle_inventory_mode(event, mouse_pos)

            case State.SHOP:
                self.shop.handle_click(mouse_pos, self)
                self.shop.handle_navigation(event)
                self.shop.quit_button.handle_event(event)

            case State.DESTRUCTION:
                self.handle_destruction_mode(mouse_pos)
                self.destruction_quit_button.handle_event(event)

            case State.INTERACTION:
                self.handle_interaction_mode(mouse_pos)

            case State.DIALOG:
                self.handle_dialog_mode()

            case State.CONFIRMATION:
                self.handle_confirmation_mode(mouse_pos)

            case State.PAUSED:
                self.quit_button.handle_event(event)
            

    def handle_build_mode(self):
        if self.build_mode.can_place(self.current_room): # Check if the object can be placed in the room when clicked
            self.current_room.placed.append(self.build_mode.get_configured_placeable(self.current_room.num)) # Place the object in the room
            self.sound_manager.items.play() 
            self.beauty = self.process_total_beauty() # Update beauty score
            self.gui_state = State.INVENTORY # Return to the inventory
            self.inventory.init()
        else:
            self.popups.append(InfoPopup("Vous ne pouvez pas placer cet objet ici !"))

    def handle_inventory_mode(self, event: pg.event.Event, mouse_pos: Coord):
        self.inventory.handle_floor_navigation_buttons(event)
        if self.inventory.handle_destruction_button(event):
            self.toggle_destruction_mode()
        self.inventory.handle_navigation(event)
        clicked_placeable = self.inventory.handle_click(mouse_pos)
        if clicked_placeable and self.current_room.num != 0:
            self.build_mode.selected_placeable = clicked_placeable
            self.gui_state = State.BUILD

    def handle_destruction_mode(self, mouse_pos: Coord):
        for placeable in self.current_room.placed:
            if placeable.rect.collidepoint(mouse_pos.x, mouse_pos.y):
                self.destruction_mode.remove_from_room(placeable, self.current_room) # Remove the object from the room
                self.beauty = self.process_total_beauty()

    def handle_interaction_mode(self, mouse_pos: Coord):
        for placeable in self.current_room.placed:
            if placeable.rect.collidepoint(mouse_pos.x, mouse_pos.y): # Check if the mouse is over a placeable
                self.placeable_interaction_handler(placeable)

        self.hivemind.handle_bot_click(mouse_pos, self.launch_random_dialogue) # Handle bot reaction click

    def handle_dialog_mode(self):
        if self.dialogue_manager.click_interaction(): # Check if the dialogue is over
            self.reset_guistate() # Return to the interaction state
            self.paused = False

    def handle_confirmation_mode(self, mouse_pos: Coord):
        flag = self.confirmation_popups[-1].handle_click(mouse_pos) # Check if the confirmation popup was clicked
        if flag is not None:
            self.confirmation_popups.pop()

        if not self.confirmation_popups: # If there are no more confirmation popups
            self.reset_guistate() # Return to the interaction state


#                    __      __     
#   __  ______  ____/ /___ _/ /____ 
#  / / / / __ \/ __  / __ `/ __/ _ \
# / /_/ / /_/ / /_/ / /_/ / /_/  __/
# \__,_/ .___/\__,_/\__,_/\__/\___/ 
#     /_/                         


    def update(self, mouse_pos):
        self.update_music()
        self.update_timers()
        self.update_particles()
        self.update_current_room(mouse_pos)
        self.update_bots()
        self.update_gui_state()

    def update_timers(self):
        self.timer.update()

    def update_particles(self):
        spawners: list[ParticleSpawner] = self.particle_spawners.get(self.current_room.num, None)
        if spawners is not None:
            for spawner in spawners:
                spawner.spawn()
                spawner.update_all()
                if spawner.finished:
                    spawners.remove(spawner)
    
    def update_music(self):
        if self.current_room.num == 5:
            self.sound_manager.music_ambiant.set_volume(0.6*self.sound_manager.volume)
        else:
            self.sound_manager.music_ambiant.set_volume(0.2*self.sound_manager.volume)
        
    def play_random_ambiant_sound(self):
        if self.hivemind.liberated_bots and self.current_room.num != 0: # 25% chance to play a random robot sound
            self.sound_manager.play_random_robot_sound()
        

    def update_current_room(self, mouse_pos):
        self.current_room.update_sprite()
        for placeable in self.current_room.placed:
            if placeable.rect.collidepoint(mouse_pos.xy) and self.gui_state in [State.DESTRUCTION, State.INTERACTION]:
                color = (170, 170, 230) if self.gui_state != State.DESTRUCTION else (255, 0, 0)
                placeable.update_sprite(True, color)
            else:
                placeable.update_sprite(False)

    def update_bots(self):
        self.hivemind.order_inline_bots()
        self.hivemind.update(ROOMS, self.timer)

    def update_gui_state(self):
        match self.gui_state:
            case State.INTERACTION:
                self.hivemind.create_last_bot_clickable()
        if self.confirmation_popups:
            self.gui_state = State.CONFIRMATION


#     ____                     
#    / __ \_________ __      __
#   / / / / ___/ __ `/ | /| / /
#  / /_/ / /  / /_/ /| |/ |/ / 
# /_____/_/   \__,_/ |__/|__/  

    def draw(self, mouse_pos: Coord):
        """Draws all elements of the game"""
        self.draw_background()
        self.draw_current_room()
        self.draw_bots(mouse_pos)
        self.draw_patterns_and_canva()
        self.draw_particles()
        self.draw_foreground()
        self.draw_info_ui()
        self.draw_gui(mouse_pos)
        if self.config['gameplay']['debug']:
            self.draw_debug_info(mouse_pos)
        self.render_popups()
        if not self.paused:
            self.win.blit(self.transparency_win, (0, 0))
            
    def draw_info_ui(self):
        beauty_default_string = "0000.0" # Default string to display the beauty score
        cropped_beauty = float(min(self.beauty, 9999.9)) # Crop the beauty score to 4 digits
        beauty_string = beauty_default_string[:6-len(str(cropped_beauty))] + str(cropped_beauty) # Magic slice to replace the end of default string with actual beauty value
        beauty_background = sprite.BEAUTY_LABEL_ANIMATION.get_frame() # Get the current frame of the beauty label animation

        cropped_money = int(min(self.money, 99999)) # Crop the money to 5 digits, doesn't affect the actual money value
        money_background = sprite.MONEY_LABEL_ANIMATION.get_frame()

        # Blit everything together
        beauty_background.blit(TERMINAL_FONT_BIG.render(beauty_string, False, (0, 255, 0)), (6*6, 6*6))
        money_background.blit(TERMINAL_FONT_BIG.render(str(cropped_money), False, (255, 255, 0)), (6*5, 8*6)) 

        self.win.blit(beauty_background, (self.win.get_width()-beauty_background.get_width(), 0))

        if self.current_room.num == 0:
            self.win.blit(money_background, (self.win.get_width()-money_background.get_width(), beauty_background.get_height()+6))
        else:
            self.win.blit(money_background, (self.win.get_width()-money_background.get_width()-beauty_background.get_width()-6, 0))

    def draw_background(self):
        self.win.blit(self.current_room.bg_surf, (0, 0))
        self.transparency_win.fill((0, 0, 0, 0)) # Reset the transparency window

    def draw_current_room(self):
        self.current_room.draw_placed(self.win)
    
    def draw_foreground(self):
        self.current_room.draw_placed_foreground(self.transparency_win)

    def draw_bots(self, mouse_pos):
        self.hivemind.draw(self.win, self.current_room.num, mouse_pos, self.transparency_win)

    def draw_patterns_and_canva(self):
        if self.current_room.num == 0:
            self.pattern_holder.draw(self.win)
            self.canva.draw(self.win) # Needs to be drawn after the pattern holder

    def draw_particles(self):
        spawners: list[ParticleSpawner] = self.particle_spawners.get(self.current_room.num, None)
        if spawners is not None:
            for spawner in spawners:
                spawner.draw_all(self.transparency_win)

    def draw_gui(self, mouse_pos):
        """Draws the GUI elements based on the current state"""
        match self.gui_state:
            case State.INTERACTION:
                # hasattr is used because the spectating placeable is disabled in offline mode
                if hasattr(self, "spectating_placeable") and self.spectating_placeable.open and self.current_room.num == 5: # If the spectating placeable is open and on last floor
                    self.spectating_placeable.user_list.draw(self.win)

            case State.BUILD:
                self.win.blit(sprite.BUILD_MODE_BORDER, (0, 0))
                mouse_pos_coord = Coord(self.current_room.num, (mouse_pos.x - self.build_mode.get_width() // 2, mouse_pos.y - self.build_mode.get_height() // 2))
                self.build_mode.show_hologram(self.win, mouse_pos_coord)
                self.build_mode.show_room_holograms(self.win, self.current_room)
            
            case State.DESTRUCTION:
                self.win.blit(sprite.DESTRUCTION_MODE_BORDER, (0, 0))
                self.destruction_quit_button.draw(self.win, self.destruction_quit_button.rect.collidepoint(mouse_pos.xy))

            case State.DIALOG:
                self.win.blit(self.temp_bg, (0, 0))
                self.paused = True
                self.dialogue_manager.update()
                self.dialogue_manager.draw(self.win)

            case State.PAUSED:
                self.win.blit(self.temp_bg, (0, 0))
                self.paused = True
                self.quit_button.draw(self.win, self.quit_button.rect.collidepoint(mouse_pos.xy))

            case State.TRANSITION:
                if self.incr_fondu <= pi:
                    self.incr_fondu = sprite.fondu([self.win, self.transparency_win], self.incr_fondu, 0.0125) #
                else:
                    self.reset_guistate() 

            case State.CONFIRMATION:
                if self.confirmation_popups:
                    self.confirmation_popups[-1].draw(mouse_pos)

            case State.INVENTORY:
                self.inventory.draw(self.win, mouse_pos)
                self.inventory.draw_floor_navigation_buttons(self.win, mouse_pos)

            case State.SHOP:
                self.shop.draw(self.win, mouse_pos)

    def draw_debug_info(self, mouse_pos : Coord):
        self.win.blit(InfoPopup(
            f'gui state : {self.gui_state} / fps : {round(self.clock.get_fps())} / mouse : {mouse_pos.get_pixel_perfect()} / $ : {self.money} / th_gold : {self.bot_distributor.theorical_gold} / beauty : {self.beauty} / bot_count {len(self.hivemind.liberated_bots)}').text_surf, (0, 0))


#     __  ______    _____   __   __    ____  ____  ____ 
#    /  |/  /   |  /  _/ | / /  / /   / __ \/ __ \/ __ \
#   / /|_/ / /| |  / //  |/ /  / /   / / / / / / / /_/ /
#  / /  / / ___ |_/ // /|  /  / /___/ /_/ / /_/ / ____/ 
# /_/  /_/_/  |_/___/_/ |_/  /_____/\____/\____/_/      


    def get_save_dict(self):
        return {'gold': self.money, 'inventory': self.inventory.inv, "shop": self.shop.inv, "unlocks": self.unlock_manager, "beauty" : self.beauty}

    def main_loop(self) -> dict:
        fps = self.config['gameplay']['fps']  # Frame rate
        while True:
            self.clock.tick(fps)  # Maintain frame rate
            mouse_pos: Coord = Coord(self.current_room.num, pg.mouse.get_pos())  # Coordinates of the mouse (to not call pg.mouse.get_pos() multiple times)
            events = pg.event.get()  # Get all events from the event queue

            for event in events:
                if event.type == pg.QUIT:  # Check for quit event
                    return self.get_save_dict() # Return data to be saved in the DB
                
                self.event_handler(event, mouse_pos)
            
            if not self.paused: # If the game is not paused
                self.update(mouse_pos)

            self.draw(mouse_pos) # Draw the game


            pg.display.flip()  # Update the display