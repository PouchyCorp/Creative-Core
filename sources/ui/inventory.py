r"""
Projet : Creative Core
Equipe : Paul Baumard, Abel Bossard, Tybalt Debruyne, Taddeo Boisseuil-Marcil
  _                      _                         __      _                 
 (_)                    | |                       / /     | |                
  _ _ ____   _____ _ __ | |_ ___  _ __ _   _     / /   ___| |__   ___  _ __  
 | | '_ \ \ / / _ \ '_ \| __/ _ \| '__| | | |   / /   / __| '_ \ / _ \| '_ \ 
 | | | | \ V /  __/ | | | || (_) | |  | |_| |  / /    \__ \ | | | (_) | |_) |
 |_|_| |_|\_/ \___|_| |_|\__\___/|_|   \__, | /_/     |___/_| |_|\___/| .__/ 
                                        __/ |                         | |    
                                       |___/                          |_|    

Key Features:
-------------
*Inventory*
- Manages the player's inventory.
- Allows the player to change floors rapidly with buttons on the right.
- Items are displayed in a grid with a maximum of 8 items per page, page navigation buttons are provided.
- Inventory items are given a thumbnail (which is compressed with a funny method) and a label.

*Shop*
- Inherits from Inventory.
- Unlocked at floor 2.
- Allows the player to buy items from the shop.
- The inheritance allows the shop to use the same rendering methods as the inventory.

Author: Pouchy (Paul), with contributions from Tioh and Ytyt.
"""


from objects.placeable import Placeable
from utils.coord import Coord
from pygame import Surface, transform, BLEND_RGB_MIN
from ui.sprite import WINDOW, nine_slice_scaling, ARROW_LEFT, ARROW_RIGHT, whiten, CLOSE_BUTTON, DESTRUCTION_BUTTON
from ui.confirmationpopup import ConfirmationPopup
from ui.infopopup import InfoPopup
from ui.button import Button
from objects.particlesspawner import ConfettiSpawner
from math import ceil
from utils.fonts import TERMINAL_FONT, TERMINAL_FONT_BIG, TERMINAL_FONT_VERYBIG, STANDARD_COLOR

BORDER_AROUND_WINDOW = 24
OBJECT_SIZE = 180
ITEMS_PER_PAGE = 8


class Inventory:
    def __init__(self, change_floor_func, quit_func, title: str = "Inventory", content : list[Placeable] = []) -> None:
        """Initializes the inventory with an optional title."""
        self.inv: list[Placeable] = content  # List of owned items
        self.displayed_objects: list[tuple[Placeable, Surface]] = []  # Rendered items on the current page
        self._page: int = 0  # Current page index
        self.font = TERMINAL_FONT # Font for labels
        self.title = title  # Title of the inventory
        width = BORDER_AROUND_WINDOW * 2 + OBJECT_SIZE*2 + 20
        height = OBJECT_SIZE*5
        self.window_sprite = nine_slice_scaling(WINDOW, (width, height), (12, 12, 12, 12))
        self.sound_manager = None

        # Navigation buttons
        self.button_prev = Button((60,984), self.handle_navigation_left, whiten(ARROW_LEFT), ARROW_LEFT)
        self.button_next = Button((292,984), self.handle_navigation_right, whiten(ARROW_RIGHT), ARROW_RIGHT)

        SCALED_ARROW_RIGHT = transform.scale_by(ARROW_RIGHT, 2)
        SCALED_ARROW_LEFT = transform.scale_by(ARROW_LEFT, 2)

        self.up_button = Button((1758, 228), change_floor_func, 
                        whiten(transform.rotate(SCALED_ARROW_RIGHT, 90)), 
                        transform.rotate(SCALED_ARROW_RIGHT, 90), [1])
        self.down_button = Button((1758,498), change_floor_func, 
                            whiten(transform.rotate(SCALED_ARROW_LEFT, 90)), 
                            transform.rotate(SCALED_ARROW_LEFT, 90), [-1])
        
        self.quit_button = Button((786,930), quit_func, 
                            whiten(CLOSE_BUTTON), 
                            CLOSE_BUTTON)
        
        self.destruction_button = Button((1332, 930), int,
                            whiten(DESTRUCTION_BUTTON),
                            DESTRUCTION_BUTTON)
        
        
    def init(self):
        """Initializes the objects for rendering on the current page."""
        # Paginate items
        start = self._page * ITEMS_PER_PAGE
        end = (self._page + 1) * ITEMS_PER_PAGE
        self.displayed_objects = self.inv[start:end]

        self._process_objects()

    def _process_objects(self):
        """Processes each object for rendering on the current page."""
        processed_objects = []

        for ind, obj in enumerate(self.displayed_objects):
            # Scale the object to fit within a thumbnail
            biggest_side = max(obj.rect.width, obj.rect.height)
            scale_ratio = OBJECT_SIZE / biggest_side
            thumbnail_surf = transform.scale_by(obj.surf, scale_ratio)
            thumbnail_rect = thumbnail_surf.get_rect()

            # Apply greyscale if the object is placed
            if obj.placed:
                thumbnail_surf.fill((50, 50, 50), special_flags=BLEND_RGB_MIN)

            # Position the thumbnail
            thumbnail_rect.centerx = 324-OBJECT_SIZE-20 if ind % 2 == 0 else 324 # Big blob of magic numbers
            thumbnail_rect.y = 84 + (220 * (ind // 2))

            # Create a new Placeable for the thumbnail
            thumbnail_placeable = Placeable(obj.name, Coord(obj.coord.room_num, thumbnail_rect.topleft), thumbnail_surf, price=obj.price)
            thumbnail_placeable.id = obj.id
            thumbnail_placeable.pixelise()

            # Create a label for the object
            label_surf = self.font.render(obj.name, False, STANDARD_COLOR)

            # Add to processed list
            processed_objects.append((thumbnail_placeable, label_surf))

        self.displayed_objects = processed_objects

    def draw(self, win: Surface, mouse_pos: Coord):
        """Draws the inventory or shop interface on the screen."""
        win.blit(self.window_sprite, (12, 60))
        self._draw_labels(win)
        self._mouse_highlight(win, mouse_pos)

        # Draw objects and their labels
        win.blits([(plcb.surf, plcb.rect.topleft) for plcb, _ in self.displayed_objects])
        win.blits([(txt_surf, (plcb.rect.centerx-(txt_surf.get_width()//2), plcb.rect.y + 190)) for plcb, txt_surf in self.displayed_objects])

        # Draw navigation buttons
        self._draw_navigation_buttons(win, mouse_pos)

    def _draw_labels(self, win: Surface):
        """Draws the different labels on the inventory window."""
        title_surf = TERMINAL_FONT_VERYBIG.render(self.title, False, STANDARD_COLOR)
        page_surf = self.font.render(f"Page {self._page + 1}/{ceil((len(self.inv)+1)/ITEMS_PER_PAGE)}", False, STANDARD_COLOR) # Big blob of magic numbers to render the page number
        win.blit(title_surf, (self.window_sprite.get_width()//2-title_surf.get_width()//2, 12))
        win.blit(page_surf, (168, 1002))

    def _mouse_highlight(self, win: Surface, mouse_pos: Coord):
        """Highlights the item under the mouse pointer."""
        for placeable, _ in self.displayed_objects:
            if placeable.rect.collidepoint(mouse_pos.xy):
                placeable.draw_outline(win, (150, 150, 255))

    def _draw_navigation_buttons(self, win: Surface, mouse_pos):
        """Draws the previous and next page buttons."""
        self.button_next.draw(win, self.button_next.rect.collidepoint(mouse_pos.xy))
        self.button_prev.draw(win, self.button_prev.rect.collidepoint(mouse_pos.xy))

    def handle_navigation_left(self):
        """Handles navigation button clicks to change pages."""
        if self._page > 0:
            self._page -= 1
            self.init()

    def handle_navigation_right(self):
        if (self._page + 1) * ITEMS_PER_PAGE < len(self.inv):
            self._page += 1
            self.init()

    def handle_navigation(self, event):
        self.button_next.handle_event(event)
        self.button_prev.handle_event(event)

    def handle_click(self, mouse_pos):
        """returns the placeable contained in inventory if all conditions are valid : placeable not already placed, mouse clicked on it"""
        clicked_showed_obj_id = self._select_item(mouse_pos)  # Check if an inventory item was clicked, and if the object is already placed
        if clicked_showed_obj_id:
            clicked_obj = self._search_by_id(clicked_showed_obj_id)  # Retrieve the object by its ID
            if not clicked_obj.placed:
                return clicked_obj
        return None

    def _select_item(self, mouse_pos: Coord) -> str | None:
        """Returns the ID of the selected item, or None if no item is selected or the item is already placed."""
        for placeable, _ in self.displayed_objects:
            if placeable.rect.collidepoint(mouse_pos.xy) and not placeable.placed:
                return placeable.id
        return None

    def _search_by_id(self, item_id: int) -> Placeable | None:
        """Finds and returns the first placeable matching the given ID."""
        for obj in self.inv:
            if obj.id == item_id:
                return obj
        return None

    def draw_floor_navigation_buttons(self, win : Surface, mouse_pos : Coord):
        """Draws the floor navigation buttons on the right side of the screen."""
        self.up_button.draw(win, self.up_button.rect.collidepoint(mouse_pos.xy))
        self.down_button.draw(win, self.down_button.rect.collidepoint(mouse_pos.xy))
        self.quit_button.draw(win, self.quit_button.rect.collidepoint(mouse_pos.xy))
        self.destruction_button.draw(win, self.destruction_button.rect.collidepoint(mouse_pos.xy))
        floor_surf = TERMINAL_FONT_BIG.render("Changer d'étage", False, STANDARD_COLOR)
        win.blit(floor_surf, (1758-floor_surf.get_width()//2, 438))

    def handle_floor_navigation_buttons(self, event):
        """Handles the floor navigation buttons events."""
        self.up_button.handle_event(event)
        self.down_button.handle_event(event)
        self.quit_button.handle_event(event)
    
    def handle_destruction_button(self, event):
        """Handles the destruction button events."""
        if self.destruction_button.handle_event(event):
            return True
        return False

    def __repr__(self):
        """Returns a string representation of the inventory."""
        return str(self.__dict__)


class Shop(Inventory):
    def buy_object(self, obj : Placeable, game):
        if game.money - obj.price >= 0:
            game.money -= obj.price
            game.inventory.inv.append(obj)
            self.inv.remove(obj)
            self.init()
            game.popups.append(InfoPopup(f"{obj.name} a été ajouté à ton inventaire !"))
            self.sound_manager.items.play()
            game.particle_spawners[2].append(ConfettiSpawner(Coord(1,(0,0)),300))
        else:
            game.popups.append(InfoPopup("Tu n'as as assez d'argent pour acheter l'objet :("))
            self.sound_manager.incorrect.play()
            

    def handle_click(self, mouse_pos : Coord, game):
        """checks if click event happenend on an object, and launches confirmation for buying"""
        clicked_showed_obj_id = self._select_item(mouse_pos)  # Check if an inventory item was clicked, and if the object is already placed
        if clicked_showed_obj_id:
            clicked_obj = self._search_by_id(clicked_showed_obj_id)  # Retrieve the object by its ID
            game.confirmation_popups.append(ConfirmationPopup(game.win, f"Acheter cet objet pour {clicked_obj.price}¥?", self.buy_object, yes_func_args=[clicked_obj, game]))
            from core.logic import State
            game.gui_state = State.CONFIRMATION
    

    def draw(self, win, mouse_pos):
        super().draw(win, mouse_pos) # Draw the inventory using the parent method
        for plcb, _ in self.displayed_objects:
            price_label = TERMINAL_FONT.render(f"{plcb.price}¥", False, (168, 112, 62)) # Price label at the bottom of each object
            win.blit(price_label, (plcb.rect.centerx-price_label.get_width()//2, plcb.rect.y + 210))
        self.quit_button.draw(win, self.quit_button.rect.collidepoint(mouse_pos.xy))
        