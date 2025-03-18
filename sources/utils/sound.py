r"""
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
class SoundManager:
    def __init__(self):
        """
        Class to manage sounds in the game.  
        It is a good idea to have a loading screen while loading the sounds.  
        You should not make multiple instances of this class if you dont want to wait 2sec each time you play a sound ^^"""

        # Load sounds
        self.accrocher = pygame.mixer.Sound('data/sounds/accrocher_tableau.wav') #
        self.accrocher2 = pygame.mixer.Sound('data/sounds/accrocher.mp3') #
        self.achieve = pygame.mixer.Sound('data/sounds/achieve.mp3') #
        self.blank_sound = pygame.mixer.Sound('data/sounds/blank_sound.mp3')
        self.bott = pygame.mixer.Sound('data/sounds/bot or mites.mp3')
        self.down = pygame.mixer.Sound('data/sounds/Doordown.wav') #
        self.up = pygame.mixer.Sound('data/sounds/elevator.wav') #
        self.floorcracking = pygame.mixer.Sound('data/sounds/floorcracking.mp3')
        self.incorrect = pygame.mixer.Sound('data/sounds/incorrect.mp3') #
        self.items = pygame.mixer.Sound('data/sounds/items.mp3') #
        self.mite = pygame.mixer.Sound('data/sounds/mite.mp3')
        self.mites = pygame.mixer.Sound('data/sounds/mites.mp3')
        self.mites2 = pygame.mixer.Sound('data/sounds/mites2.mp3')
        self.mites3 = pygame.mixer.Sound('data/sounds/mites3.mp3')
        self.mites4 = pygame.mixer.Sound('data/sounds/mites4.mp3')
        self.mites5 = pygame.mixer.Sound('data/sounds/mites5.mp3')
        self.noise = pygame.mixer.Sound('data/sounds/noise.mp3')
        self.rain = pygame.mixer.Sound('data/sounds/rain.mp3')
        self.robot_moving = pygame.mixer.Sound('data/sounds/robot_moving.mp3')
        self.robot = pygame.mixer.Sound('data/sounds/robot.mp3')
        self.robot1 = pygame.mixer.Sound('data/sounds/robot1.wav')
        self.robot2 = pygame.mixer.Sound('data/sounds/robot2.wav')
        self.robot3 = pygame.mixer.Sound('data/sounds/robot3.wav')
        self.robot4 = pygame.mixer.Sound('data/sounds/robot4.wav')
        self.robot5 = pygame.mixer.Sound('data/sounds/robot5.wav')
        self.robot6 = pygame.mixer.Sound('data/sounds/robot6.wav')
        self.robot7 = pygame.mixer.Sound('data/sounds/robot7.mp3')
        self.robots = pygame.mixer.Sound('data/sounds/robots.mp3')
        self.shop = pygame.mixer.Sound('data/sounds/shop.wav') #
        self.walk = pygame.mixer.Sound('data/sounds/walk.wav')
        self.wind = pygame.mixer.Sound('data/sounds/wind.mp3')

        #A list for every sounds which refers to noise blank sounds. At random moments, the loop is choosing one and play him
        self.noise_blank=[self.wind,
                          self.rain,
                          self.floorcracking
        ]
        #Random sounds for bots while moving
        self.robot=[self.robot, 
                    self.robot1,
                    self.robot2,  
                    self.robot3, 
                    self.robot4, 
                    self.robot5, 
                    self.robot6, 
                    self.robot7, 
                    self.robots]