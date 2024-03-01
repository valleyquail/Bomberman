# This is necessary to find the main code
import math
import random
import sys
import numpy as np
sys.path.insert(0, '../bomberman')
# Import necessary stuff
from entity import CharacterEntity
from colorama import Fore, Back
from priority_queue import PriorityQueue

class TestCharacter(CharacterEntity):
    action = "stay"
    path = None
    def do(self, wrld):
        Qs = np.load("qs.npy", allow_pickle=True).item()
        self.next_move(wrld, Qs)
        action = self.action
        # print(Qs)
        # print(self.calc_values(wrld))
        print(action)

        if action == "up left":
            self.move(-1, -1)
        elif action == "up":
            self.move(0, -1)
        elif action == "up right":
            self.move(1, -1)
        elif action == "left":
            self.move(-1, 0)
        elif action == "stay":
            self.move(0, 0)
        elif action == "right":
            self.move(1, 0)
        elif action == "down left":
            self.move(-1, 1)
        elif action == "down":
            self.move(0, 1)
        elif action == "down right":
            self.move(1, 1)
        elif action == "bomb":
            self.place_bomb()
        elif action == "path":
            self.move(self.path[1][0] - self.x, self.path[1][1] - self.y)



    def a_star(self, goal, start, wrld):

        locs = PriorityQueue()
        locs.put(start, 0)

        came_from = {}
        cost_so_far = {}
        came_from[start] = None
        cost_so_far[start] = 0

        path = []

        if not goal or not start:
            return

        while not locs.empty():
            loc = locs.get()

            x = loc[0]
            y = loc[1]

            if loc == goal:
                path.insert(0, loc)
                node = loc

                while came_from[node] is not None:
                    path.insert(0, node)
                    node = came_from[node]
                path.insert(0, start)

                return path

            if wrld.empty_at(x, y) or (x, y) == (start[0], start[1]):
                cost = cost_so_far[loc]
                adj_cells = [(x + 1, y), (x + 1, y + 1), (x + 1, y - 1), (x - 1, y), (x - 1, y + 1), (x - 1, y - 1), (x, y + 1), (x, y - 1)]

                for next in adj_cells:
                    if -1 < next[0] < wrld.width() and -1 < next[1] < wrld.height() and (wrld.empty_at(next[0], next[1]) or next == goal) and next not in came_from.values():
                        if next in cost_so_far:
                            if cost_so_far[next] > cost + self.distance(next, goal):
                                locs.put(next, cost + self.distance(next, goal))
                                came_from[next] = loc
                                cost_so_far[next] = cost + 1
                        else:
                            locs.put(next, cost + self.distance(next, goal))
                            came_from[next] = loc
                            cost_so_far[next] = cost + 1

        return

    def distance(self, p1, p2):
        return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)

    def goal(self, wrld):
        for x in range(wrld.width()):
            for y in range(wrld.height()):
                if wrld.exit_at(x, y):
                    return (x, y)

    def bomb(self, wrld):
        for x in range(wrld.width()):
            for y in range(wrld.height()):
                if wrld.bomb_at(x, y):
                    return (x, y)

    def explosions(self, wrld):
        explosions = []

        for x in range(wrld.width()):
            for y in range(wrld.height()):
                if wrld.explosion_at(x, y):
                    explosions.append((x, y))

        return explosions

    def walls(self, wrld):
        walls = []

        for x in range(wrld.width()):
            for y in range(wrld.height()):
                if wrld.wall_at(x, y):
                    walls.append((x, y))

        return walls

    def monsters(self, wrld):
        monsters = []
        for x in range(wrld.width()):
            for y in range(wrld.height()):
                if wrld.monsters_at(x, y):
                    monsters.append((x, y))

        return monsters

    def boundaries(self, wrld):
        boundaries = []
        for x in range(-1, wrld.width()+1):
            boundaries.append((x, -1))
            boundaries.append((x, wrld.height()))
        for y in range(0, wrld.height()):
            boundaries.append((-1, y))
            boundaries.append((wrld.width(), y))

        return boundaries

    def calc_values(self, wrld):
        goal = self.goal(wrld)
        path_to_goal = self.a_star(goal, (self.x, self.y), wrld)

        if path_to_goal:
            goal_dist = len(path_to_goal)
            goal_ang = math.atan2(self.y - goal[1], self.x - goal[0])
        else:
            goal_dist = 100
            goal_ang = 0


        explosion_paths = []
        for explosion in self.explosions(wrld):
            result = self.a_star((self.x, self.y), explosion, wrld)
            if result is not None:
                explosion_paths.append(result)

        explosion = None
        if explosion_paths:
            explosion_dist = len(explosion_paths[0])
            explosion = explosion_paths[0][0]
            explosion_ang = math.atan2(explosion_paths[0][0][1] - self.y, explosion_paths[0][0][0] - self.x)

            if self.y == explosion[1] and self.x == explosion[0]:
                explosion_ang = 404

            for path in explosion_paths:
                if len(path) < explosion_dist:

                    explosion_dist = len(path)
                    explosion_ang = math.atan2(path[0][1] - self.y, path[0][0] - self.x)
                    explosion = path[0]

                    if self.y == explosion[1] and self.x == explosion[0]:
                        explosion_ang = 404
        else:
            explosion_ang = None

        bomb = self.bomb(wrld)
        path_to_bomb = self.a_star((self.x, self.y), bomb, wrld)
        if path_to_bomb is not None:
            bomb_dist = len(path_to_bomb)
            bomb_ang = math.atan2(bomb[1] - self.y, bomb[0] - self.x)
            if self.y == bomb[1] and self.x == bomb[0]:
                bomb_ang = 404
        else:
            bomb_dist = 26
            bomb_ang = None

        bomb_down = 0
        bomb_to_self = (26, 26)
        if explosion:
            bomb_ang = explosion_ang

        bomb_ang = self.convertAng(bomb_ang)

        monster_paths = []
        for monster in self.monsters(wrld):
            result = self.a_star((self.x, self.y), monster, wrld)
            if result is not None:
                monster_paths.append(result)

        monster = None
        monster_to_self = None
        if monster_paths:
            monster_dist = len(monster_paths[0])
            monster_ang = math.atan2(monster_paths[0][0][1] - self.y, monster_paths[0][0][0] - self.x)
            monster = monster_paths[0][0]
            if monster_dist <= 4 and abs(monster[0] - self.x) <= 4 and abs(monster[1] - self.y) <= 4:
                monster_to_self = (max(min(monster[0] - self.x, 4), -4), max(min(monster[1] - self.y, 4), -4))

            if self.y == monster[1] and self.x == monster[0]:
                monster_ang = 404

            for path in monster_paths:
                if len(path) < monster_dist:
                    monster_dist = len(path)
                    monster_ang = math.atan2(path[0][1] - self.y, path[0][0] - self.x)
                    monster = path[0]
                    if monster_dist <= 4 and abs(monster[0] - self.x) <= 4 and abs(monster[1] - self.y) <= 4:
                        monster_to_self = (max(min(monster[0] - self.x, 4), -4), max(min(monster[1] - self.y, 4), -4))

                    if self.y == monster[1] and self.x == monster[0]:
                        monster_ang = 404
        else:
            monster_dist = 100
            monster_ang = None

        walls = self.walls(wrld)
        wall_to_self = (26, 26)
        wall_dist = 26
        wall_ang = None

        close_walls = []
        for wall in walls:
            dist = (self.x - wall[0], self.y - wall[1])
            if (dist == (1, 1) or dist == (1, 0) or dist == (1, -1) or dist == (0, 1) or
                    dist == (0, 0) or dist == (0, -1) or dist == (-1, 1) or dist == (-1, 0) or dist == (-1, -1)):
                if dist == (1,1):
                    dist = 'NW'
                elif dist == (1,0):
                    dist = 'W'
                elif dist == (1,-1):
                    dist = 'SW'
                elif dist == (0,1):
                    dist = 'N'
                elif dist == (0,0):
                    dist = 'ON TOP'
                elif dist == (0,-1):
                    dist = 'S'
                elif dist == (-1,1):
                    dist = 'NE'
                elif dist == (-1,0):
                    dist = 'E'
                elif dist == (-1,-1):
                    dist = 'SE'

                close_walls.append(dist)

        boundaries = self.boundaries(wrld)
        close_boundaries = []
        for boundary in boundaries:
            dist = (self.x - boundary[0], self.y - boundary[1])

            if (dist == (1, 1) or dist == (1, 0) or dist == (1, -1) or dist == (0, 1) or
                    dist == (0, 0) or dist == (0, -1) or dist == (-1, 1) or dist == (-1, 0) or dist == (-1, -1)):

                if dist == (1,1):
                    dist = 'NW'
                elif dist == (1,0):
                    dist = 'W'
                elif dist == (1,-1):
                    dist = 'SW'
                elif dist == (0,1):
                    dist = 'N'
                elif dist == (0,0):
                    dist = 'ON TOP'
                elif dist == (0,-1):
                    dist = 'S'
                elif dist == (-1,1):
                    dist = 'NE'
                elif dist == (-1,0):
                    dist = 'E'
                elif dist == (-1,-1):
                    dist = 'SE'
                close_boundaries.append(dist)

        close_walls.sort()
        close_boundaries.sort()

        return bomb_down, goal_dist+1, bomb_ang, tuple(close_walls), tuple(close_boundaries), monster_to_self


    def next_move(self, wrld, Qs):
        state = self.calc_values(wrld)

        goal = self.goal(wrld)
        path_to_goal = self.a_star(goal, (self.x, self.y), wrld)

        if not path_to_goal:
            n_unexplored = 0
            actions = ["down right", "down", "down left",
                       "right", "stay", "left",
                       "up right", "up", "up left", "bomb"]
            action_dict = {}
            unknown_actions = []
            for action in actions:
                if (state, action) in Qs:
                    action_dict[action] = Qs[state, action], 0
                else:
                    n_unexplored += 1
                    unknown_actions.append(action)
                    action_dict[action] = 1

            count = 0
            # if sum != 10:
            best_action = "stay"
            best_value = -100000

            eps = 0.0 + n_unexplored

            if random.random() < eps:
                print("RANDOM ACTION!", n_unexplored)
                if unknown_actions:
                    rand = random.randint(1, n_unexplored)
                    self.action = unknown_actions[rand - 1]
                else:
                    rand = random.randint(1, 10)
                    self.action = actions[rand - 1]
                return
            else:
                known_state = False
                for action in actions:
                    if (state, action) in Qs and Qs[state, action] > best_value:
                        known_state = True
                        best_action = action
                        best_value = Qs[state, action]

                if known_state:
                    self.action = best_action
                else:
                    print("RANDOM ACTION!")
                    rand = random.randint(1, 10)
                    self.action = actions[rand - 1]
                return
        else:
            self.action = "path"
            self.path = path_to_goal

    def convertAng(self, angle):
        tolerance = 0.001
        if angle is None:
            angle = None
        elif abs(angle - 0) < tolerance:
            angle = 'E'
        elif abs(angle - math.pi/2) < tolerance:
            angle = 'S'
        elif abs(angle - math.pi) < tolerance:
            angle = 'W'
        elif abs(angle + math.pi/2) < tolerance:
            angle = 'N'
        elif 0 < angle < math.pi/2:
            angle = 'SE'
        elif math.pi/2 < angle < math.pi:
            angle = 'SW'
        elif -math.pi < angle < -math.pi/2:
            angle = 'NW'
        elif -math.pi/2 < angle < 0:
            angle = 'NE'
        elif angle == 404:
            angle = "ON TOP"
        return angle

    def get_next_move(self):
        return self.action