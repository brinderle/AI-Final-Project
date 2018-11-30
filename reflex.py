# Created by Minbiao Han and Roman Sharykin
# AI fall 2018

from __future__ import print_function
from __future__ import division

from builtins import range
from past.utils import old_div
import MalmoPython
import json
import logging
import math
import os
import random
import sys
import time
import re
import uuid
from collections import namedtuple
from operator import add
from random import *
import numpy as np

### You should define your evaluation function here
# Inputs: pos - tuple (position of player), enemy_pos - tuple, food - array
# Output: your evaluation score
# should assess
    # how far the player is from the nearest destination block
    # how many destination blocks have not been visited
    # how far the player is from the enemy at any given time
def evalfuncReflex(pos, enemy_pos, dest_blocks):
    ### YOUR CODE HERE ###
    # adjust the position and enemy position tuples to be more accurate in calculating distance to
    # the destinations, which are integer tuples, whereas position sits on a corner of a block + .5
    pos_x = pos[0]
    pos_y = pos[1]
    adjusted_pos = (pos_x - .5, pos_y - .5)
    enemy_pos_x = enemy_pos[0]
    enemy_pos_y = enemy_pos[1]
    adjusted_enemy_pos = (enemy_pos_x - .5, enemy_pos_y - .5)


    # I think the destinations are automatically deleted from the list after you encounter them
    score = 0
    destCount = len(dest_blocks)
    closestDest = findClosestDest(adjusted_pos, dest_blocks)
    closestDestDistance = manhattan_distance(adjusted_pos, closestDest)
    distanceToEnemy = manhattan_distance(adjusted_pos, adjusted_enemy_pos)
    enemyDistanceToClosestDest = manhattan_distance(closestDest, adjusted_enemy_pos)

    # need a special case if the position is also a destination, can't divide by zero
    inverse_closestDestDistance = 0
    if closestDestDistance == 0:
        inverse_closestDestDistance = 5
    else:
        inverse_closestDestDistance = 1/closestDestDistance
    # also need a special case if you and enemy are in the same spot
    if distanceToEnemy == 0:
        inverse_distanceToEnemy = 2
    else:
        inverse_distanceToEnemy = 1/distanceToEnemy
    # return really small number if the move would put you on an enemy square
    # want to avoid at all costs
    if distanceToEnemy == 0:
        score = -10000000000
    elif distanceToEnemy == 1:
        # enemy is one move from randomly moving into you, try to avoid this
        if destCount == 1 and closestDestDistance == 0: # GO, you will finish the game
            score = inverse_closestDestDistance - inverse_distanceToEnemy
        else:
            score = inverse_closestDestDistance - inverse_distanceToEnemy
    elif closestDestDistance < enemyDistanceToClosestDest:
        # it is safe to go to the nearest destination
        # prioritize going to the destination over how far the enemy is from you
        score = 10 * inverse_closestDestDistance - inverse_distanceToEnemy
    else: # closestDestDistance >= enemyDistanceToClosestDest
        score = 5 * inverse_closestDestDistance - inverse_distanceToEnemy

    # print("The CLOSEST DESTINATION is " + str(closestDest))
    # print("The SCORE is " + str(score))
    # print("The inverse closest dest distance is " + str(inverse_closestDestDistance))
    print(str(len(dest_blocks)) + " food remaining")
    return score

def findClosestDest(pos, dest_blocks):
    minDistance = math.inf
    for i in range(0, len(dest_blocks)):
        distanceToDest = manhattan_distance(pos, dest_blocks[i])
        if distanceToDest < minDistance:
            minDistance = distanceToDest
            closestDest = dest_blocks[i]
    return closestDest

### Implement a way for the agent to decide which way to move
# Inputs: pos - tuple (position of player), world_state, enemy_pos - tuple, food - array
# Output: direction in which to move (can be a string, int, or whatever way you want to implement it)
def chooseAction(pos, wstate, dest_blocks, enemy_pos):
    ### YOUR CODE HERE ###
    # determine which moves are legal
    legalMoves = ["left", "right", "back", "forward"]
    illegalMoveList = illegalMoves(wstate)
    for move in illegalMoveList:
        legalMoves.remove(move)
    # evaluate the moves that are legal, choose the one with the best score
    legalScores = []
    # change the position depending on the direction of the move
    for move in legalMoves:
        if move == "left":
            # print("This is the left move")
            newPosition = [pos[0] + 1, pos[1]]
        elif move == "right":
            # print("This is the right move")
            newPosition = [pos[0] - 1, pos[1]]
        elif move == "back":
            # print("This is the back move")
            newPosition = [pos[0], pos[1] - 1]
        else: # straight
            # print("This is the forward move")
            newPosition = [pos[0], pos[1] + 1]
        score = evalfuncReflex(newPosition, enemy_pos, dest_blocks)
        legalScores.append(score)

    # find the best score, randomly choose a move with the best score if there are multiple
    maxScore = -10000000000
    bestMoves = []
    for i in range(0, len(legalMoves)):
        if legalScores[i] > maxScore:
            maxScore = legalScores[i]
            bestMoves = [legalMoves[i]]
        elif legalScores[i] == maxScore:
            bestMoves.append(legalMoves[i])

    randomBestIndex = randint(0,len(bestMoves)-1)
    bestMove = bestMoves[randomBestIndex]

    # print("The best move is " + str(bestMove))

    return bestMove

### Move the agent here
# Output: void (should just call the correct movement function)
def reflexAgentMove(agent, pos, wstate, dest_blocks, enemy_pos):
    ### YOUR CODE HERE ###
    # get the direction the agent is supposed to move in
    action = chooseAction(pos, wstate, dest_blocks, enemy_pos)
    # move in the direction
    if action == "right":
        moveRight(agent)
    elif action == "left":
        moveLeft(agent)
    elif action == "forward":
        moveStraight(agent)
    elif action == "back":
        moveBack(agent)
    return

### Helper methods for you to use ###

# Simple movement functions
# Hint: if you want your execution to run faster you can decrease time.sleep
def moveRight(ah):
    ah.sendCommand("strafe 1")
    time.sleep(.1)


def moveLeft(ah):
    ah.sendCommand("strafe -1")
    time.sleep(.1)


def moveStraight(ah):
    ah.sendCommand("move 1")
    time.sleep(.1)


def moveBack(ah):
    ah.sendCommand("move -1")
    time.sleep(.1)

# Used to find which movements will result in the player walking into a wall
### Input: current world state
### Output: An array directional strings
def illegalMoves(world_state):
    blocks = []
    if world_state.number_of_observations_since_last_state > 0:
        msg = world_state.observations[-1].text
        observations = json.loads(msg)
        grid = observations.get(u'floor3x3W', 0)
        if grid[3] == u'diamond_block':
            blocks.append("right")
        if grid[1] == u'diamond_block':
            blocks.append("back")
        if grid[5] == u'diamond_block':
            blocks.append("left")
        if grid[7] == u'diamond_block':
            blocks.append("forward")

        return blocks

# Used to find the Manhattan distance between two tuples
def manhattan_distance(start, end):
    sx, sy = start
    ex, ey = end
    return abs(ex - sx) + abs(ey - sy)

# Do not modify!
###
###
# This functions moves the enemy agent randomly #
def enemyAgentMoveRand(agent, ws):
    time.sleep(0.1)
    illegalgrid = illegalMoves(ws)
    legalLST = ["right", "left", "forward", "back"]
    for x in illegalgrid:
        if x in legalLST:
            legalLST.remove(x)
    y = randint(0,len(legalLST)-1)
    togo = legalLST[y]
    if togo == "right":
        moveRight(agent)

    elif togo == "left":
        moveLeft(agent)

    elif togo == "forward":
        moveStraight(agent)

    elif togo == "back":
        moveBack(agent)

def enemyAgentMoveWithProb(agent, ws, player_pos, pos):
    time.sleep(0.1)
    illegalgrid = illegalMoves(ws)
    legalLST = ["right", "left", "forward", "back"]
    for x in illegalgrid:
        if x in legalLST:
            legalLST.remove(x)
    y = randint(0,len(legalLST)-1)

    # get a random number between 0 and 1
    probTowardsPlayer = .4
    z = random()
    if z < probTowardsPlayer:
        legalScores = []
        # change the position depending on the direction of the move
        for move in legalLST:
            if move == "left":
                newPosition = [pos[0] + 1, pos[1]]
            elif move == "right":
                newPosition = [pos[0] - 1, pos[1]]
            elif move == "back":
                newPosition = [pos[0], pos[1] - 1]
            else: # forward
                newPosition = [pos[0], pos[1] + 1]
            score = manhattan_distance(newPosition, player_pos)
            legalScores.append(score)

        # find the best score or min distance, randomly choose a move with the best score if there are multiple
        minDistance = 10000000000
        bestMoves = []
        for i in range(0, len(legalLST)):
            if legalScores[i] < minDistance:
                minDistance = legalScores[i]
                bestMoves = [legalLST[i]]
            elif legalScores[i] == minDistance:
                bestMoves.append(legalLST[i])

        randomBestIndex = randint(0,len(bestMoves)-1)
        togo = bestMoves[randomBestIndex]
    else:
        togo = legalLST[y]

    if togo == "right":
        moveRight(agent)

    elif togo == "left":
        moveLeft(agent)

    elif togo == "forward":
        moveStraight(agent)

    elif togo == "back":
        moveBack(agent)

def goalAgentMoveRand(agent, ws):
    time.sleep(0.1)
    illegalgrid = illegalMoves(ws)
    legalLST = ["right", "left", "forward", "back"]
    for x in illegalgrid:
        if x in legalLST:
            legalLST.remove(x)
    y = randint(0,len(legalLST)-1)
    togo = legalLST[y]
    if togo == "right":
        moveRight(agent)

    elif togo == "left":
        moveLeft(agent)

    elif togo == "forward":
        moveStraight(agent)

    elif togo == "back":
        moveBack(agent)