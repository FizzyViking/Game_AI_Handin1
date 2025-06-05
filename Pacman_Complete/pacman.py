from random import choice
import pygame
from pygame.locals import *
from vector import Vector2
from constants import *
from entity import Entity
from sprites import PacmanSprites
from behaviorTree import *

class Pacman(Entity):
    def __init__(self, node, ghosts, pelletGroup):
        Entity.__init__(self, node )
        self.name = PACMAN    
        self.color = YELLOW
        self.direction = LEFT
        self.setBetweenNodes(LEFT)
        self.alive = True
        self.sprites = PacmanSprites(self)
        self.ghosts = ghosts # Ghosts reference
        self.pelletGroup = pelletGroup # Pellets reference
        self.bTDir = None # Estimated direction to take based on BT

    def reset(self):
        Entity.reset(self)
        self.direction = LEFT
        self.setBetweenNodes(LEFT)
        self.alive = True
        self.image = self.sprites.getStartImage()
        self.sprites.reset()

    def die(self):
        self.alive = False
        self.direction = STOP

    def setGhosts(self, ghosts):
        self.ghosts = ghosts

    def setUpBehaviorTree(self):
        # Distance to consider whether a ghost is close to pacman
        isGhostCloseDistance = 110.0 # This distance was mostly trial and error in finding it

        # Create the behavior tree for pacman
        self.tree = Selector([
            Sequence([ 
            IsGhostClose(self, self.ghosts, isGhostCloseDistance), # Is there any ghost close to pacman? or are the nearby ghosts in spawn or freight mode?
            FleeFromGhosts(self, self.ghosts, isGhostCloseDistance) # If so, set pacman to flee from the ghosts
        ]),
        GreedyPellet(self, self.pelletGroup) # If no ghost is close, set goaldirection to go to nearest pellet
        ])

    def update(self, dt):	
        self.sprites.update(dt)
        self.position += self.directions[self.direction]*self.speed*dt

        # Run the behavior tree every frame and update the direction
        self.runBehaviorTree()
        direction = self.bTDir

        if self.overshotTarget():
            self.node = self.target
            if self.node.neighbors[PORTAL] is not None:
                self.node = self.node.neighbors[PORTAL]
            self.target = self.getNewTarget(direction)
            if self.target is not self.node:
                self.direction = direction
            else:
                self.target = self.getNewTarget(self.direction)

            if self.target is self.node:
                self.direction = STOP
                
            self.setPosition()
        else: 
            if self.oppositeDirection(direction):
                self.reverseDirection()

    def runBehaviorTree(self):
        self.tree.run()
    
    # Valid direction and goaldirection but with node changed to target
    def validDirection(self, direction):
        if direction is not STOP:
            if self.name in self.target.access[direction]:
                if self.target.neighbors[direction] is not None:
                    return True
        return False

    def validDirections(self):
        directions = []
        for key in [UP, DOWN, LEFT, RIGHT]:
            if self.validDirection(key):
                if key != self.direction * -1:
                    directions.append(key)
        if len(directions) == 0:
            directions.append(self.direction * -1)
        return directions

    def goalDirection(self, directions):
        distances = []
        for direction in directions:
            vec = self.target.position + self.directions[direction]*TILEWIDTH - self.goal
            distances.append(vec.magnitudeSquared())
        index = distances.index(min(distances))
        return directions[index]
    
    # Goal direction method for use in BT, with the target ghost's position to flee from
    def goalDirectionFlee(self, directions, ghost):
        distances = []
        for direction in directions:
            vec = self.target.position + self.directions[direction]*TILEWIDTH - ghost.position
            distances.append(vec.magnitudeSquared())
        index = distances.index(max(distances))
        return (directions[index], max(distances))

    def eatPellets(self, pelletList):
        for pellet in pelletList:
            if self.collideCheck(pellet):
                return pellet
        return None    
    
    def collideGhost(self, ghost):
        return self.collideCheck(ghost)

    def collideCheck(self, other):
        d = self.position - other.position
        dSquared = d.magnitudeSquared()
        rSquared = (self.collideRadius + other.collideRadius)**2
        if dSquared <= rSquared:
            return True
        return False
