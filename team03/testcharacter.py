# This is necessary to find the main code
import math
import random
import sys
import numpy as np
sys.path.insert(0, '../bomberman')
from events import Event
# Import necessary stuff
from entity import CharacterEntity
from colorama import Fore, Back
from priority_queue import PriorityQueue

class TestCharacter(CharacterEntity):
    action = "stay"
    path = None
    alpha = 0.001
    gamma = 0.8

    with open('weights.txt', 'r') as fd:
        w_path_to_goal = float(fd.readline().split()[2])
        w_goal_dist = float(fd.readline().split()[2])
        w_bomb_dist = float(fd.readline().split()[2])
        w_monster_dist = float(fd.readline().split()[2])

    weights = [w_path_to_goal, w_goal_dist, w_bomb_dist, w_monster_dist]

    def do(self, wrld):
        self.next_move(wrld)
        action = self.action

        print(action, self.weights)

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
        try:
            new_bomberman = next(iter(wrld.characters.values()))
            new_bomberman = new_bomberman[0]
        except:
            return 0, 0.001, 1, 1

        goal = self.goal(wrld)
        goal_dist = max(goal[0] - new_bomberman.x, goal[1] - new_bomberman.y)

        path_to_goal = self.a_star(goal, (new_bomberman.x, new_bomberman.y), wrld)

        if path_to_goal:
            path_to_goal = 1
        else:
            path_to_goal = 0

        explosion_paths = []
        for explosion in self.explosions(wrld):
            result = self.a_star((new_bomberman.x, new_bomberman.y), explosion, wrld)
            if result is not None:
                explosion_paths.append(result)
        explosion_dist = 100
        if explosion_paths:
            explosion_dist = len(explosion_paths[0])
            for path in explosion_paths:
                if len(path) < explosion_dist:
                    explosion_dist = len(path)


        bomb = self.bomb(wrld)
        bomb_dist = 100
        path_to_bomb = self.a_star((new_bomberman.x, new_bomberman.y), bomb, wrld)
        if path_to_bomb is not None:
            bomb_dist = max(abs(bomb[0] - new_bomberman.x), abs(bomb[1] - new_bomberman.y))
            if bomb[0] == new_bomberman.x or bomb[1] == new_bomberman.y:
                bomb_dist = 0.1

        if explosion_paths:
            bomb_dist = explosion_dist


        monster_paths = []
        for monster in self.monsters(wrld):
            result = self.a_star((new_bomberman.x, new_bomberman.y), monster, wrld)
            if result is not None:
                monster_paths.append(result)

        if monster_paths:
            monster_dist = len(monster_paths[0])
            for path in monster_paths:
                if len(path) < monster_dist:
                    monster_dist = len(path)
        else:
            monster_dist = 100

        return path_to_goal, 1/(goal_dist+1), 1/(bomb_dist+1), 1/math.sqrt(monster_dist)


    def next_move(self, wrld):
        goal = self.goal(wrld)
        path_to_goal = self.a_star(goal, (self.x, self.y), wrld)

        if not path_to_goal:
            s_current = self.calc_values(wrld)
            q_current = self.calc_q(s_current)
            print(s_current, q_current)

            if s_current[2] == 1/101:
                self.place_bomb()

            actions = ["down right", "down", "down left",
                       "right", "stay", "left",
                       "up right", "up", "up left"]
            biggest_q = -10000
            best_action = 'stay'
            best_events = []

            for action in actions:
                new_bomberman = next(iter(wrld.characters.values()))
                new_bomberman = new_bomberman[0]

                if action == "up left":
                    new_bomberman.move(-1, -1)
                elif action == "up":
                    new_bomberman.move(0, -1)
                elif action == "up right":
                    new_bomberman.move(1, -1)
                elif action == "left":
                    new_bomberman.move(-1, 0)
                elif action == "stay":
                    new_bomberman.move(0, 0)
                elif action == "right":
                    new_bomberman.move(1, 0)
                elif action == "down left":
                    new_bomberman.move(-1, 1)
                elif action == "down":
                    new_bomberman.move(0, 1)
                elif action == "down right":
                    new_bomberman.move(1, 1)
                elif action == "bomb":
                    new_bomberman.place_bomb()

                next_wrld, events = wrld.next()

                next_state = self.calc_values(next_wrld)
                next_q = self.calc_q(next_state)

                reward = self.reward(best_events, action)

                delta = reward + self.gamma * next_q - q_current
                for i, weight in enumerate(self.weights):
                    self.weights[i] += self.alpha * delta * s_current[i]

                next_q = self.calc_q(next_state)

                if next_q > biggest_q:
                    biggest_q = next_q
                    best_action = action
                    best_events = events

            self.action = best_action
            # self.save_weights()

        else:
            self.action = "path"
            self.path = path_to_goal

    def calc_q(self, state):
        q = 0
        for i, weight in enumerate(self.weights):
            q += weight * state[i]
        return q

    def reward(self, events, action):
        r = -0.01
        for e in events:
            if e.tpe == Event.BOMB_HIT_CHARACTER:
                r -= 1
            elif e.tpe == Event.BOMB_HIT_WALL:
                r += 0.1
            elif e.tpe == Event.BOMB_HIT_MONSTER:
                r += 0.5
            elif e.tpe == Event.CHARACTER_KILLED_BY_MONSTER:
                r -= 1
            elif e.tpe == Event.CHARACTER_FOUND_EXIT:
                r += 1
        if action == "down left" or action == "down right" or action == "down":
            r+= 0.05
        return r

    def save_weights(self):
        f = open("weights.txt", 'w')
        f.write("w_path = " + str(self.weights[0]) + " \n")
        f.write("w_goal_dist = " + str(self.weights[1]) + "\n")
        f.write("w_bomb_dist = " + str(self.weights[2]) + "\n")
        f.write("w_monster_dist = " + str(self.weights[3]) + "\n")