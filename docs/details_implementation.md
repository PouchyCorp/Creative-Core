Visionez les fichiers Markdown (.md) sur un support adapté pour plus de comfort (par exemple github) !  

## Fonctionnement de la base de donnée 

**Echanges effectués quand `send_query()` est appelé sur le client**
```
Client                          Serveur de Base de Données
  |                                           |
  | ------ Connecte via socket -------------> |
  |                                           |
  | --- Envoie longueur des données --------> |
  |                                           |
  | - Envoie données sérialisées par paquet ->|
  |                                           |
  | <------- Envoie statut d'erreur --------- |
  |                                           |
  | <----- Envoie longueur de la réponse ---- |
  |                                           |
  | <--- Envoie réponse par paquet ------     |
  |                                           |
  | -- Le client désérialise les données ---- |
  |                                           |
```
La version basique du client utilisée pour la conception et les testes peut être trouvée sur [test_client.py](tests/test_client.py)


## Fonctionnement de `TimerManager`

La classe `TimerManager` permet de créer et de gérer des minuteries qui exécutent des fonctions après un certain délai.  
Ce composant est critique pour notre projet, il est utilisé plus de 20 fois dans le code !

- **`create_timer`** : Crée une nouvelle minuterie avec une durée spécifiée, une fonction à exécuter, et des arguments optionnels. La minuterie peut être répétée si nécessaire.
- **`update`** : Met à jour les minuteries en vérifiant si leur durée est écoulée. Si c'est le cas, la fonction associée est exécutée et la minuterie est soit supprimée, soit réinitialisée si elle est répétée.

### Exemple typique d'usage

Supposons que nous voulons créer une minuterie qui affiche un message après 2 secondes. Voici comment nous pourrions utiliser `TimerManager` :

```python
from utils.timermanager import TimerManager

# Initialisation du gestionnaire de minuteries
timer_manager = TimerManager()

# Fonction à exécuter après 2 secondes
def afficher_message():
    print("2 secondes se sont écoulées!")

# Création de la minuterie
timer_manager.create_timer(2.0, afficher_message)

# Boucle principale du programme
while True:
    # Mise à jour du timer
    timer_manager.update()
```

### Cheminement pour l'implémentation

1. **Définition des besoins** : Nous avons identifié le besoin de gérer des minuteries pour exécuter des fonctions après un certain délai, sans utiliser `sleep`, puisque nous devons continuer à executer la boucle principale.
2. **Conception de la classe `TimerManager`** : Nous avons approché le probleme d'une maniere à rendre le minuteur le plus facile d'utilisation possible:
- Grâce à la POO, il est facile de passer en paramètre une méthode d’instance d’une classe. Cette méthode, conçue pour ne pas prendre de paramètres, peut alors utiliser directement les attributs de l’instance pour fonctionner.
Cela garantit que les valeurs utilisées sont toujours "à jour". Si les paramètres (comme la position ou la couleur) étaient fixés lors de l’initialisation d’un minuteur, rien n’assurerait qu’ils seraient encore valides au moment de l’exécution de la fonction une minute plus tard.

- L’avantage de `create_timer()`, c’est qu’il simplifie l’utilisation du minuteur, sans nécessiter d’action supplémentaire de l’utilisateur. Son inconvénient est qu’il ne peut être appelé que sur une seule instance de la classe TimerManager, ce qui oblige à passer cette instance en paramètre à toute fonction souhaitant créer un minuteur. 
3. **Test et validation** : Nous avons testé la classe avec différents scénarios pour nous assurer qu'elle fonctionne correctement, nous avons par exemple trouvé un bug qui ne supprimait pas correctement les minuteurs écoulés quand la durée était très courte.
