import tcod as libtcod

from random import randint

from game_messages import Message


class BasicMonster:
    def take_turn(self, target, fov_map, game_map, entities):
        results = []

        monster = self.owner
        if monster.z == target.z:

            if monster.distance_to(target) >= 2:
                monster.move_astar(target, entities, game_map, fov_map)

            elif target.fighter.hp > 0 and monster.z == target.z:
                monster.push(target, entities, fov_map, game_map)
                
        else:
            (rx, ry) = (0, 0)
            while (rx, ry) == (0, 0):
                #pick -1 or 1
                coin = randint(0,1)
                if coin == 0:
                    rx = randint(-1, 1)
                    ry = randint(-1, 1)
                else:
                    ry = randint(-1, 1)
                    rx = randint(-1, 1)
                    
                if (rx, ry) == (target.x, target.y): (rx, ry) = (0, 0)
                    
            monster.move(rx, ry, fov_map)   
               
        return results


class ConfusedMonster:
    def __init__(self, previous_ai, number_of_turns=10):
        self.previous_ai = previous_ai
        self.number_of_turns = number_of_turns

    def take_turn(self, target, fov_map, game_map, entities):
        results = []

        if self.number_of_turns > 0:
            random_x = self.owner.x + randint(0, 2) - 1
            random_y = self.owner.y + randint(0, 2) - 1

            if random_x != self.owner.x and random_y != self.owner.y:
                self.owner.move_towards(random_x, random_y, game_map, entities, fov_map)

            self.number_of_turns -= 1
        else:
            self.owner.ai = self.previous_ai
            results.append({'message': Message('The {0} is no longer confused!'.format(self.owner.name), libtcod.red)})

        return results
