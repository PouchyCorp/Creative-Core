r"""
Projet : Creative Core
Equipe : Paul Baumard, Abel Bossard, Tybalt Debruyne, Taddeo Boisseuil-Marcil
  _    _
 | |  | |                                                    
 | |__| | ___  _ __ ___   ___   ___  ___ _ __ ___  ___ _ __  
 |  __  |/ _ \| '_ ` _ \ / _ \ / __|/ __| '__/ _ \/ _ \ '_ \ 
 | |  | | (_) | | | | | |  __/ \__ \ (__| | |  __/  __/ | | |
 |_|  |_|\___/|_| |_| |_|\___| |___/\___|_|  \___|\___|_| |_|
                                                             
This module provides the home screen with login and registration options.

Key Features:
-------------
- Online and offline versions.
- Home screen with login and registration options (FSM implementation).
- Animated background.
- Text input boxes for username and password.

Author: Leih (Abel), with background made by Ytyt (Tybalt)
"""

import pygame as pg
from enum import Enum, auto
from ui.inputbox import InputBox
from  ui.infopopup import InfoPopup
from ui.button import Button
from utils.database import Database
import ui.sprite as sprite
from utils.fonts import TERMINAL_FONT
from math import sin

class LoginStates(Enum):
    HOME = auto()
    REGISTER = auto()
    LOGIN = auto()

class OnlineHomescreen:
    def __init__(self, server_ip, server_port):

        self.gui_state = LoginStates.HOME

        self.launch_status = {'ready' : False, 'username' : None}

        self.username_input = InputBox(10,10,600,50)
        self.password_input = InputBox(10,70,600,50)

        self.info_popups : list[InfoPopup]= []

        self.database = Database(server_ip, server_port, self.info_popups)

#-------------------------------------------------
#               BUTTON ACTIONS
#-------------------------------------------------

    def quit(self):
        if self.gui_state is LoginStates.HOME:
            from sys import exit
            exit()

    def close(self):
        self.gui_state = LoginStates.HOME

    def change_gui_to_login(self):
        self.gui_state = LoginStates.LOGIN
    
    def change_gui_to_register(self):
        self.gui_state = LoginStates.REGISTER
    
    def attempt_register(self):
        self.database.register_user(self.username_input.text, self.password_input.text)
    
    def attempt_login(self):
        status = self.database.login_user(self.username_input.text, self.password_input.text)
        if status:
            self.launch_status = {'ready' : True, 'username' : self.username_input.text}

#-------------------------------------------------
#               MAIN LOOP
#-------------------------------------------------

    def main_loop(self, win : pg.Surface) -> tuple[str, dict]:

        pg.init()
        fps = 60  # Frame rate
        CLOCK = pg.time.Clock()
        win.fill('black')
        win_rect = win.get_rect()
        pg.display.set_icon(pg.image.load('data/big_icon.png'))

        from utils.fonts import font_path
        font = pg.font.Font(font_path, 100)
        win.blit(font.render(f"Connection à {self.database.server_ip} / {self.database.server_port} ...", False, 'white'), (100, win.get_rect().centery)) # Display connecting message
        pg.display.flip()

        self.background = sprite.PRETTY_BG
        self.bg_offset = 0

        self.quitbutton = Button((0,0), self.quit, sprite.whiten(sprite.QUIT_BUTTON), sprite.QUIT_BUTTON)
        self.close_button = Button((0,0), self.close, sprite.whiten(sprite.CLOSE_BUTTON), sprite.CLOSE_BUTTON)
        self.register_button = Button((0,0), self.change_gui_to_register, sprite.whiten(sprite.REGISTER_BUTTON), sprite.REGISTER_BUTTON)
        self.login_button = Button((0,0), self.change_gui_to_login, sprite.whiten(sprite.LOGIN_BUTTON), sprite.LOGIN_BUTTON)
        self.accept_login_button = Button((0,0), self.attempt_login, sprite.whiten(sprite.CONFIRM_BUTTON), sprite.CONFIRM_BUTTON)
        self.accept_register_button = Button((0,0), self.attempt_register, sprite.whiten(sprite.CONFIRM_BUTTON), sprite.CONFIRM_BUTTON)

        self.login_button.rect.center = win_rect.center
        self.register_button.rect.center = (self.login_button.rect.centerx, self.login_button.rect.centery+self.login_button.rect.height+30)
        self.quitbutton.rect.center = (self.register_button.rect.centerx, self.register_button.rect.centery+self.register_button.rect.height+30)
        self.close_button.rect.center = (self.register_button.rect.centerx, self.register_button.rect.centery+self.register_button.rect.height+30)
        self.accept_login_button.rect.center = self.register_button.rect.center
        self.accept_register_button.rect.center = self.register_button.rect.center
        self.password_input.rect.center = self.login_button.rect.center
        self.username_input.rect.center = (self.password_input.rect.centerx, self.password_input.rect.centery-self.password_input.rect.height-30)

        border = 36
        size = (self.password_input.rect.width + border*2, self.password_input.rect.bottom-self.username_input.rect.y + border*2)
        self.inputbox_background = sprite.nine_slice_scaling(sprite.WINDOW, size, (12, 12, 12, 12)) 

        self.title_screen_size_incr = 0
        while not self.launch_status['ready']:
            CLOCK.tick(fps)  # Maintain frame rate
            mouse_pos = pg.mouse.get_pos()  # Create a coordinate object for the mouse position
            events = pg.event.get()  # Get all events from the event queue
            win.fill('blue')

            self.title_screen_size_incr += 0.1

            for event in events:
                if event.type == pg.QUIT:  # Check for quit event
                    pg.quit()  # Quit Pygame
                    from sys import exit
                    exit()

                if event.type in [pg.MOUSEBUTTONUP, pg.KEYDOWN, pg.MOUSEBUTTONDOWN]: # Check for mouse and keyboard events
                    match self.gui_state: # match the current state of the GUI using a FSM
                        case LoginStates.LOGIN:
                            self.password_input.handle_event(event)
                            self.username_input.handle_event(event)

                            self.close_button.handle_event(event)
                            self.accept_login_button.handle_event(event)

                        case LoginStates.REGISTER:
                            self.password_input.handle_event(event)
                            self.username_input.handle_event(event)

                            self.close_button.handle_event(event)
                            self.accept_register_button.handle_event(event)

                        case LoginStates.HOME:
                            self.quitbutton.handle_event(event)
                            self.register_button.handle_event(event)
                            self.login_button.handle_event(event)
            
            #draw
            self.draw(win, mouse_pos)
            
            self.render_popups(win)
            
            pg.display.flip()  # Update the display


        #if root terminated and ready to launch, returns game data
        if self.launch_status['ready']:
            return self.launch_status['username'], self.database.fetch_user_data(self.launch_status['username']), win.copy() # Return the username and the user's save data
    
    def render_popups(self, win):  
        # Iterate over existing popups to render and manage their lifetime
        for popup in self.info_popups:
            if popup.lifetime <= 0:
                self.info_popups.remove(popup)
            else:
                popup.draw(win)
                popup.lifetime -= 1

    def draw(self, WIN : pg.Surface, mouse_pos : tuple):
        WIN.blit(self.background, (0,0), (self.bg_offset, 0, *WIN.get_size()))
        self.bg_offset += 2

        if self.bg_offset > self.background.get_width()-WIN.get_width():
            self.bg_offset = 0
        
        temp_title = pg.transform.scale_by(sprite.TITLE, 1 + sin(self.title_screen_size_incr)*0.02)
        title_rect = temp_title.get_rect(center = (WIN.get_width()//2, 220))
        WIN.blit(temp_title, title_rect)

        username_label = TERMINAL_FONT.render("Nom d'utilisateur", False, (168, 112, 62))
        password_label = TERMINAL_FONT.render("Mot de passe", False, (168, 112, 62))

        match self.gui_state:
            case LoginStates.LOGIN:
                WIN.blit(self.inputbox_background, (self.username_input.rect.x-36, self.username_input.rect.y-36))
                WIN.blit(username_label, (self.username_input.rect.x, self.username_input.rect.y-username_label.get_height()))
                WIN.blit(password_label, (self.password_input.rect.x, self.password_input.rect.y-username_label.get_height()))
                self.password_input.draw(WIN)
                self.username_input.draw(WIN)
                self.close_button.draw(WIN, self.close_button.rect.collidepoint(mouse_pos))
                self.accept_login_button.draw(WIN, self.accept_login_button.rect.collidepoint(mouse_pos))

            case LoginStates.REGISTER:
                WIN.blit(self.inputbox_background, (self.username_input.rect.x-36, self.username_input.rect.y-36))
                WIN.blit(username_label, (self.username_input.rect.x, self.username_input.rect.y-username_label.get_height()))
                WIN.blit(password_label, (self.password_input.rect.x, self.password_input.rect.y-password_label.get_height()))
                self.password_input.draw(WIN)
                self.username_input.draw(WIN)
                self.close_button.draw(WIN, self.close_button.rect.collidepoint(mouse_pos))
                self.accept_register_button.draw(WIN, self.accept_register_button.rect.collidepoint(mouse_pos))

            case LoginStates.HOME:
                self.quitbutton.draw(WIN, self.quitbutton.rect.collidepoint(mouse_pos))
                self.register_button.draw(WIN, self.register_button.rect.collidepoint(mouse_pos))
                self.login_button.draw(WIN, self.login_button.rect.collidepoint(mouse_pos))
        

class OfflineHomescreen:
    def __init__(self):
        self.ready_status = False

    def play(self):
        self.ready_status = True

    def quit(self):
        from sys import exit
        exit()

    def main_loop(self, win : pg.Surface):

        pg.init()
        fps = 60  # Frame rate
        CLOCK = pg.time.Clock()
        win.fill('black')
        win_rect = win.get_rect()
        pg.display.set_icon(pg.image.load('data/big_icon.png'))

        import ui.sprite as sprite

        background = sprite.PRETTY_BG
        bg_offset = 0

        quit_button = Button((0,0), self.quit, sprite.whiten(sprite.QUIT_BUTTON) , sprite.QUIT_BUTTON)
        play_button = Button((0,0), self.play, sprite.whiten(sprite.PLAY_BUTTON), sprite.PLAY_BUTTON)

        play_button.rect.center = win_rect.center
        quit_button.rect.center = play_button.rect.centerx, play_button.rect.centery + play_button.rect.width + 30
        title_screen_size_incr = 0
        while not self.ready_status:
            CLOCK.tick(fps)  # Maintain frame rate
            events = pg.event.get()  # Get all events from the event queue
            win.fill('blue')
            mouse_pos = pg.mouse.get_pos()

            title_screen_size_incr += 0.1

            for event in events:
                if event.type == pg.QUIT:  # Check for quit event
                    pg.quit()  # Quit Pygame
                    from sys import exit
                    exit()

                if event.type in [pg.MOUSEBUTTONDOWN]:
                    quit_button.handle_event(event)
                    play_button.handle_event(event)
            
            #draw
            win.blit(background, (0,0), (bg_offset, 0, *win.get_size()))
            bg_offset += 2

            temp_title = pg.transform.scale_by(sprite.TITLE, 1 + sin(title_screen_size_incr)*0.02)
            title_rect = temp_title.get_rect(center = (win.get_width()//2, 220))
            win.blit(temp_title, title_rect)

            quit_button.draw(win, quit_button.rect.collidepoint(mouse_pos))
            play_button.draw(win, play_button.rect.collidepoint(mouse_pos))

            if bg_offset > background.get_width()-win.get_width():
                bg_offset = 0
            
            pg.display.flip()
        
        return win.copy()