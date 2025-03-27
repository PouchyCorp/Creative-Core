#Projet : Creative Core
#Equipe : Paul Baumard, Abel Bossard, Tybalt Debruyne, Taddeo Boisseuil-Marcil

"""This is the test file that was used to test our nine slice scaling function. It creates a window that can be resized and shows the nine slice scaling in action. It is not part of the final project and is only used for testing purposes."""

import pygame as pg
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../sources'))) # Magic to make the imports work, taken on stackoverflow
from ui.sprite import nine_slice_scaling, load_image

def main():
    pg.init()
    screen = pg.display.set_mode((800, 600))

    # Load the window sprite
    window_sprite = load_image("data/bord.png")
    margins = (12, 12, 12, 12)  # Example margins

    running = True
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

        mouse_x, mouse_y = pg.mouse.get_pos()

        # Ensure the target size is at least as large as the margins to avoid crashing
        target_width = max(mouse_x, margins[0] + margins[1])
        target_height = max(mouse_y, margins[2] + margins[3])

        scaled_image = nine_slice_scaling(window_sprite, (target_width, target_height), margins)

        screen.fill((0, 0, 0))

        screen.blit(scaled_image, (0, 0))

        pg.display.flip()

    pg.quit()
    sys.exit()

if __name__ == "__main__":
    main()
