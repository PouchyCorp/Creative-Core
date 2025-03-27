r"""
Projet : Creative Core
Equipe : Paul Baumard, Abel Bossard, Tybalt Debruyne, Taddeo Boisseuil-Marcil
                      _ _     _   
                     | (_)   | |  
  _   _ ___  ___ _ __| |_ ___| |_ 
 | | | / __|/ _ \ '__| | / __| __|
 | |_| \__ \  __/ |  | | \__ \ |_ 
  \__,_|___/\___|_|  |_|_|___/\__|


This module manages the user list UI component.

Key Features:
-------------
- Displays a list of users.
- Handles user interactions with the list.

Author: Ytyt (Tybalt)
"""

from pygame import Surface, Rect, MOUSEBUTTONUP
from ui.sprite import WINDOW, nine_slice_scaling
from utils.fonts import TERMINAL_FONT
from core.spectator import Spectator

class UserList:
    def __init__(self, coord : tuple, content : list[tuple]):
        self.coord = coord
        self.content = content
        self.lengh = len(content)
        self.page = 1
        self.processed_tabs = []
        self.init(self.content)

    def init(self, content):
        self.displayed_content = content[(self.page-1)*4:self.page*4]
        self.process_tabs()

    def process_tabs(self) -> list[tuple[Surface, Rect]]:
        self.processed_tabs = []
        for i, data in enumerate(self.displayed_content):
            username, dic = data
            username_surf = TERMINAL_FONT.render(f"Musée de {username}", False, "white")
            beauty_surf = TERMINAL_FONT.render(f"beauté : {dic['beauty']}", False, "white")
            floor_unlock_surf = TERMINAL_FONT.render(f"étages débloqués : {len(dic['unlocks'].unlocked_floors)-1} / 5", False, "white")
            rect = Rect(735, 216+(110*i)+24, 450, 100)
            
            bg_surf = nine_slice_scaling(WINDOW, rect.size, (12,12,12,12))
            bg_surf.blit(username_surf, (12,12))
            bg_surf.blit(beauty_surf, (12,12+username_surf.get_height()+2))
            bg_surf.blit(floor_unlock_surf, (12,12+username_surf.get_height()+beauty_surf.get_height()+4))

            self.processed_tabs.append((bg_surf, rect))

    def draw(self, win : Surface):
        win.blits(self.processed_tabs)


    def handle_event(self, event):
        if event.type == MOUSEBUTTONUP:
            mouse_pos = event.pos
            for i, tab in enumerate(self.processed_tabs):
                if tab[1].collidepoint(mouse_pos):
                    Spectator(self.displayed_content[i]).start_spectating()
