Visionez les fichiers Markdown (.md) sur un support adapté pour plus de comfort (par exemple github) !    

Le projet est divisé en plusieurs modules, chacun s'occupant d'une partie spécifique du jeu. Les principaux modules comprennent :

**Les Modules de Base (Core)** : Responsables de la logique principale du jeu, de la gestion des états et des fonctionnalités de base.

**Les Modules d'Interface Utilisateur (UI)** : Gèrent les éléments de l'interface utilisateur tels que l'inventaire, les boutons et les popups.

**Les Modules d'Objets (Objects)** : Définissent les différents objets qui peuvent être placés dans le jeu et leurs comportements.

**Les Modules Utilitaires (Utils)** : Fournissent des fonctions et des classes utiles pour les coordonnées, les animations et d'autres fonctions d'aide.

Chaque module clé a ses propres responsabilités :

### Les Modules de Base incluent
- **[main.py](/sources/main.py)** (chargement de la configuration et lancement du jeu)
- **[logic.py](/sources/core/logic.py)** (boucle principale du jeu)
- **[room.py](/sources/core/room.py)** (gestion des objets dans la pièce)
- **[spectator.py](/sources/core/spectator.py)** (visualise en lecture seule une sauvegarde)
- **[unlockmanager.py](/sources/core/unlockmanager.py)** (gestion et stockage de la progression du joueur)
- **[buildmode.py](/sources/core/buildmode.py)** (gestion des modes de construction et de destruction)

### Les Modules d'Interface Utilisateur
- **[inventory.py](/sources/ui/inventory.py)** (gestion de l'inventaire)
- **[button.py](/sources/ui/button.py)** (éléments de bouton)
- **[infopopup.py](/sources/ui/infopopup.py)** (popups d'information)
- **[userlist.py](/sources/ui/userlist.py)** (affichage de la liste des utilisateurs dans le contexte du mode spectateur)
- **[sprite.py](/sources/ui/sprite.py)** (gestion des sprites et des animations)

### Les Modules d'Objets
- **[placeable.py](/sources/objects/placeable.py)** (classe de base des objets placés)
- **[placeablesubclass.py](/sources/objects/placeablesubclass.py)** (sous-classes d'objets avec des comportements spécifiques) 
- **[canva.py](/sources/objects/canva.py)** (gestion du système de peinture)
- **[patterns.py](/sources/objects/patterns.py)** (stockage et gestion des motifs)
- **[dialogue.py](/sources/objects/dialogue.py)** (gestion des dialogues)
- **[bot.py](/sources/objects/bot.py)** (gestion des bots et de leur comportement)

### Les Modules Utilitaires
- **[coord.py](/sources/utils/coord.py)** (système de coordonnées)
- **[anim.py](/sources/utils/anim.py)** (animations)
- **[sound.py](/sources/utils/sound.py)** (effets sonores)
- **[room_config.py](/sources/utils/room_config.py)** (configuration des pièces)
- **[database.py](/sources/utils/database.py)** (gestion de la base de données)
- **[timermanager.py](/sources/utils/timermanager.py)** (création et mise à jour de minuteurs)

Nous pensons architecture modulaire permet une gestion efficace du jeu, facilitant la maintenance et les extensions.

## Note sur la programmation objet

Nous avons utilisés de maniere intensive de la programmation orientée objet dans notre projet. Selon nous, cela présente plusieurs avantages. 
Voici deux exemples concrets pris dans notre code :

**Utilisation de l'héritage:**
Le fichier placeablesubclass.py montre l'utilisation de l'héritage pour créer différentes classes d'objets (BotPlaceable, ShopPlaceable, etc.) qui héritent de la classe de base Placeable. Cela permet de réutiliser le code commun tout en ajoutant des comportements spécifiques à chaque classe dérivée.

**Encapsulation et modularité:**
Le fichier anim.py illustre bien le concept de l'encapsulation où la classe Animation encapsule les détails de l'animation d'une spritesheet, rendant le code plus modulaire et facile à maintenir.

Cela nous a permi de rendre le code plus facile à naviguer et nous a donné beaucoup d'experience à travailler avec des Objets.

# Pour plus d'information sur le déroulé de la boucle principale, regardez la [timeline](/docs/timeline.md)