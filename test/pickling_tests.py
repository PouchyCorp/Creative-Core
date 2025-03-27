#Projet : Creative Core
#Equipe : Paul Baumard, Abel Bossard, Tybalt Debruyne, Taddeo Boisseuil-Marcil
import pickle
from pygame import Surface
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../sources'))) # Magic to make the imports work, taken on stackoverflow
from utils.anim import Spritesheet
from utils.anim import Animation
from objects.placeable import Placeable
from utils.coord import Coord # idk why the python language server is complaining about this import, it works fine
print('pickle test')

"""All tests should print the same dictionaries, if they don't, there is an error in the pickling process  
This test is needed because all the classes have custom pickling methods as they contain pygame objects that cannot be pickled"""

try :
    test = Spritesheet(Surface((10,10)),(1,1))
    pickled_data = pickle.dumps(test)
    unpickled_data = pickle.loads(pickled_data)
    print(test.__dict__, unpickled_data.__dict__)
except Exception as e:
    print("Exception in Spritesheet test")
    print(e)

try:
    test = Animation(Spritesheet(Surface((10,10)),(1,1)), 0, 1, 1, True)
    pickled_data = pickle.dumps(test)
    unpickled_data = pickle.loads(pickled_data)
    print(test.__dict__, unpickled_data.__dict__)
except Exception as e:
    print("Exception in Animation test)")
    print(e)

try:
    test = Placeable('test', Coord(0,(0,0)), Surface((10,10)))
    pickled_data = pickle.dumps(test)
    unpickled_data = pickle.loads(pickled_data)
    print(test.__dict__, unpickled_data.__dict__)
except Exception as e:
    print("Exception in Placeable test")
    print(e)

print('test complete, please check for errors by comparing the printed dictionaries')