Visionez les fichiers Markdown (.md) sur un support adapté pour plus de comfort (par exemple github) !    

# Projet Creative Core
# Chronologie d'une Frame Typique de la Boucle Principale de [logic.py](/sources/core/logic.py)

Cette section décrit en détail les étapes effectuées à chaque frame de la boucle principale du jeu, le composant le plus important de tout le projet, c'est en quelque sorte le 'chef d'orquestre' du jeu.  
Ces étapes sont exécutés à une fréquence de 60 fois par seconde (60fps), ça fait beaucoup de choses !  
Bien entendu, cette section ne decrit pas le fonctionnement interne de chaque étape, mais simplement l'ordre dans lequel les differents modules et fonctions sont appelés.

## Chronologie

1. **Gestion des Événements**
    Traite les entrées de l'utilisateur pour mettre à jour l'état du jeu.

    ```python
    events = pg.event.get()
    for event in events:
        if event.type == pg.QUIT:
            pg.quit()
            return self.get_save_dict()
        self.event_handler(event, mouse_pos)
    ```

2. [**Mise à Jour**](#détails-des-étapes-de-mise-à-jour)
    Avance les minuteries, met à jour les comportements de l'IA et rafraîchit les objets en fonction de l'état actuel.  

    ```python
    if not self.paused:
        self.update(mouse_pos)
    ```

3. [**Rendu**](#détails-des-étapes-de-rendu)
    Dessine les objets, les éléments de l'interface utilisateur et les superpositions selon l'état actif.  

    ```python
    self.draw(mouse_pos)
    pg.display.flip()
    ```

## Détails des étapes de mise à jour

1. **Mise à Jour des Minuteries**
    Met à jour toutes les minuteries actives.  
    *Modules concernés :* `timermanager.py`

    ```python
    self.update_timers()
    ```

2. **Mise à Jour des Particules**
    Met à jour les spawners de particules et leurs particules associées.  
    *Modules concernés :* `particlesspawner.py`

    ```python
    self.update_particles()
    ```

3. **Mise à Jour de la Salle Actuelle**
    Met à jour les sprites et les objets placés dans la salle actuelle.  
    *Modules concernés :* `room_config.py`, `placeable.py`

    ```python
    self.update_current_room(mouse_pos)
    ```

4. **Mise à Jour des Robots**
    Met à jour les robots gérés par le Hivemind.  
    *Modules concernés :* `bot.py`

    ```python
    self.update_bots()
    ```

5. **Mise à Jour de l'État de l'Interface Utilisateur**
    Met à jour l'état de l'interface utilisateur en fonction des interactions et des confirmations.  
    *Modules concernés :* `inventory.py`, `confirmationpopup.py`

    ```python
    self.update_gui_state()
    ```

## Détails des Étapes de Rendu

1. **Rendu de l'Arrière-Plan**
    Dessine l'arrière-plan de la salle actuelle.  
    *Modules concernés :* `room_config.py`

    ```python
    self.draw_background()
    ```

2. **Rendu de la Salle Actuelle**
    Dessine les objets placés dans la salle actuelle.  
    *Modules concernés :* `room_config.py`, `placeable.py`

    ```python
    self.draw_current_room()
    ```

3. **Rendu des Robots**
    Dessine les robots dans la salle actuelle.  
    *Modules concernés :* `bot.py`

    ```python
    self.draw_bots(mouse_pos)
    ```

4. **Rendu des Motifs et du Canevas**
    Dessine les motifs et le canevas dans la salle actuelle.  
    *Modules concernés :* `patterns.py`

    ```python
    self.draw_patterns_and_canva()
    ```

5. **Rendu des Particules**
    Dessine les particules générées par les spawners de particules.  
    *Modules concernés :* `particlesspawner.py`

    ```python
    self.draw_particles()
    ```

6. **Rendu de l'Interface Utilisateur**
    Dessine les éléments de l'interface utilisateur en fonction de l'état actuel.  
    *Modules concernés :* `inventory.py`, `confirmationpopup.py`, `infopopup.py`

    ```python
    self.draw_gui(mouse_pos)
    ```

7. **Rendu des Informations de Débogage**
    Dessine les informations de débogage si le mode débogage est activé.  
    *Modules concernés :* `logic.py`

    ```python
    if self.config['gameplay']['debug']:
        self.draw_debug_info(mouse_pos)
    ```

8. **Rendu des Popups**
    Dessine les popups d'information.  
    *Modules concernés :* `infopopup.py`

    ```python
    self.render_popups()
    ```