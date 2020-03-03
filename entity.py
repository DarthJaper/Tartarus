import tcod as libtcod

import math

from render_functions import RenderOrder, clear_entity, draw_entity
from menus import death
from input_handlers import handle_keys, handle_mouse, handle_main_menu

import time

class Entity:
    """
    A generic object to represent players, enemies, items, etc.
    """
    def __init__(self, x, y, z, char, color, name, blocks=False, render_order=RenderOrder.CORPSE, strength=2, fighter=None, ai=None,
                 item=None, inventory=None):
        self.x = x
        self.y = y
        self.z = z
        self.char = char
        self.color = color
        self.name = name
        self.blocks = blocks
        self.render_order = render_order
        self.strength = strength
        self.fighter = fighter
        self.ai = ai
        self.item = item
        self.inventory = inventory
        
        if self.name == "Player":
            self.depth = 10
            self.killcounts = {}
            self.score = 0
            self.multiplier = 1
            

        if self.fighter:
            self.fighter.owner = self

        if self.ai:
            self.ai.owner = self

        if self.item:
            self.item.owner = self

        if self.inventory:
            self.inventory.owner = self

    def move(self, dx, dy, fov_map):
        clear_entity(0, self)
        # Move the entity by a given amount
        self.x += dx
        self.y += dy
        draw_entity(0, self, fov_map)
        
    def move_towards(self, target_x, target_y, game_map, entities, fov_map):
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        dx = int(round(dx / distance))
        dy = int(round(dy / distance))

        if not (game_map.is_blocked(self.x + dx, self.y + dy) or
                    get_blocking_entities_at_location(entities, self.x + dx, self.y + dy)):
            self.move(dx, dy, fov_map)

    def push(self, target, entities, fov_map, game_map):
        #push a target. can get direction from self.x,y and target.x,y1
        
        player = None
        
        for e in entities:
            if e.name == "Player":
                player = e
                break
        
        dirx = target.x - self.x
        diry = target.y - self.y     
        
        for entity in entities:
            if self.x - dirx == entity.x and self.y - diry == entity.y:
                clear_entity(0, entity)
                entity.x -= dirx
                entity.y -= diry
                draw_entity(0, entity, fov_map)
                break

        clear_entity(0, self)
        self.x -= dirx
        self.y -= diry
        draw_entity(0, self, fov_map)
        
        throw_range = 15
        if target.name == "Player":
            throw_range = self.strength
        
        for c in range(throw_range+1):
            targets_target = get_blocking_entities_at_location(entities, target.x + dirx, target.y + diry)
        
            if targets_target:
                player.multiplier += 1
                print("c-c-c-combooooo!")
                target.push(targets_target, entities, fov_map, game_map)
                
                break
            else:
                player.multiplier = 1
                
                tx = target.x + dirx
                ty = target.y + diry
                isded = False
            
                if game_map.tiles[tx][ty].blocked:
                    if target.name == "Player":
                        print('oof. player dies.')
                        death(target)
                        break
                    else:
                        if self.name == "Player":
                            count = self.killcounts.get(target.name)
                            if count:
                                self.killcounts[target.name] += 1
                                print(str(target.name) + " x" + str(self.killcounts[target.name]))
                            else:
                                self.killcounts[target.name] = 1
                                
                        #do a dies
                        player.score += (10 * player.multiplier)                        
                        entities.remove(target)
                        break
                    
                else:
                    #rudimentary animation of entity being pushed
                    clear_entity(0, target)
                    target.x += dirx
                    target.y += diry
                    draw_entity(0, target, fov_map)
                    time.sleep(.015)
                    libtcod.console_flush()

            
        

    def distance(self, x, y):
        return math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)

    def distance_to(self, other):
        dx = other.x - self.x
        dy = other.y - self.y
        return math.sqrt(dx ** 2 + dy ** 2)

    def move_astar(self, target, entities, game_map, fov_map):
        # Create a FOV map that has the dimensions of the map
        fov = libtcod.map_new(game_map.width, game_map.height)

        # Scan the current map each turn and set all the walls as unwalkable
        for y1 in range(game_map.height):
            for x1 in range(game_map.width):
                libtcod.map_set_properties(fov, x1, y1, not game_map.tiles[x1][y1].block_sight,
                                           not game_map.tiles[x1][y1].blocked)

        # Scan all the objects to see if there are objects that must be navigated around
        # Check also that the object isn't self or the target (so that the start and the end points are free)
        # The AI class handles the situation if self is next to the target so it will not use this A* function anyway
        for entity in entities:
            if entity.blocks and entity != self and entity != target:
                # Set the tile as a wall so it must be navigated around
                libtcod.map_set_properties(fov, entity.x, entity.y, True, False)

        # Allocate a A* path
        # The 1.41 is the normal diagonal cost of moving, it can be set as 0.0 if diagonal moves are prohibited
        my_path = libtcod.path_new_using_map(fov, 1.41)

        # Compute the path between self's coordinates and the target's coordinates
        libtcod.path_compute(my_path, self.x, self.y, target.x, target.y)

        # Check if the path exists, and in this case, also the path is shorter than 25 tiles
        # The path size matters if you want the monster to use alternative longer paths (for example through other rooms) if for example the player is in a corridor
        # It makes sense to keep path size relatively low to keep the monsters from running around the map if there's an alternative path really far away
        if not libtcod.path_is_empty(my_path) and libtcod.path_size(my_path) < 25:
            # Find the next coordinates in the computed full path
            x, y = libtcod.path_walk(my_path, True)
            if x or y:
                # Set self's coordinates to the next path tile
                self.x = x
                self.y = y
        else:
            # Keep the old move function as a backup so that if there are no paths (for example another monster blocks a corridor)
            # it will still try to move towards the player (closer to the corridor opening)
            self.move_towards(target.x, target.y, game_map, entities, fov_map)

            # Delete the path to free memory
        libtcod.path_delete(my_path)


def get_blocking_entities_at_location(entities, destination_x, destination_y):
    for entity in entities:
        if entity.blocks and entity.x == destination_x and entity.y == destination_y:
            return entity

    return None
