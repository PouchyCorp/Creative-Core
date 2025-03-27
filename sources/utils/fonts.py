r"""
Projet : Creative Core
Equipe : Paul Baumard, Abel Bossard, Tybalt Debruyne, Taddeo Boisseuil-Marcil
   __            _   
  / _|          | |  
 | |_ ___  _ __ | |_ 
 |  _/ _ \| '_ \| __|
 | || (_) | | | | |_ 
 |_| \___/|_| |_|\__|

Simple module to load fonts for the game
The font used is Big Blue Terminal by VileR, using the CC Attribution-ShareAlike 4.0 license
https://int10h.org/blog/2015/12/bigblue-terminal-oldschool-fixed-width-font/

Author: Tioh (Taddeo)
"""

from pygame import font
font.init()

font_path = "data/PxPlus_IBM_VGA8.ttf"
font_size = 25
TERMINAL_FONT = font.Font(font_path, font_size)
TERMINAL_FONT_BIG = font.Font(font_path, font_size + 10)
TERMINAL_FONT_VERYBIG = font.Font(font_path, font_size + 20)

STANDARD_COLOR = (255, 212, 163)