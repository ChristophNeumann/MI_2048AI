# 2048 5x5 ExpectiMaxi AI
# Usage: "python 2048ai.py min" or "python 2048ai.py exp"

from game import Game, Direction
import numpy
import copy
import time
import sys
import os

# Min node as Nature move
class MinNode:
    def __init__(self, game, direction, depth, parentAlpha = float("-infinity")):
        self.direction = direction
        self.parentAlpha = parentAlpha
        self.game = copy.deepcopy(game)
        self.depth = depth
        self.action = 0
        self.successors = []
        self.actionList = []
        self.beta = float("infinity")
        self.value = self.getValue()

    def branch(self):
        availableCells = self.game.get_available_cells()
        successors = []
        prune = False
        # for each available cell ...
        for cell in availableCells:
            branchGame = copy.deepcopy(self.game)
            # ... generate two MaxNodes, one with a 2- and the other with a 4-tile
            for value in [2, 4]:
                # store weight, so we can later calculate the value of this min node
                #Check if parent can't enforce a better outcome
                if self.parentAlpha <= self.beta:
                    branchGame.set(cell, value)
                    branchedMaxNode = MaxNode(branchGame, depth= self.depth - 1, mode = "min", parentBeta= self.beta)
                    self.beta = min(self.beta, branchedMaxNode.value)
                    successors.append(branchedMaxNode)
                #Parent can enforce a better outcome. No more need to check the for loop or to create successors
                else:
                    prune = True
                    break
            if prune:
                break
        self.successors = successors

    def getValue(self):
        # generate all chance node successors
        self.branch()
        possibleValueSuccessors = []
        for maxNode in self.successors:
            possibleValueSuccessors.append(maxNode.value)
            self.beta = min(self.beta,maxNode)

        possibleValueSuccessors = numpy.array(possibleValueSuccessors)
        value = min(possibleValueSuccessors)
        return value

# MaxNode represents our turn
class MaxNode:
    def __init__(self, game, depth, mode = "exp", parentBeta = float("infinity")):
        self.game = copy.deepcopy(game)
        self.parentBeta = parentBeta
        self.depth = depth
        self.action = 0
        self.successors = []
        self.actionList = []
        self.action = 0
        self.mode = mode
        self.alpha = float("-infinity")
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
            #Check if branching was possible at this node
            if possibleValueSuccessors:
                possibleValueSuccessors = numpy.array(possibleValueSuccessors)
                value = max(possibleValueSuccessors)
                self.action = directionSuccessors[numpy.argmax(possibleValueSuccessors)]
                self.actionList = possibleValueSuccessors
            #If branching was infeasible, return infinity as value
            else:
                value = float("-infinity")
        return value


    # Genertes ChanceNodes for each possible move
    def branch(self):
        for i in xrange(4):
            succGame = copy.deepcopy(self.game)
            # perform the i'st move and only add as successor if move was allowed
            if succGame.move(i+1):
                if self.mode == "exp":
                    succ = ChanceNode(succGame, i+1, self.depth)
                    self.successors.append(succ)
                # Ensure that parent is unable to enforce a better outcome. If false, no more need for creating children
                elif self.alpha <= self.parentBeta:
                    succ = MinNode(succGame, (i+1), self.depth, parentAlpha=self.alpha)
                    self.alpha = max(self.alpha, succ.value)
                    self.successors.append(succ)
                #No more evaluation necessary. Prune this node
                else:
                    break


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

class Agent:
    def __init__(self, mode, printMe = True):
        self.score = 0
        self.mode = mode
        self.gameState = numpy.zeros([5,5])
        self.printMe = printMe
        self.playGame()

    def playGame(self):
    # start
        startTime = time.clock()
        initialGame = Game(testing = False)
        gameRunning = True
        firstGoalReached = False
        secondGoalReached = False
        boardHeuristicScore = 0

        # measurements
        target = 2048
        measuredTimes = []

        while gameRunning:
            gameRunning = not initialGame.over
            initialGame.testing = True
            optimizedDepth = 1

            # use more depth if we have only a few free tiles
            if len(initialGame.get_available_cells()) < 3 :
                optimizedDepth = 4
            elif len(initialGame.get_available_cells()) < 4:
                optimizedDepth = 3
            elif len(initialGame.get_available_cells()) < 7 :
                optimizedDepth = 2

            startNode = MaxNode(initialGame, optimizedDepth, mode=self.mode)
            boardHeuristicScore = startNode.value;
            initialGame.testing = False
            initialGame.move(startNode.action)
            elapsedTime = time.clock() - startTime

            self.gameState = initialGame.state.astype(numpy.uint32)
            self.score = initialGame.score

            # check if the AI lost the game or we reached our maximum tile we want to achive
            if initialGame.over or target > 2048:
                print "Game ended after : "  + str(elapsedTime) + "seconds"
                gameRunning = False

                # log final heuristic score and times to csv file
                with open("benchmark.csv", "a") as file:
                    benchmarkString = str(self.score) + ", " + str(boardHeuristicScore) + ", " + ", ".join([str(i) for i in measuredTimes]) + os.linesep
                    print benchmarkString
                    file.write(benchmarkString)

            else:
                # print game board at each move
                if self.printMe:
                    print "Depth = " + str(optimizedDepth)
                    self.printGame(startNode.action)
                
                # check if AI has reached a target
                if (self.gameState == target).any():
                    print "Time elapsed to reach " + str(target) + ": " + str(elapsedTime)

                    # set next target
                    target = target * 2;
                    measuredTimes.append(elapsedTime);

        print "game is over. "
        print "board heuristic score: " + str(boardHeuristicScore)
        self.printGame(5)

    def printGame(self, action):
        if action == 1:
            print "left"
        elif action == 2:
            print "right"
        elif action == 3:
            print "up"
        elif action == 4:
            print "down"
        print self.gameState
        print "Score : " + str(self.score)
        print "*********************"

# read either exp or min from command line arguments
mode = "exp"
if sys.argv[1] == "min":
    mode = "min"

print "Performing AI in " + mode + " mode."
myAgent = Agent(mode, True)

