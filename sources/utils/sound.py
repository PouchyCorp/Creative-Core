r"""
Projet : Creative Core
Equipe : Paul Baumard, Abel Bossard, Tybalt Debruyne, Taddeo Boisseuil-Marcil
                            _     
                           | |    
  ___  ___  _   _ _ __   __| |___ 
 / __|/ _ \| | | | '_ \ / _` / __|
 \__ \ (_) | |_| | | | | (_| \__ \
 |___/\___/ \__,_|_| |_|\__,_|___/

Key Features:
-------------
- Class to manage sounds in the game.

Every sounds are free access and have been taken in pixabay.com

Author: Leih (Abel)
"""

import pygame 
import random
from utils.timermanager import TimerManager 

class SoundManager:
    def __init__(self, volume, timer):
        """
        Class to manage sounds in the game.  
        It is a good idea to have a loading screen while loading the sounds.  
        You should not make multiple instances of this class if you dont want to wait 2sec each time you play a sound ^^"""
        self.timer : TimerManager = timer

        # Set the volume from the config file
        self.volume = volume/100 # because the volume is a percentage

        # Load sounds
        self.accrocher = pygame.mixer.Sound('data/sounds/accrocher_tableau.wav') #
        self.achieve = pygame.mixer.Sound('data/sounds/achieve.mp3') #
        self.shop = pygame.mixer.Sound('data/sounds/shop.wav') #
        self.down = pygame.mixer.Sound('data/sounds/Doordown.wav') #
        self.up = pygame.mixer.Sound('data/sounds/elevator.wav') #
        self.incorrect = pygame.mixer.Sound('data/sounds/incorrect.wav') #
        self.items = pygame.mixer.Sound('data/sounds/items.mp3') #
        self.mite = pygame.mixer.Sound('data/sounds/mite.wav') #

        classic_sounds = [self.accrocher, self.achieve, self.shop, self.down, self.up, self.incorrect, self.items, self.mite]
        for sound in classic_sounds:
            sound.set_volume(0.5*self.volume)

        self.floorcracking = pygame.mixer.Sound('data/sounds/floorcracking.mp3')
        self.blank_sound = pygame.mixer.Sound('data/sounds/blank_sound.mp3')
        self.noise = pygame.mixer.Sound('data/sounds/noise.mp3')
        self.rain = pygame.mixer.Sound('data/sounds/rain.mp3')
        self.wind = pygame.mixer.Sound('data/sounds/wind.mp3')

        self.robot_moving = pygame.mixer.Sound('data/sounds/robot_moving.mp3')
        self.robot = pygame.mixer.Sound('data/sounds/robot.mp3')
        self.robot1 = pygame.mixer.Sound('data/sounds/robot1.wav')
        self.robot2 = pygame.mixer.Sound('data/sounds/robot2.wav')
        self.robot3 = pygame.mixer.Sound('data/sounds/robot3.wav')
        self.robot4 = pygame.mixer.Sound('data/sounds/robot4.wav')
        self.robot5 = pygame.mixer.Sound('data/sounds/robot5.wav')
        self.robot6 = pygame.mixer.Sound('data/sounds/robot6.wav')
        self.robots = pygame.mixer.Sound('data/sounds/robots.mp3')
        self.walk = pygame.mixer.Sound('data/sounds/walk.wav')

        self.music_begin = pygame.mixer.Sound('data/sounds/musiqueintro.wav')
        self.music_ambiant = pygame.mixer.Sound('data/sounds/Musiquejeu.wav')

        self.music_begin.set_volume(0.8*self.volume)
        self.music_ambiant.set_volume(0.2*self.volume)

        #A list for every sounds which refers to noise blank sounds. At random moments, the loop is choosing one and play him
        self.noise_blank=[self.wind,
                          self.rain,
                          self.floorcracking
        ]

        for sound in self.noise_blank:
            sound.set_volume(0.2*self.volume)
        #Random sounds for bots while moving
        self.robot=[self.robot, 
                    self.robot1,
                    self.robot2,  
                    self.robot3, 
                    self.robot4, 
                    self.robot5, 
                    self.robot6, 
                    self.robots,
                    self.robot_moving,
                    self.walk]

        for sound in self.robot:
            sound.set_volume(0.1*self.volume)
        
    def play_random_ambiant_sound(self):
        """
        Play a random sound in the list of noise blank sounds
        This is a recursive function, it will play a sound, then wait for the sound to finish, then play another sound a random time after the end of the first sound
        """
        chosen_sound = random.choice(self.noise_blank)
        chosen_sound.play(fade_ms=1000)
        self.timer.create_timer(chosen_sound.get_length()-1, chosen_sound.fadeout, arguments=(1000,))
        self.timer.create_timer(chosen_sound.get_length()+random.randint(0,10), self.play_random_ambiant_sound)
    
    def play_random_robot_sound(self):
        """
        Play a random sound in the list of robot sounds
        This is called randomly when a robot is freed
        """
        chosen_sound = random.choice(self.robot)
        chosen_sound.play(fade_ms=500)
        self.timer.create_timer(chosen_sound.get_length()-0.5, chosen_sound.fadeout, arguments=(1000,))