# This is necessary to find the main code
import math
import random
import sys

import numpy as np
import pygame
import colorama
# np.save('qs.npy', {})

with open('weights.txt', 'r') as fd:
    w_bomb_down = int(fd.readline().split()[2])
    w_goal_dist = int(fd.readline().split()[2])
    w_bomb_ang = int(fd.readline().split()[2])
    w_close_walls = float(fd.readline().split()[2])
    w_close_boundaries = float(fd.readline().split()[2])
    w_monster_ang = float(fd.readline().split()[2])
    w_down_weight = float(fd.readline().split()[2])

weights = [w_bomb_down, w_goal_dist, w_bomb_ang, w_close_walls, w_close_boundaries, w_monster_ang, w_down_weight]

sys.path.insert(0, '../bomberman')
sys.path.insert(1, '..')

# Import necessary stuff
from events import Event
from game import Game
from monsters.stupid_monster import StupidMonster
from monsters.selfpreserving_monster import SelfPreservingMonster

# TODO This is your code!
sys.path.insert(1, '../team03')
from testcharacter import TestCharacter

# Run!
n_steps = 10000
gamma = 0.9
# Q = {}
Q = np.load("qs.npy", allow_pickle=True).item()
max_Q = 1
prevState = None
prevAction = None
alpha = 0.1

def calc_f_states():
    if prevState[5] is None:
        if prevState[1] == 101:
            if prevAction == 'bomb' and prevState[0] == 1:
                f_states[0] = -1
            elif prevAction == 'bomb' and prevState[0] == 0:
                f_states[0] = 1
            else:
                f_states[0] = prevState[0]
        else:
            if prevAction == 'bomb':
                f_states[0] = -1
            else:
                f_states[0] = 0
    else:
        if prevAction == 'bomb' and 'S' not in prevState[3]:
            f_states[0] = -1
    if prevState[0] == 0 and prevAction == 'stay':
        f_states[0] = -1

    if prevState[1] != 101:
        if prevAction == 'up':
            f_states[1] = 1 / (prevState[1] + 1)
        elif prevAction == 'up left':
            f_states[1] = 1 / (prevState[1] + 1)
        elif prevAction == 'up right':
            f_states[1] = 1 / (prevState[1] + 1)
        elif prevAction == 'down':
            f_states[1] = 1 / (prevState[1] - 1)
        elif prevAction == 'down right':
            f_states[1] = 1 / (prevState[1] - 1)
        elif prevAction == 'down left':
            f_states[1] = 1 / prevState[1]
        elif prevAction == 'left':
            f_states[1] = 1 / (prevState[1] + 1)
        elif prevAction == 'right':
            f_states[1] = 1 / prevState[1]
        else:
            f_states[1] = 1 / prevState[1]
    else:
        f_states[1] = 0

    if prevAction == 'up' and (prevState[2] == 'N' or prevState[2] == 'NW' or prevState[2] == 'NE'):
        f_states[2] = -1
    elif prevAction == 'up left' and (
            prevState[2] == 'N' or prevState[2] == 'NW' or prevState[2] == 'NE' or prevState[2] == 'SW' or prevState[
        2] == 'W'):
        f_states[2] = -1
    elif prevAction == 'up right' and (
            prevState[2] == 'N' or prevState[2] == 'NW' or prevState[2] == 'NE' or prevState[2] == 'SE' or prevState[
        2] == 'E'):
        f_states[2] = -1
    elif prevAction == 'down' and (prevState[2] == 'S' or prevState[2] == 'SW' or prevState[2] == 'SE'):
        f_states[2] = -1
    elif prevAction == 'down right' and (
            prevState[2] == 'S' or prevState[2] == 'SW' or prevState[2] == 'SE' or prevState[2] == 'NE' or prevState[
        2] == 'E'):
        f_states[2] = -1
    elif prevAction == 'down left' and (
            prevState[2] == 'S' or prevState[2] == 'SW' or prevState[2] == 'SE' or prevState[2] == 'NW' or prevState[
        2] == 'W'):
        f_states[2] = -1
    elif prevAction == 'left' and (prevState[2] == 'W' or prevState[2] == 'NW' or prevState[2] == 'SW'):
        f_states[2] = -1
    elif prevAction == 'right' and (prevState[2] == 'E' or prevState[2] == 'NE' or prevState[2] == 'SE'):
        f_states[2] = -1
    elif (
            prevAction == "up" or prevAction == "down" or prevAction == "left" or prevAction == "right" or prevAction == "stay" or prevAction == "bomb") and \
            prevState[2] == "ON TOP":
        f_states[2] = -1
    elif (prevAction == "stay" or prevAction == "bomb") and prevState[2] == "E" or prevState[2] == "W" or prevState[
        2] == "S" or prevState[2] == "N":
        f_states[2] = -1
    # elif prevState[2] != "E" and prevState[2] != "W" and  prevState[2] != "S" and prevState[2] != "N" and prevState[2] != "ON TOP" and prevAction == 'stay':
    #     f_states[2] = 1
    else:
        f_states[2] = 0

    if prevState[5] is not None:
        f_states[5] = - 1 / (min(abs(prevState[5][0]), abs(prevState[5][1])) + 1)

    if prevState[0] == 1 or prevState[5] is not None:
        if prevAction == 'up' and "N" in prevState[3]:
            f_states[3] = -1
        elif prevAction == 'up left' and "NW" in prevState[3]:
            f_states[3] = -1
        elif prevAction == 'up right' and "NE" in prevState[3]:
            f_states[3] = -1
        elif prevAction == 'down' and "S" in prevState[3]:
            f_states[3] = -1
        elif prevAction == 'down right' and "SE" in prevState[3]:
            f_states[3] = -1
        elif prevAction == 'down left' and "SW" in prevState[3]:
            f_states[3] = -1
        elif prevAction == 'left' and "W" in prevState[3]:
            f_states[3] = -1
        elif prevAction == 'right' and "E" in prevState[3]:
            f_states[3] = -1
        else:
            f_states[3] = 0

        if prevAction == 'up' and "N" in prevState[4]:
            f_states[4] = -1
        elif prevAction == 'up left' and "NW" in prevState[4]:
            f_states[4] = -1
        elif prevAction == 'up right' and "NE" in prevState[4]:
            f_states[4] = -1
        elif prevAction == 'down' and "S" in prevState[4]:
            f_states[4] = -1
        elif prevAction == 'down right' and "SE" in prevState[4]:
            f_states[4] = -1
        elif prevAction == 'down left' and "SW" in prevState[4]:
            f_states[4] = -1
        elif prevAction == 'left' and "W" in prevState[4]:
            f_states[4] = -1
        elif prevAction == 'right' and "E" in prevState[4]:
            f_states[4] = -1
        else:
            f_states[4] = 0
    else:
        if prevAction == 'up' and "N" in prevState[3]:
            f_states[3] = -0.01
        elif prevAction == 'up left' and "NW" in prevState[3]:
            f_states[3] = -0.01
        elif prevAction == 'up right' and "NE" in prevState[3]:
            f_states[3] = -0.01
        elif prevAction == 'down' and "S" in prevState[3]:
            f_states[3] = -0.01
        elif prevAction == 'down right' and "SE" in prevState[3]:
            f_states[3] = -0.01
        elif prevAction == 'down left' and "SW" in prevState[3]:
            f_states[3] = -0.01
        elif prevAction == 'left' and "W" in prevState[3]:
            f_states[3] = -0.01
        elif prevAction == 'right' and "E" in prevState[3]:
            f_states[3] = -0.01
        else:
            f_states[3] = 0

        if prevAction == 'up' and "N" in prevState[4]:
            f_states[4] = -0.01
        elif prevAction == 'up left' and "NW" in prevState[4]:
            f_states[4] = -0.01
        elif prevAction == 'up right' and "NE" in prevState[4]:
            f_states[4] = -0.01
        elif prevAction == 'down' and "S" in prevState[4]:
            f_states[4] = -0.01
        elif prevAction == 'down right' and "SE" in prevState[4]:
            f_states[4] = -0.01
        elif prevAction == 'down left' and "SW" in prevState[4]:
            f_states[4] = -0.01
        elif prevAction == 'left' and "W" in prevState[4]:
            f_states[4] = -0.01
        elif prevAction == 'right' and "E" in prevState[4]:
            f_states[4] = -0.01
        else:
            f_states[4] = 0

        if prevState[1] == 101 and prevState[0] != 1:
            if ('E' in prevState[3] or 'N' in prevState[3] or 'W' in prevState[3]) and prevAction == 'bomb':
                f_states[6] = 0.01
            elif 'S' in prevState[3] and prevAction == 'bomb':
                f_states[6] = 0.1
            elif 'S' not in prevState[3] and 'S' not in prevState[4] and prevAction == 'down':
                f_states[6] = 0.01

for step in range(n_steps):
    print(step)
    # Create the game
    g = Game.fromfile('project2/map.txt', sprite_dir="../bomberman/sprites/")

    print(step, g.world.width(), g.world.height())
    character = TestCharacter("me" + str(step),  # name
                              "C",  # avatar
                              random.randint(0, g.world.width() - 2), random.randint(g.world.height() - 15, g.world.height() - 10)  # position
                              # 0, 0
                              )
    # TODO Add your character
    g.add_character(character)
    # g.add_monster(SelfPreservingMonster("aggressive",  # name
    #                                     "A",  # avatar
    #                                     3, 10,  # position
    #                                     2  # detection range
    #                                     ))
    g.add_monster(StupidMonster("stupid",  # name
                                "S",  # avatar
                                3, 9  # position
                                ))


    """ Main game loop. """
    def step():
        # pygame.event.clear()
        # input("Press Enter to continue or CTRL-C to stop...")
        pygame.time.wait(abs(0))

    colorama.init(autoreset=True)
    g.display_gui()
    g.draw()
    step()

    while not g.done():
        load = np.load("qs.npy", allow_pickle=True).item()

        # print(Q)
        prevState = character.calc_values(g.world)
        prevAction = character.action

        f_states = [prevState[0], 1/prevState[1], prevState[2], 0, 0, 0, 0]
        calc_f_states()

        Q[prevState, prevAction] = 0
        for i, weight in enumerate(weights):
            Q[prevState, prevAction] += weight * f_states[i]

        # if abs(Q[prevState, prevAction]) > max_Q:
        #     max_Q = abs(Q[prevState, prevAction])
        #     for staction in Q:
        #         Q[staction] /= max_Q
        # else:
        #     Q[prevState, prevAction] /= max_Q

        (g.world, g.events) = g.world.next()
        g.display_gui()
        g.draw()
        step()
        g.world.next_decisions()
        # print(state)

        state = character.calc_values(g.world)
        actions = ["down right", "down", "down left",
                   "right", "stay", "left",
                   "up right", "up", "up left", "bomb"]

        max_action = 0
        best_action = "stay"
        for action in actions:
            if (state, action) in Q:
                if Q[state, action] > max_action:
                    max_action = Q[state, action]
                    best_action = action

        r = -0.001
        for e in g.world.events:
            if e.tpe == Event.BOMB_HIT_CHARACTER:
                r -= 1
            elif e.tpe == Event.BOMB_HIT_WALL:
                r += 0.1
            # elif e.tpe == Event.BOMB_HIT_MONSTER:
            #     r += 0.5
            elif e.tpe == Event.CHARACTER_KILLED_BY_MONSTER:
                r -= 1
            elif e.tpe == Event.CHARACTER_FOUND_EXIT:
                r += 1

        delta = max(min(r + gamma * max_action - Q[prevState, prevAction], 1), -1)
        # print(delta, r, max_action, Q[prevState, prevAction])

        # Q[prevState, prevAction] += alpha*delta
        for i, weight in enumerate(weights):
            weights[i] += alpha * delta * np.linalg.norm(f_states[i])

        print(delta)
        print(weights)
        print("Current:", Q[prevState, prevAction], prevState, prevAction)
        if (state, best_action) in Q:
            print("Next:", Q[state, best_action], state, best_action)

        np.save('qs.npy', Q)
    np.save('qs.npy', Q)


    colorama.deinit()
    # g.go(1)
np.save('qs.npy', Q)