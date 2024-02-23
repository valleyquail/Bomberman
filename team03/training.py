# This is necessary to find the main code
import math
import random
import sys

import numpy as np
import pygame
import colorama
np.save('qs.npy', {})

with open('weights.txt', 'r') as fd:
    w_goal_dist = int(fd.readline().split()[2])
    w_goal_ang = int(fd.readline().split()[2])
    w_monster_dist = int(fd.readline().split()[2])
    w_monster_ang = int(fd.readline().split()[2])
    w_explosion_dist = int(fd.readline().split()[2])
    w_explosion_ang = int(fd.readline().split()[2])
    w_bomb_dist = int(fd.readline().split()[2])
    w_bomb_ang = int(fd.readline().split()[2])
    w_bomb_danger = int(fd.readline().split()[2])

weights = [w_bomb_danger]

sys.path.insert(0, '../bomberman')
sys.path.insert(1, '..')

# Import necessary stuff
from events import Event
from game import Game
from monsters.stupid_monster import StupidMonster

# TODO This is your code!
sys.path.insert(1, '../team03')
from testcharacter import TestCharacter

# Run!
n_steps = 10000
gamma = 0.8
Q = {}
prevState = None
prevAction = None
alpha = 0.00001

for step in range(n_steps):
    print(step)
    # Create the game
    g = Game.fromfile('project2/map.txt', sprite_dir="../bomberman/sprites/")

    character = TestCharacter("me" + str(step),  # name
                              "C",  # avatar
                              random.randint(0, g.world.width()-1), random.randint(0, g.world.height()-1)  # position
                              )
    # TODO Add your character
    g.add_character(character)
    g.add_monster(StupidMonster("stupid",  # name
                                "S",  # avatar
                                3, 9  # position
                                ))


    """ Main game loop. """
    def step():
        # pygame.event.clear()
        # input("Press Enter to continue or CTRL-C to stop...")
        pygame.time.wait(abs(1))

    colorama.init(autoreset=True)
    g.display_gui()
    g.draw()
    step()

    while not g.done():
        prevState = character.calc_values(g.world)
        prevAction = character.action

        (g.world, g.events) = g.world.next()
        g.display_gui()
        g.draw()
        step()
        g.world.next_decisions()

        load = np.load("qs.npy", allow_pickle=True).item()
        state = character.calc_values(g.world)

        actions = ["up left", "up", "up right",
                   "left", "stay", "right",
                   "down left", "down", "down right", "bomb"]
        max_action = 0
        for action in actions:
            if not (state, action) in Q:
                Q[state, action] = 0
                for i, weight in enumerate(weights):
                    Q[state, action] += weight * state[i+1]

            if Q[state, action] > max_action:
                max_action = Q[state, action]

        r = -1
        for e in g.world.events:
            if e.tpe == Event.BOMB_HIT_CHARACTER:
                r -= 100
            elif e.tpe == Event.BOMB_HIT_WALL:
                r += 10
            elif e.tpe == Event.BOMB_HIT_MONSTER:
                r += 100
            elif e.tpe == Event.CHARACTER_KILLED_BY_MONSTER:
                r -= 1000
            elif e.tpe == Event.CHARACTER_FOUND_EXIT:
                r += 10000

        delta = r + gamma * max_action - Q[prevState, prevAction]
        Q[prevState, prevAction] += alpha*delta
        for i, weight in enumerate(weights):
            weights[i] += alpha * delta * state[i+1]

        # print(weights)

    np.save('qs.npy', Q)


    colorama.deinit()
    # g.go(1)
np.save('qs.npy', Q)