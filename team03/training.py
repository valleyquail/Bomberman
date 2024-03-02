# This is necessary to find the main code
import math
import random
import sys
import numpy as np
import pygame
import colorama


sys.path.insert(0, '../bomberman')
sys.path.insert(1, '..')

# Import necessary stuff
from game import Game
from monsters.stupid_monster import StupidMonster
from monsters.selfpreserving_monster import SelfPreservingMonster

# TODO This is your code!
sys.path.insert(1, '../team03')
from testcharacter import TestCharacter

# Run!
n_steps = 1000
for step in range(n_steps):
    print(step)
    # Create the game
    g = Game.fromfile('project2/map.txt', sprite_dir="../bomberman/sprites/")

    character = TestCharacter("me" + str(step),  # name
                              "C",  # avatar
                              # random.randint(0, g.world.width() - 2), random.randint(0, g.world.height()-10)  # position
                              0, 0
                              )
    # TODO Add your character
    g.add_character(character)
    g.add_monster(SelfPreservingMonster("aggressive",  # name
                                        "A",  # avatar
                                        3, 10,  # position
                                        2  # detection range
                                        ))
    # g.add_monster(StupidMonster("stupid",  # name
    #                             "S",  # avatar
    #                             3, 9  # position
    #                             ))


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
        (g.world, g.events) = g.world.next()
        g.display_gui()
        g.draw()
        step()
        g.world.next_decisions()
    colorama.deinit()
    # g.go(1)