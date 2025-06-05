from random import choice
from entity import *
from nodes import *
from pellets import PelletGroup

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
                return True
        return False
        
class Sequence(Task):
    def __init__(self, children : list[Task]):
        self.children = children
    
    def run(self):
        for c in self.children:
            if not c.run():
                return False
        return True

# Task to determine whether a ghost is close to pacman or not
class IsGhostClose(Task):
    def __init__(self, pacman: Entity, ghosts: list[Entity], distance: float):
        # References to pacman and the ghosts
        self.pacman = pacman
        self.ghosts = ghosts
        self.distance = distance # Distance to determine whether pacman is too close to a ghost

    def run(self):
        for ghost in self.ghosts:
            # For every ghost we check whether it is in scatter or chase mode, as these pose the most danger to pacman
            # We then calculate the magnitude distance between pacman and the ghost(s) and check whether it is close enough to 
            # set pacman to flee from the ghosts
            # If just one ghost fufills these requirements, we return true, so pacman can flee from the ghost(s)
            if (ghost.mode.current in [SCATTER, CHASE]) and (ghost.position - self.pacman.position).magnitude() < self.distance:
                return True
        return False

# Action task that set pacman to flee from the nearby ghosts
class FleeFromGhosts(Task):
    def __init__(self, pacman: Entity, ghosts: list[Entity], distance: float):
        self.pacman = pacman
        self.ghosts = ghosts
        self.distance = distance

    def run(self):
        # We get the valid directions that we can take from the node we're travelling to
        valid_directions = self.pacman.validDirections()
        directions = [] # To hold directions to take to avoid the ghost(s)
        for ghost in self.ghosts:
            # Check if ghost is too close to pacman
            if (ghost.position - self.pacman.position).magnitude() <= self.distance:
                # If it is, find the direction to take to avoid the ghost
                directions.append(self.pacman.goalDirectionFlee(valid_directions, ghost))
        # Among the list of (direction, distance) returned, choose the direction with the highest distance
        estimated_direction = directions[directions.index(max(directions, key=lambda x: x[1]))][0]
        if any(dir[0] == estimated_direction * -1 for dir in directions):
            # choose the last valid direction that is not estimated_direction or its opposite
            valid_directions.remove(estimated_direction * -1)
            valid_directions.remove(estimated_direction)
            if valid_directions:
                # If there are still valid directions left, choose one at random
                self.pacman.bTDir = choice(valid_directions)
            else: self.pacman.bTDir = estimated_direction # If no valid directions left, just go in the estimated direction
        else: self.pacman.bTDir = estimated_direction 
        return True

# Task that finds the closest pellet and sets pacman's goal to it
class GreedyPellet(Task):
    def __init__(self, pacman: Entity, pellets: PelletGroup):
        self.pacman = pacman
        self.pellets = pellets

    def run(self):
        # Find the closest pellet to pacman
        closest_pellet = None
        closest_distance = float('inf')
        for pellet in self.pellets.pelletList:
            distance = (self.pacman.position - pellet.position).magnitude()
            if distance < closest_distance:
                closest_distance = distance
                closest_pellet = pellet

        # Set pacman's goal to the closest pellet's position
        if closest_pellet is not None:
            self.pacman.goal = closest_pellet.position
            self.pacman.bTDir = self.pacman.goalDirection(self.pacman.validDirections())
            #print(f"Closest pellet found at {closest_pellet.position} with distance {closest_distance}")
            return True
        return False