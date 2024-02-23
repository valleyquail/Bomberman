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
    action = "down"
    def do(self, wrld):
        Qs = np.load("qs.npy", allow_pickle=True).item()
        self.next_move(wrld, Qs)
        action = self.action
        # print(Qs, action)

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
            self.move(-1, 1)
        elif action == "bomb":
            self.place_bomb()



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


    def monsters(self, wrld):
        monsters = []
        for x in range(wrld.width()):
            for y in range(wrld.height()):
                if wrld.monsters_at(x, y):
                    monsters.append((x, y))

        return monsters

    def calc_values(self, wrld):
        goal = self.goal(wrld)
        path_to_goal = self.a_star(goal, (self.x, self.y), wrld)

        if path_to_goal:
            goal_dist = len(path_to_goal)
            goal_ang = math.atan2(self.y - goal[1], self.x - goal[0])
        else:
            goal_dist = 26
            goal_ang = 0


        monster_paths = []
        for monster in self.monsters(wrld):
            result = self.a_star((self.x, self.y), monster, wrld)
            if result is not None:
                monster_paths.append(result)

        monster = (0,0)
        if monster_paths:
            monster_dist = len(monster_paths[0])
            monster_ang = math.atan2(monster_paths[0][0][1] - self.y, monster_paths[0][0][0] - self.x)
            for path in monster_paths:
                if len(path) < monster_dist:
                    monster_dist = len(path)
                    monster_ang = math.atan2(path[0][1] - self.y, path[0][0] - self.x)
                    monster = path[0]
        else:
            monster_dist = 26
            monster_ang = 0

        explosion_paths = []
        for explosion in self.explosions(wrld):
            result = self.a_star((self.x, self.y), explosion, wrld)
            if result is not None:
                explosion_paths.append(result)

        explosion = (0,0)
        if explosion_paths:
            explosion_dist = len(explosion_paths[0])
            explosion_ang = math.atan2(explosion_paths[0][0][1] - self.y, explosion_paths[0][0][0] - self.x)
            for path in explosion_paths:
                if len(path) < explosion_dist:
                    explosion_dist = len(path)
                    explosion_ang = math.atan2(path[0][1] - self.y, path[0][0] - self.x)
                    explosion = path[0]
        else:
            explosion_dist = 26
            explosion_ang = 0


        bomb = self.bomb(wrld)
        path_to_bomb = self.a_star(bomb, (self.x, self.y), wrld)

        if path_to_bomb:
            bomb_dist = len(path_to_bomb)
            bomb_ang = math.atan2(self.y - bomb[1], self.x - bomb[0])
        else:
            bomb_dist = 26
            bomb_ang = 45

        bomb_danger = 0
        if abs(bomb_ang - 0) < 0.01 or abs(bomb_ang - math.pi/2) < 0.01 or abs(bomb_ang - math.pi) < 0.01  or abs(bomb_ang + math.pi/2) < 0.01:
            bomb_danger = 1

        return (self.x, self.y), bomb_danger


    def next_move(self, wrld, Qs):
        state = self.calc_values(wrld)
        sum = 0
        min = 10000

        actions = ["up left", "up", "up right",
                   "left", "stay", "right",
                   "down left", "down", "down right", "bomb"]
        action_dict = {}
        for action in actions:
            if (state, action) in Qs:
                sum += max(Qs[state, action], 0)
                action_dict[action] = max(Qs[state, action], 0)

            else:
                sum += 1
                action_dict[action] = 1

        count = 0
        if sum != 10 and sum > 0:
            rand = random.random() * sum
            for action in action_dict:
                if count + action_dict[action] > rand:
                    self.action = action
                    return
                count += action_dict[action]
        else:
            rand = random.randint(1, 10)
            self.action = actions[rand-1]
            return

    def get_next_move(self):
        return self.action