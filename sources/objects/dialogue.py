r"""
Projet : Creative Core
Equipe : Paul Baumard, Abel Bossard, Tybalt Debruyne, Taddeo Boisseuil-Marcil
      _ _       _                         
     | (_)     | |                        
   __| |_  __ _| | ___   __ _ _   _  ___  
  / _` | |/ _` | |/ _ \ / _` | | | |/ _ \ 
 | (_| | | (_| | | (_) | (_| | |_| |  __/ 
  \__,_|_|\__,_|_|\___/ \__, |\__,_|\___| 
                         __/ |            
                        |___/             

Key Features:
-------------
- Dialogue instance containing one dialogue option. 
- Handles text for each dialogue line.
- Updates the dialogue text progressively with animation effects.


      _ _       _                                                                      
     | (_)     | |                                                                     
   __| |_  __ _| | ___   __ _ _   _  ___   _ __ ___   __ _ _ __   __ _  __ _  ___ _ __ 
  / _` | |/ _` | |/ _ \ / _` | | | |/ _ \ | '_ ` _ \ / _` | '_ \ / _` |/ _` |/ _ \ '__|
 | (_| | | (_| | | (_) | (_| | |_| |  __/ | | | | | | (_| | | | | (_| | (_| |  __/ |   
  \__,_|_|\__,_|_|\___/ \__, |\__,_|\___| |_| |_| |_|\__,_|_| |_|\__,_|\__, |\___|_|   
                         __/ |                                          __/ |          
                        |___/                                          |___/           

Key Features:
-------------
- Manages multiple dialogues instances (above) loaded from a JSON file.
- Allows random selection of dialogues for interaction.
- Enhance the interaction with a robot character.

Author: Leih (Abel)
"""

import random as rand
import pygame as pg
import json
from utils.anim import Animation
import ui.sprite as sprite
from utils.fonts import TERMINAL_FONT

pg.init()

class Dialogue:
    def __init__(self, text: list[str]):
        """
        Initialize a Dialogue instance.

        text: List of dialogue lines.
        """
        self.textes = text  # List of dialogue lines
        self.anim_chars = ""  # Characters to be animated
        self.bliting_list: list[pg.Surface] = []  # List of surfaces to be blitted
        self.part_ind = 0  # Index of the current part of the dialogue
        self.showed_texte = self.textes[self.part_ind]  # Current text to be shown
        self.page = 0  # Current page of the dialogue
        self.page_size = 5  # Number of lines per page

    def get_text_surf(self, bot_name : str):
        """
        Get the surface for the current text.

        bot_name: Name of the bot.
        """
        return TERMINAL_FONT.render(f"{bot_name}@botOS:~$ {self.anim_chars}", False, 'green')

    def update(self, bot_name : str):
        """
        Update the dialogue animation.

        bot_name: Name of the bot.
        """
        if self.showed_texte != self.anim_chars:
            self.anim_chars += self.showed_texte[len(self.anim_chars)]

        if self.page != self.part_ind // self.page_size:  # If page changed
            self.page = self.part_ind // self.page_size
            self.bliting_list = []  # Reset showed texts

        if len(self.bliting_list) + (self.page * self.page_size) - 1 < self.part_ind:  # If dialogue text animation finished
            self.bliting_list.append(self.get_text_surf(bot_name))  # Add new line
        else:
            self.bliting_list[self.part_ind - (self.page * self.page_size)] = self.get_text_surf(bot_name)  # Update line

    def is_on_last_part(self):
        """
        Check if the dialogue is on the last part.
        """
        return True if self.part_ind == len(self.textes) - 1 else False

    def skip_to_next_part(self):
        """
        Skip to the next part of the dialogue.
        """
        if not self.is_on_last_part() and self.showed_texte == self.anim_chars:
            self.part_ind += 1
            self.anim_chars = ""
            self.showed_texte = self.textes[self.part_ind] # Change the text to be shown

    def reset(self):
        """
        Reset the dialogue to the beginning.
        """
        self.anim_chars = ""
        self.showed_texte = self.textes[0]
        self.bliting_list = []
        self.part_ind = 0

class DialogueManager:
    def __init__(self):
        """
        Initialize the DialogueManager instance.
        """
        self.dialogues: list[Dialogue] = self.__init()  # List of dialogues
        self.special_dialogues = self.__special_init()  # Dictionary of special dialogues
        self.selected_dialogue: Dialogue = Dialogue(["You shouldn't see this message"])  # Default dialogue
        self.npc_icon: Animation | pg.Surface = None  # Idle animation of the robot clicked
        self.background = sprite.DIALBOX  # Background sprite for dialogue box

    def __init(self) -> list[Dialogue]:
        """
        Initialize the dialogues from a JSON file.
        """
        with open("data/dialogue.json", encoding='utf8') as file:
            json_string = file.read()
            dialogues = []
            loaded_dicts = json.loads(json_string)
            for dict in loaded_dicts:
                for dialogue in dict['dialogues']:
                    dialogues.append(Dialogue(dialogue))
            return dialogues

    def __special_init(self) -> dict[str, Dialogue]:
        """
        Initialize the special dialogues from a JSON file.
        """
        with open("data/special_dialogue.json", encoding='utf8') as file:
            json_string = file.read()
            special_dialogues = {}
            loaded_dict = json.loads(json_string)
            for key in loaded_dict:
                special_dialogues[key] = Dialogue(loaded_dict[key])
            return special_dialogues

    def random_dialogue(self):
        """
        Select a random dialogue from the list of dialogues.
        """
        if self.selected_dialogue:
            self.selected_dialogue.reset()  # Reset the current dialogue

        self.selected_dialogue = rand.choice(self.dialogues)  # Select a random dialogue

    def special_dialogue(self, dialogue_name):
        """
        Select a special dialogue by name.
        """
        if self.selected_dialogue:
            self.selected_dialogue.reset()  # Reset the current dialogue

        self.selected_dialogue = self.special_dialogues[dialogue_name]  # Select the special dialogue

    def click_interaction(self) -> bool:
        """
        Handle click interaction and return True if the dialogue is finished.
        """
        if self.selected_dialogue.is_on_last_part():
            return True  # Dialogue is finished
        else:
            self.selected_dialogue.skip_to_next_part()  # Skip to the next part of the dialogue
            return False

    def update(self, npc_name = 'anon'):
        """
        Update the current dialogue.
        """  # Default bot name
        self.selected_dialogue.update(npc_name)  # Update the dialogue with the bot name

    def draw(self, screen: pg.Surface):
        """
        Draw the dialogue and bot animation on the screen.
        """
        screen.blit(self.background, (300 + 46 * 6, 750))  # Draw the background
        for i, surf in enumerate(self.selected_dialogue.bliting_list):
            line_height = 812 + 27 * i  # Calculate the line height
            screen.blit(surf, (650, line_height))  # Draw each line of the dialogue

        if self.npc_icon:
            if type(self.npc_icon) == Animation:
                scaled_bot_surface = pg.transform.scale2x(self.npc_icon.get_frame())  # Scale the bot animation
            else:
                scaled_bot_surface = pg.transform.scale2x(self.npc_icon)
            scaled_bot_rect = scaled_bot_surface.get_rect(bottomright=(504, 1050))  # Get the rect for the bot animation
            screen.blit(scaled_bot_surface, scaled_bot_rect)  # Draw the bot animation





