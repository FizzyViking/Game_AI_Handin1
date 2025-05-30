from vector import Vector2
from entity import *
from nodes import *

# Behavior Tree class to control pacman

# Code from exercise 5
class Task:
    def run(self):
        return NotImplementedError

class Selector(Task):
    def __init__(self, children : list[Task]):
        self.children = children        
   
    def run(self):
      
        for c in self.children: 
            if c.run():
                print(str(c) + ":" + str(True))
                return True
            print(str(c) + ":" + str(False))
        return False
        
class Sequence(Task):
    def __init__(self, children : list[Task]):
        self.children = children
    
    def run(self):
        for c in self.children:
            if not c.run():
                print(str(c) + ":" + str(False))
                return False
            print(str(c) + ":" + str(True))
        return True

# Tasks to determine where the ghosts are and what turn to take in order to avoid them
class IsGhostClose(Task):
    def __init__(self, pacman: Entity, ghosts: list[Entity], distance: float):
        self.pacman = pacman
        self.ghosts = ghosts
        self.distance = distance

    def run(self):
        for ghost in self.ghosts:
            if self.pacman.position.distance_to(ghost.position) < self.distance:
                return True
        return False

class GhostToTheLeft(Task):
    def __init__(self, pacman: Entity, ghosts: list[Entity]):
        self.pacman = pacman
        self.ghosts = ghosts

    def run(self):
        for ghost in self.ghosts:
            if ghost.position.x < self.pacman.position.x and ghost.position.y == self.pacman.position.y:
                self.pacman.direction = RIGHT
                return True
        return False

class GhostToTheRight(Task):
    def __init__(self, pacman: Entity, ghosts: list[Entity]):
        self.pacman = pacman
        self.ghosts = ghosts

    def run(self):
        for ghost in self.ghosts:
            if ghost.position.x > self.pacman.position.x and ghost.position.y == self.pacman.position.y:
                self.pacman.direction = LEFT
                return True
        return False