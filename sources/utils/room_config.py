from utils.coord import Coord 
from objects.placeable import Placeable
from core.room import Room
import ui.sprite as sprite
from pygame import Surface
import objects.placeablesubclass as subplaceable

stairs_up = subplaceable.DoorUp('R1_stairs', Coord(1,(1594,546)), Surface((335,220)))
stairs_down = subplaceable.DoorDown('R1_stairs_down', Coord(1,(1594,516 + 33*6)), Surface((335,220)))

stairs_down.pair_door_up(stairs_up)
stairs_up.pair_door_down(stairs_down)
#R0
R0 = Room(0,sprite.BG2)
canva = Placeable('canva', Coord(0,(1200,50)), Surface((700,1000)))
R0.placed += [stairs_up , stairs_down]

#R1
R1 = Room(1,sprite.BG1)
test_canva = Placeable('test_canva', Coord(1,(1000,100)), Surface((48*6,64*6)), "decoration")
auto_cachier = subplaceable.AutoCachierPlaceable('AutoCachierPlaceable', Coord(1,(1500,700)), Surface((10*6, 10*6)))
inventory_plcb = subplaceable.InvPlaceable("Inventory", Coord(1, (1536, 186)), Surface((53*6, 31*6)))
R1.placed += [test_canva, stairs_up , stairs_down, auto_cachier, inventory_plcb]
R1.blacklist += [stairs_up , stairs_down, auto_cachier, inventory_plcb]


#R2
R2 = Room(2,sprite.BG3)
test_canva = Placeable('test_canva', Coord(2,(100,100)), Surface((48*6,64*6)), "decoration")
shop = subplaceable.ShopPlaceable('shop', Coord(2,(1000,100)), Surface((50*6,90*6)), "shop")
R2.placed += [stairs_up , stairs_down, test_canva, shop]
R2.blacklist += [stairs_up , stairs_down, shop]

#R3
R3 = Room(3,sprite.BG4)
R3.placed += [stairs_up , stairs_down]

R4 = Room(4, sprite.BG5)
R4.placed += [stairs_up , stairs_down]

ROOMS : list[Room] = [R0, R1, R2, R3, R4]

DEFAULT_SAVE = {'gold' : 0, 
                "inventory": [Placeable('cheater beauty', Coord(2,(100,100)), sprite.PROP_STATUE, "decoration", y_constraint=0, price=50, beauty=10000000)], 


                "shop": [Placeable('bust', Coord(2,(100,100)), sprite.PROP_STATUE, "decoration", y_constraint=0, price=50, beauty=10),
                        Placeable('plante 1', Coord(2,(100,100)), sprite.SPRITE_PLANT_1, "decoration",  y_constraint=0, price=50, beauty=100),
                        Placeable('plante 2', Coord(2,(100,100)), sprite.SPRITE_PLANT_2, "decoration",  y_constraint=0, price=50, beauty=1000)]}