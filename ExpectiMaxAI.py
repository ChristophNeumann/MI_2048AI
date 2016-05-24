# 2048 5x5 ExpectiMaxi AI

from game import Game, Direction
import numpy
import copy
import time

# MaxNode represents our turn
class MaxNode:
    def __init__(self, game, depth):
        self.game = copy.deepcopy(game)
        self.depth = depth
        self.action = 0
        self.successors = []
        self.actionList = []
        self.action = 0
        self.value = self.getValue()


    # Easy "print maxNode" functionality
    def __str__(self):
        printStr =  "MaxNode:\n"
        printStr +=  str(self.game.state.astype(numpy.uint32))
        printStr += "\nMaxNodeValue: " + str(self.value)
        return printStr


    # Calculates the value of this MaxNode
    def getValue(self):
        if self.depth == 0:
            value = self.maxNodeTerminalValue()
        else:
            # generate all chance node successors
            self.branch()
            possibleValueSuccessors = []
            directionSuccessors = []
            for chanceNode in self.successors:
                possibleValueSuccessors.append(chanceNode.value)
                directionSuccessors.append(chanceNode.direction)
            possibleValueSuccessors = numpy.array(possibleValueSuccessors)
            value = max(possibleValueSuccessors)
            self.action = directionSuccessors[numpy.argmax(possibleValueSuccessors)]
            self.actionList = possibleValueSuccessors
        return value


    # Genertes ChanceNodes for each possible move
    def branch(self):
        for i in xrange(4):
            succGame = copy.deepcopy(self.game)

            # perform the i'st move and only add as successor if move was allowed
            if succGame.move(i+1):
                succ = ChanceNode(succGame, i+1, depth= self.depth)
                self.successors.append(succ)

    # Calculates the value of the current board, this is also called the heuristic
    def maxNodeTerminalValue(self):
        weightMatrix = numpy.array(
            [[0.15, 0.135759, 0.121925, 0.102812, 0.099937],
            [0.135759, 0.0997992, 0.0888405, 0.076711, 0.0724143],
            [0.0724143, 0.060654 , 0.0562579 , 0.037116 , 0.0161889],
            [0.0161889, 0.0125498 , 0.00992495 , 0.00575871 , 0.00335193],
            [0.0125498 , 0.00992495 , 0.00575871 , 0.00335193, 0.0002]])

        # To get a balanced value of the current board, we calculate the 
        # value based on a rotated and transposed matrix 
        # and then count the maximum as value.
        possibleValues = []
        for i in range(0,4):
            currentWeight = numpy.rot90(weightMatrix, i)
            possibleValues.append((currentWeight * self.game.state).sum())
            possibleValues.append((currentWeight.transpose() * self.game.state).sum())
        value = max(possibleValues)
        return value

# ChanceNode represents the random placement of a tile at the board
class ChanceNode:
    def __init__(self, game, direction, depth):
        self.depth = depth
        self.value = 0
        self.direction = direction
        self.game = game
        self.branchNodes = []
        self.value = self.getChanceNodeValue()


    # Generates corresponding successor max nodes for each available tile
    def branch(self):
        availableCells = self.game.get_available_cells()
        branchWeights = []
        branchNodes = []

        # for each available cell ...
        for cell in availableCells:
            branchGame = copy.deepcopy(self.game)

            # ... generate two MaxNodes, one with a 2- and the other with a 4-tile
            for value in [2,4]:
                if value == 2:
                    probability = 0.9
                else:
                    probability = 0.1

                # store weight, so we can later calculate the value of this chance node
                branchWeight = 1.0 / (len(availableCells)) * probability
                branchWeights.append(branchWeight)
                branchGame.set(cell, value)

                branchedMaxNode = MaxNode(branchGame, depth=(self.depth-1))
                branchNodes.append(branchedMaxNode)

        self.branchWeights = numpy.array(branchWeights)
        self.branchNodes = branchNodes


    # Calculates the chance node value by weighted probabilites
    def getChanceNodeValue(self):
        self.branch()
        branchValues = []
        for node in self.branchNodes:
            branchValues.append(node.value)

        successorValues = numpy.array(branchValues)
        value = sum(successorValues * self.branchWeights)
        return value

    # Easy "print chanceNode" functionality
    def __str__(self):
        printStr =  "ChanceNode \n"
        printStr += str(self.game.state.astype(numpy.uint32))
        printStr += "\nChanceNodeValue:" + str(self.value)
        return printStr

# start
initialGame = Game(testing = False)
gameRunning = True
while gameRunning:
    gameRunning = not initialGame.over
    initialGame.testing = True
    depth = 1

    # use more depth if we have only a few free tiles
    if len(initialGame.get_available_cells()) < 8:
        print "using depth=2"
        depth = 2
    if len(initialGame.get_available_cells()) < 4:
        print "using depth=3"
        depth = 3
    elif len(initialGame.get_available_cells()) < 3:
        print "using depth=4"
        depth = 4

    startNode = MaxNode(initialGame, depth)
    initialGame.testing = False
    print initialGame.state.astype(numpy.uint32)
    initialGame.move(startNode.action)
    if startNode.action == 1:
        print "left"
    elif startNode.action == 2:
        print "right"
    elif startNode.action == 3:
        print "up"
    elif startNode.action == 4:
        print "down"
    print initialGame.state.astype(numpy.uint32)
    print "*********************"
