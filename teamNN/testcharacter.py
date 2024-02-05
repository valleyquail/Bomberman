# This is necessary to find the main code
import math
import sys
sys.path.insert(0, '../bomberman')
# Import necessary stuff
from entity import CharacterEntity
from colorama import Fore, Back
from priority_queue import PriorityQueue

class TestCharacter(CharacterEntity):
    def do(self, wrld):
        # Your code here
        path = self.a_star(wrld)
        print("path:", path)

        self.move(path[0][0] - self.x, path[0][1] - self.y)

        pass

    def a_star(self, wrld):
        goal = self.goal(wrld)
        start = (self.x, self.y)

        monster_paths = []
        for monster in self.monsters(wrld):
            monster_paths.append(self.monster_a_star(monster, start, wrld))

        locs = PriorityQueue()
        locs.put(start, 0)

        came_from = {}
        monsters = {}
        cost_so_far = {}
        came_from[start] = None
        cost_so_far[start] = 0
        monsters[start] = [monster for monster in self.monsters(wrld)]

        path = []

        while not locs.empty():
            loc = locs.get()

            x = loc[0]
            y = loc[1]

            if wrld.exit_at(x, y):
                path.insert(0, loc)
                node = loc

                while came_from[node] is not None:
                    path.insert(0, node)
                    node = came_from[node]

                return path

            if wrld.empty_at(x, y) or (x, y) == (self.x, self.y):
                cost = cost_so_far[loc]
                adj_cells = [(x + 1, y), (x + 1, y + 1), (x + 1, y - 1), (x - 1, y), (x - 1, y + 1), (x - 1, y - 1), (x, y + 1), (x, y - 1)]

                for next in adj_cells:
                    if -1 < next[0] < wrld.width() and -1 < next[1] < wrld.height() and (wrld.empty_at(next[0], next[1]) or wrld.exit_at(next[0], next[1])) and next not in came_from.values():

                        if monster_paths:
                            monster_paths = []
                            for monster in monsters[loc]:
                                monster_paths.append(self.monster_a_star(monster, next, wrld))

                            nearest_monster = 0
                            for monster in monster_paths:
                                dist = self.distance(next, monster[1])
                                weight = 1000000 * 100 ** (-dist)

                                if weight > nearest_monster:
                                    nearest_monster = weight

                            new_cost = cost + nearest_monster + 1
                            if next in cost_so_far:
                                if cost_so_far[next] > cost + self.distance(next, goal):

                                    locs.put(next, new_cost + self.distance(next, goal))
                                    came_from[next] = loc
                                    cost_so_far[next] = new_cost
                                    monsters[next] = [path[0] for path in monster_paths]
                            else:
                                locs.put(next, cost + nearest_monster + self.distance(next, goal))
                                came_from[next] = loc
                                cost_so_far[next] = cost + nearest_monster + 1
                                monsters[next] = [path[0] for path in monster_paths]

                        else:
                            if next in cost_so_far:
                                if cost_so_far[next] > cost + self.distance(next, goal):
                                    locs.put(next, cost + self.distance(next, goal))
                                    came_from[next] = loc
                                    cost_so_far[next] = cost + self.distance(next, loc)
                            else:
                                locs.put(next, cost + self.distance(next, goal))
                                came_from[next] = loc
                                cost_so_far[next] = cost + self.distance(next, loc)

        return path

    def monster_a_star(self, monster, player, wrld):
        goal = player
        start = monster

        locs = PriorityQueue()
        locs.put(start, 0)

        came_from = {}
        cost_so_far = {}
        came_from[start] = None
        cost_so_far[start] = 0

        path = []

        while not locs.empty():
            loc = locs.get()
            # print(loc)

            x = loc[0]
            y = loc[1]

            if loc == goal:
                path.insert(0, loc)
                node = loc

                while came_from[node] is not None:
                    path.insert(0, node)
                    node = came_from[node]
                path.insert(0, node)

                return path

            if wrld.empty_at(x, y) or (x, y) == (monster[0], monster[1]):
                cost = cost_so_far[loc]
                adj_cells = [(x + 1, y), (x + 1, y + 1), (x + 1, y - 1), (x - 1, y), (x - 1, y + 1), (x - 1, y - 1), (x, y + 1), (x, y - 1)]

                for next in adj_cells:

                    if -1 < next[0] < wrld.width() and -1 < next[1] < wrld.height() and (wrld.empty_at(next[0], next[1]) or next == goal) and next not in came_from:
                        locs.put(next, cost + self.distance(next, goal))
                        came_from[next] = loc
                        cost_so_far[next] = cost + self.distance(loc, next)

        return path

    def distance(self, p1, p2):
        return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)

    def goal(self, wrld):
        for x in range(wrld.width()):
            for y in range(wrld.height()):
                if wrld.exit_at(x, y):
                    return (x, y)

    def monsters(self, wrld):
        monsters = []
        for x in range(wrld.width()):
            for y in range(wrld.height()):
                if wrld.monsters_at(x, y):
                    monsters.append((x, y))

        return monsters