r"""
Projet : Creative Core
Equipe : Paul Baumard, Abel Bossard, Tybalt Debruyne, Taddeo Boisseuil-Marcil
              _            _
             | |          | |
  _   _ _ __ | | ___   ___| | __   _ __ ___   __ _ _ __   __ _  __ _  ___ _ __
 | | | | '_ \| |/ _ \ / __| |/ /  | '_ ` _ \ / _` | '_ \ / _` |/ _` |/ _ \ '__|
 | |_| | | | | | (_) | (__|   <   | | | | | | (_| | | | | (_| | (_| |  __/ |
  \__,_|_| |_|_|\___/ \___|_|\_\  |_| |_| |_|\__,_|_| |_|\__,_|\__, |\___|_|
                                                                __/ |
                                                               |___/

Key Features:
-------------
- Keeps a record of unlocked floors and features.
- Fully serializable using Pickle
- Uses confirmation popups to prompt the user before unlocking.
- Handles the constraints (costs) associated with unlocking floors and features.
- Triggers sound effects and notifications upon unlocking.
"""

from ui.confirmationpopup import ConfirmationPopup
from ui.infopopup import InfoPopup
from objects.particlesspawner import ConfettiSpawner
from utils.coord import Coord

from typing_extensions import TYPE_CHECKING

# Very ugly, but it's the only way to avoid circular imports
if TYPE_CHECKING: #  Always False when in runtime
    from core.logic import Game 

class UnlockManager:
    def __init__(self) -> None:
        """class to manage all game unlocks, it needs to be fully picklable"""
        self.unlocked_floors = ["0", "1"]
        self.unlocked_features = []
        self.discovered_features = []
        self.discovered_floors = []
        self.floor_price = {"2": 200, "3": 1000, "4": 5000, "5": 10000}
        self.feature_price = {"Auto Cachier": 5000, "Color" : 1000}

    def is_floor_unlocked(self, num: int):
        """Returns True if the floor is unlocked, False otherwise."""
        if str(num) in self.unlocked_floors:
            return True
        return False

    def is_feature_unlocked(self, feature_name):
        """Returns True if the feature is unlocked, False otherwise."""
        if feature_name in self.unlocked_features:
            return True
        return False
    
    def is_floor_discovered(self, num: int):
        """Returns True if the floor is discovered, False otherwise."""
        if str(num) in self.discovered_floors:
            return True
        return False

    def is_feature_discovered(self, feature_name):
        """Returns True if the feature is discovered, False otherwise."""
        if feature_name in self.discovered_features:
            return True
        return False

    def try_to_unlock_floor(self, num: int, game : 'Game'): #  'Game' is just for type hinting, ignored in runtime
        """Tries to unlock the floor if possible and returns the remaining money."""
        if not self.is_floor_unlocked(num):
            game.confirmation_popups.append(ConfirmationPopup(game.win, f"Débloquer pour {self.floor_price[str(num)]}¥ ?", self.unlock_floor, yes_func_args=[num, game]))
        else:
            game.popups.append(InfoPopup(f"Vous avez déjà débloqué l'étage {num} !"))

    def try_to_unlock_feature(self, name, game : 'Game'):
        """Tries to unlock the feature if possible and returns the remaining money."""
        if not self.is_feature_unlocked(name):
            game.confirmation_popups.append(ConfirmationPopup(game.win, f"Débloquer pour {self.feature_price[name]}¥ ?", self.unlock_feature, yes_func_args=[name, game]))
        else:
            game.popups.append(InfoPopup(f"Vous avez déjà débloqué {name} !"))
            game.sound_manager.incorrect.play()

    def unlock_floor(self, num: int, game : 'Game'):
        """unlocks the floor if possible and return left money"""
        assert str(num) in self.floor_price, "this should not happend"
        if not self.is_floor_unlocked(num) and game.money-self.floor_price[str(num)] >= 0:
            game.money -= self.floor_price[str(num)]
            self.unlocked_floors.append(str(num))

            game.popups.append(InfoPopup(f"Vous avez débloqué l'étage {num} !"))
            game.sound_manager.achieve.play()
            # Make it rain confetti
            game.particle_spawners[game.current_room.num].append(ConfettiSpawner(Coord(1,(0,0)),500))
            game.update_all_locked_status()
        else:
            game.popups.append(
                InfoPopup("Pas assez d'argent pour débloquer l'étage :("))
            game.sound_manager.incorrect.play()

    def unlock_feature(self, feature_name, game: 'Game'):
        """Unlocks the feature if possible and returns the remaining money."""
        assert feature_name in self.feature_price, "This should not happen"
        
        if not self.is_feature_unlocked(feature_name) and game.money - self.feature_price[feature_name] >= 0:# Check if the feature is not already unlocked and if the player has enough money
            # Deduct the cost and unlock the feature
            game.money -= self.feature_price[feature_name]
            self.unlocked_features.append(feature_name)

            # Handle specific feature unlock actions
            game.unlock_effect(feature_name)

            game.popups.append(InfoPopup(f"Vous avez débloqué {feature_name} !"))
            game.sound_manager.achieve.play()
            
            # Make it rain confetti
            game.particle_spawners[game.current_room.num].append(ConfettiSpawner(Coord(1, (0, 0)), 500))
            game.update_all_locked_status() # Update the locked status of all proper objects

            self.discovered_features.append(feature_name)
            if not game.config['gameplay']['no_story']:
                game.timer.create_timer(1, game.launch_special_dialogue, arguments=[feature_name+" Post Unlock"]) # Launch the special dialogue according to the feature unlocked
        else:
            game.popups.append(InfoPopup(f"Pas assez d'argent pour débloquer {feature_name} :("))
            game.sound_manager.incorrect.play() # Play very loud and annoying sound