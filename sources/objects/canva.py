r"""
Projet : Creative Core
Equipe : Paul Baumard, Abel Bossard, Tybalt Debruyne, Taddeo Boisseuil-Marcil
   _____                      
  / ____|                     
 | |     __ _ _ ____   ____ _ 
 | |    / _` | '_ \ \ / / _` |
 | |___| (_| | | | \ V / (_| |
  \_____\__,_|_| |_|\_/ \__,_|

This module manages the game's art system, including the canvas and painting mechanics.

Key Features:
-------------
- Provides UI elements for painting and saving.
- Arm and sprayer animation using inverse kinematics.
- Color selection and painting mechanics.
- Numerous popups for user feedback and information.
- Particle effects for painting animations.

Notes:
------
Definitely needs to be refactored to separate the UI elements from the game logic, however, the current implementation is functional.
The animation handler should be moved to a separate module.

Author: Ytyt (Tybalt) (with contributions from Paul)
"""

import pygame as pg
from utils.coord import Coord
from objects.placeable import Placeable
from objects.patterns import Pattern
from ui.inputbox import InputBox
from ui.sprite import FRAME_PAINTING, invert_alpha, PAINT_BUTTON, SAVE_BUTTON, CANVA_UI_NAME, CANVA_UI_PAINT, whiten, ARM, SPRAYER, point_rotate, inverse_kinematics, get_locked_surface, COLOR_BUTTON_BG
from ui.button import Button
from ui.confirmationpopup import ConfirmationPopup
from ui.infopopup import InfoPopup
from utils.fonts import TERMINAL_FONT_VERYBIG
from math import sqrt, ceil, pi, sin
from objects.particlesspawner import CircleParticleSpawner, ParticleSpawner
from utils.sound import SoundManager

COLORS = [(11,23,33), (105,117,130), (213,226,240),(141,171,131) , (217,137,76), (232, 216, 153), (194, 49, 47), (117, 97, 156), (91, 138, 203), (42,30,66)]

offsetx = -60 # Needed to adjust the position of the control panel, because sadly it was not written with relative coordinates
offsety = -90

class Canva:
    def __init__(self, coord : Coord, game, color_buttons_unlocked=False): 
        """Initialize the Canva object with its properties and UI elements."""
        self.coord = coord

        # Set the size and surface of the canvas
        self.size = (672,1020)
        self.surf = pg.Surface(self.size)
        self.bg_color = (236, 235, 222)
        self.surf.fill(self.bg_color)
        
        # Set the rectangle and position of the canvas
        self.rect = self.surf.get_rect()
        self.rect.x, self.rect.y = self.coord.xy
        
        # Initialize UI elements
        # Initialize UI elements
        self.name_input = InputBox(1380+offsetx, 372+offsety, 198, 40)
        self.confirm_button = Button((1584+offsetx, 378+offsety), self.attempt_save, whiten(SAVE_BUTTON), SAVE_BUTTON)
        self.paint_button = Button((1464+offsetx, 228+offsety), self.start_painting, whiten(PAINT_BUTTON), PAINT_BUTTON)

        self.color_buttons_unlocked = color_buttons_unlocked

        # Initialize color selection buttons
        self.color_buttons_pos = (1350, 528)
        self.color_buttons = self.init_color_buttons(self.color_buttons_unlocked) # Initialize the color buttons with the default colors
        
        # Import the game logic and set the game reference
        from core.logic import Game
        self.game : Game = game

        # Initialize canvas properties
        self.name = "peinture"
        self.placed_patterns : list[Pattern] = []
        self.holded_pattern : Pattern = None

        self.total_price = 0
        self.total_beauty = 0

        # Initialize robotic arm properties
        self.arm_root = (522, 469)
        self.default_target = (605, 454)
        self.arm = {'surf' : ARM.copy(), 'len' : ARM.copy().get_size()[0], 'angle' : 0}
        self.forearm = {'surf' : ARM.copy(), 'len' : ARM.copy().get_size()[0], 'angle' : 0}
        self.arm['angle'], self.forearm['angle'] = inverse_kinematics(self.default_target, self.arm_root, self.arm['len'], self.forearm['len'])

        # Set the current color for painting
        self.current_color = (11,23,33)

        self.color_gauge_incr = -pi

        # Initialize the animation handler
        self.animation_handler = CanvaAnimationHandler(self)

    def change_color(self, color):
        """Change the current color used for painting.""" 
        self.current_color = color
    
    def error_popup(self):
        """Show an error popup when the player tries to paint without placing any patterns.""" 
        self.game.popups.append(InfoPopup("Vous ne pouvez pas peindre sans pochoirs !"))
        self.game.sound_manager.incorrect.play()
    
    def color_blocked_popup(self):
        """Show a popup when the player tries to select a locked color.""" 
        self.game.popups.append(InfoPopup("Vous n'avez pas encore débloqué cette couleur !"))
        self.game.sound_manager.incorrect.play()

    def init_color_buttons(self, additional_colors_unlocked) -> list[Button]:
        """Initialize the color selection buttons.""" 
        buttons : list[Button] = []
        size = (84,84)
        x, y = self.color_buttons_pos

        if not additional_colors_unlocked:
            unlocked_colors = COLORS[:3]
        else:
            unlocked_colors = COLORS

        for i, color in enumerate(COLORS):
            surf = pg.Surface(size)
            surf.fill(color)

            if color in unlocked_colors:
                buttons.append(Button((x, y), self.change_color, whiten(surf), surf, [color]))
            else:
                locked_surf = get_locked_surface(surf)
                buttons.append(Button((x, y), self.color_blocked_popup, whiten(locked_surf), locked_surf, []))

            if i == 4:
                x+=size[0]+12
                y = self.color_buttons_pos[1]
            else:
                y+=size[1]+12
        return buttons

    def get_placeable(self) -> Placeable:
        """Create and return a Placeable object from the current canvas.""" 
        scaled_surf = pg.transform.scale_by(self.surf.copy(),0.5).convert()
        FRAME_PAINTING.blit(scaled_surf,(12,12))
        placeable = Placeable(self.name, self.coord.copy(), FRAME_PAINTING.copy(), beauty=self.total_beauty, tag="decoration", flags=["static"])
        self.reset()
        return placeable
    
    def check_price(self, price):
        """Check if the player has enough money to paint and deduct the price if possible.""" 
        if self.game.money - price >= 0:
            self.game.money -= price
            return True
        else:
            self.game.popups.append(InfoPopup("Vous n'avez pas assez d'argent pour peindre :("))
            self.game.sound_manager.incorrect.play()
            return False

    def get_price(self):
        """Calculate and return the total price of all placed patterns.
        Side effect: Set the total price of the canvas.""" 
        self.total_price = 0
        for pattern in self.placed_patterns:
            self.total_price += pattern.price
        return self.total_price

    def add_to_beauty(self, patterns : list[Pattern]):
        """Add the beauty value of the given patterns to the total beauty.""" 
        for pattern in patterns:
            self.total_beauty += pattern.beauty
            self.total_beauty = round(self.total_beauty, 2)
    
    def reset(self):
        """Reset the canvas to its initial state.""" 
        self.__init__(self.coord, self.game, self.color_buttons_unlocked)
    
    def get_round_mask(self, surface : pg.Surface, xy : tuple, circle_radius):
        """Create and return a circular mask for the given surface.""" 
        circle_surf = pg.Surface((circle_radius * 2, circle_radius * 2), pg.SRCALPHA)
        pg.draw.circle(circle_surf, (255, 255, 255, 255), (circle_radius, circle_radius), circle_radius)

        circle_surf.blit(surface, (-xy[0], -xy[1]), special_flags=pg.BLEND_RGBA_MIN)
        return circle_surf
    
    def get_next_surf(self):
        """Generate and return the next surface to be painted.
        This was tiedious to write, but it's a simple function.""" 
        next_surf = pg.Surface(self.size)
        next_surf = next_surf.convert_alpha()
        next_surf.fill((0,0,0,0))

        for pattern in self.placed_patterns:
            self.draw_pattern(next_surf, pattern) # Draw the pattern on the next surface

        invert_alpha(next_surf) # Invert the alpha channel of the next surface
        
            
        next_surf.fill(self.current_color+tuple([0]), special_flags=pg.BLEND_RGBA_MAX) # Fill the next surface with the current color, using the maximum alpha value, a clever use of that filter
        return next_surf
    
    def start_painting(self):
        """Start the painting process if the player has enough money.""" 
        if self.check_price(self.get_price()): # Check if the player has enough money
            self.game.sound_manager.mite.play()
            self.animation_handler.start_anim(self.get_next_surf()) # Start the painting animation
            self.add_to_beauty(self.placed_patterns) # Add the beauty value of the patterns to the total beauty
            
    
    def draw_pattern(self, surf, pattern : Pattern):
        """Imprint the pattern on the given surface.""" 
        relative_pos = (pattern.rect.x - self.coord.x,
                        pattern.rect.y - self.coord.y)

        surf.blit(pattern.get_effect(), relative_pos)

    def place_pattern(self, pattern : Pattern):
        """Place a moveable pattern on the canvas.""" 
        self.placed_patterns.append(pattern)
        self.get_price()

    def hold_pattern(self, pattern):
        """Hold a pattern for moving.""" 
        self.placed_patterns.remove(pattern) # Remove the pattern from the canvas
        self.get_price() # Update the total price
        self.holded_pattern = pattern
        self.holded_pattern.rect.center = Coord(0, pg.mouse.get_pos()).get_pixel_perfect()
        self.game.sound_manager.items.play()
    
    def hold_pattern_from_drawer(self, pattern):
        """Hold a pattern from the drawer for moving.
        This method is called by the PatternHolder object when a pattern is clicked.""" 
        self.holded_pattern = pattern.copy()
        self.holded_pattern.rect.center = Coord(0, pg.mouse.get_pos()).get_pixel_perfect()
    
    def drop_pattern(self, pos):
        """Drop the held pattern at the given position.""" 
        if self.rect.collidepoint(pos):
            # Place the pattern on the canvas if the position is within the canvas bounds
            self.holded_pattern.rect.center = pos
            self.place_pattern(self.holded_pattern)
            self.game.sound_manager.items.play()
        else:
            # Show a popup if the pattern is dropped outside the canvas
            self.game.popups.append(InfoPopup("Vous reposez le pochoir dans l'armoire."))
        self.holded_pattern = None

    def attempt_save(self):
        """Attempt to save the current canvas.""" 
        # Set the canvas name from the input box and show a confirmation popup
        self.name = self.name_input.text
        self.game.confirmation_popups.append(ConfirmationPopup(self.game.win, "Sauvegarder la toile ?", self.game.save_canva))

    def draw(self, win : pg.Surface):
        """Draw the canvas and its elements on the given window surface.""" 
        # Draw the canvas surface
        win.blit(self.surf, self.coord.xy)

        # Draw all placed patterns on the canvas
        for placed_pattern in self.placed_patterns:
            placed_pattern.draw(win)
        
        # Draw the held pattern if there is one
        if self.holded_pattern:
            self.holded_pattern.draw(win)

        # Draw and update the color gauge
        self.color_gauge_incr += pi/60
        if self.color_gauge_incr > pi:
            self.color_gauge_incr = -pi
        
        color_gauge = pg.Surface((80, 120))
        color_gauge.fill(self.current_color)
        win.blit(color_gauge, (1386+offsetx,164+offsety+sin(self.color_gauge_incr)*5))

        # Draw UI
        win.blit(CANVA_UI_PAINT, (1356+offsetx, 114+offsety))
        win.blit(CANVA_UI_NAME, (1356+offsetx, 314+offsety))

         # Draw the price and total beauty text
        price_label = TERMINAL_FONT_VERYBIG.render(str(self.total_price)+"¥", False, (255, 212, 163))
        price_rect = price_label.get_rect(bottomleft=(1584+offsetx, 210+offsety))
        win.blit(price_label, price_rect)

        beauty_label = TERMINAL_FONT_VERYBIG.render(str(self.total_beauty), False, (255, 212, 163))
        beauty_rect = beauty_label.get_rect(bottomleft=(1554+offsetx, 486+offsety))
        win.blit(beauty_label, beauty_rect)

        # Draw the input box and buttons
        self.name_input.draw(win)
        self.confirm_button.draw(win, self.confirm_button.rect.collidepoint(pg.mouse.get_pos()))
        self.paint_button.draw(win, self.paint_button.rect.collidepoint(pg.mouse.get_pos()))
        
        win.blit(COLOR_BUTTON_BG, (1296, 426))
        for button in self.color_buttons:
            button.draw(win, button.rect.collidepoint(pg.mouse.get_pos()))
        
        # Draw the robotic arms
        self.blit_arms(win)
    
    def blit_arms(self, win):
        """Draw the robotic arms on the given window surface.""" 
        # Rotate and draw the arm
        rotated_surf, rect = point_rotate(self.arm['surf'], self.arm_root, (5,5), -self.arm['angle'])
        relative_arm_vector = pg.Vector2(self.arm['len'], 0)
        rotated_arm_vector = relative_arm_vector.rotate(self.arm['angle'])
        # The position of the 'elbow' of the arm by adding the arm vector to the root
        global_arm_end_pos = rotated_arm_vector + pg.Vector2(self.arm_root)

        # Rotate and draw the forearm
        rotated_surf2, rect2 = point_rotate(self.forearm['surf'], global_arm_end_pos, (5,5), -self.forearm['angle'])
        relative_forearm_vector = pg.Vector2(self.forearm['len'], 0)
        rotated_forearm_vector = relative_forearm_vector.rotate(self.forearm['angle'])
        # The position of the'hand' of the arm by adding all the vectors
        global_forearm_end_pos = rotated_forearm_vector + rotated_arm_vector + pg.Vector2(self.arm_root) 

        # Draw the sprayer at the end of the forearm
        sprayer_rect = SPRAYER.get_rect(center = global_forearm_end_pos)

        win.blit(rotated_surf, rect)
        win.blit(rotated_surf2, rect2)
        win.blit(SPRAYER, sprayer_rect)

    def handle_event(self, event):
        """Handle user input events.""" 
        mouse_pos = pg.mouse.get_pos()

        # Handle events for the name input box, paint button, and confirm button
        self.name_input.handle_event(event)
        self.paint_button.handle_event(event)
        self.confirm_button.handle_event(event)
        
        # Handle events for the color selection buttons
        for button in self.color_buttons:
            button.handle_event(event)

        # Check if a pattern is clicked and hold it
        eventual_collided_pattern = [pattern for pattern in self.placed_patterns if pattern.rect.collidepoint(mouse_pos)]
        if event.type == pg.MOUSEBUTTONDOWN and eventual_collided_pattern:
            self.hold_pattern(eventual_collided_pattern[0])

        # Handle the held pattern's movement and dropping
        if self.holded_pattern:
            if event.type == pg.MOUSEBUTTONUP:
                self.drop_pattern(Coord(0, mouse_pos).get_pixel_perfect())

            if event.type == pg.MOUSEMOTION:
                self.holded_pattern.rect.center = Coord(0, mouse_pos).get_pixel_perfect()

        return False
    
class CanvaAnimationHandler:
    """
    A handler class for managing painting animations on a Canva object.
    """
    def __init__(self, canva):
        """Initialize the AnimationHandler with a reference to the Canva object.""" 
        self.canva : Canva = canva

    def start_anim(self, next_surf):
        """Start the painting animation with the given surface.
        This is a sort of turtle graphics implementation.""" 
        # Define the radius of the circular mask and the step size for the painting animation
        circle_radius = 120
        step = 25

        # Calculate optimal corner and height for the circular mask
        optimal_corner = ceil((circle_radius - (circle_radius * sqrt(2) / 2))) #ceil is used to round up to the nearest integer
        optimal_height = ceil(circle_radius * sqrt(2))
        width = (self.canva.size[0] - (circle_radius + optimal_corner))

        # Initialize the paint gun position
        paint_gun_pos = [-optimal_corner-100, -optimal_corner+self.canva.size[1]//2-25]

        # Create particle spawners for the painting animation
        center = Coord(0, (self.canva.coord.x + paint_gun_pos[0] + circle_radius, self.canva.coord.y + paint_gun_pos[1] + circle_radius))
        static_particles, aura_particles = self.create_particles(center, circle_radius)

        # Add the particle spawners to the particle spawner list
        self.canva.game.particle_spawners[0] += [static_particles, aura_particles]

        # Create the path stack for the painting animation
        path_stack = self.create_path_stack(width, optimal_height)
        current_dir = path_stack.pop()

        # Initialize animation state variables
        active = False
        static_particles.active = False
        aura_particles.active = False

        # Create a copy of the current canvas surface to apply the next surface
        true_next_surf = self.canva.surf.copy()
        true_next_surf.blit(next_surf, (0, 0))

        # Initialize the clock for controlling the animation frame rate
        clock = pg.time.Clock()

        # Start the painting animation loop
        while path_stack or current_dir[1] > 0:
            clock.tick(60)

            # Check if the current direction step is completed
            if current_dir[1] <= 0:
                current_dir = path_stack.pop()

            # Toggle the active state of the particles and animation
            if current_dir == 'toggle':
                active = not active
                static_particles.active = not static_particles.active
                aura_particles.active = not aura_particles.active
                current_dir = path_stack.pop()

            # Apply the circular mask to the canvas surface if active
            if active:
                self.canva.surf.blit(self.canva.get_round_mask(next_surf, tuple(paint_gun_pos), circle_radius), paint_gun_pos)

            # Decrease the current direction step by the step size
            current_dir[1] -= step

            # Calculate the next step size
            next_step = step + current_dir[1] if current_dir[1] < 0 else step

            # Update the paint gun position based on the current direction and step size
            self.update_paint_gun_pos(current_dir[0], paint_gun_pos, next_step)

            # Update the center position for the particle spawners
            mouse_pos = Coord(0, pg.mouse.get_pos())
            center.xy = (self.canva.coord.x + paint_gun_pos[0] + circle_radius, self.canva.coord.y + paint_gun_pos[1] + circle_radius)

            # Update and draw the game state
            self.canva.game.update(mouse_pos)
            self.canva.game.draw(mouse_pos)
            self.canva.blit_arms(self.canva.game.win)

            # Update the angles of the robotic arms based on the new center position
            self.canva.arm['angle'], self.canva.forearm['angle'] = inverse_kinematics(center.xy, self.canva.arm_root, self.canva.arm['len'], self.canva.forearm['len'])

            # Refresh the display
            pg.display.flip()

        # Finalize the painting animation by setting the canvas surface to the true next surface
        self.canva.surf = true_next_surf
        static_particles.active = False
        aura_particles.active = False

        # Schedule the removal of the particle spawners after all the particles should've vanish
        self.canva.game.timer.create_timer(5, self.canva.game.particle_spawners[0].remove, arguments=[static_particles])
        self.canva.game.timer.create_timer(5, self.canva.game.particle_spawners[0].remove, arguments=[aura_particles])

    def create_particles(self, center, circle_radius):
        """Create and return static and aura particle spawners.""" 
        static_particles = CircleParticleSpawner(center, circle_radius, pg.Vector2(0, 0), self.canva.current_color, 600, density=10, dir_randomness=0, radius=(10, 20))
        aura_particles = ParticleSpawner(center, pg.Vector2(0, 0), self.canva.current_color, 60, dir_randomness=2)
        return static_particles, aura_particles

    def create_path_stack(self, width, optimal_height):
        """Create and return the path stack for the painting animation.""" 
        return [["U", self.canva.size[1]//2], ["L", 100-25], 'toggle', ["L", width+25], ["D", optimal_height], ["R", width], ["D", optimal_height],
                ["L", width], ["D", optimal_height], ["R", width], ["D", optimal_height],
                ["L", width], ["D", optimal_height], ["R", width], 'toggle', ["R", 100], ["U", self.canva.size[1]//2-25]]

    def update_paint_gun_pos(self, direction, paint_gun_pos, step):
        """Update the paint gun position based on the current direction and step.""" 
        match direction:
            case "R":
                paint_gun_pos[0] += step
            case "L":
                paint_gun_pos[0] -= step
            case "D":
                paint_gun_pos[1] += step
            case "U":
                paint_gun_pos[1] -= step