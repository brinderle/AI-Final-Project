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

    print(str(len(dest_blocks)) + " food remaining")
    return score

def evalfuncReflexTwoEnemies(pos, enemy_pos, enemy2_pos, goal_pos, dest_blocks):
    # print(str(goal_pos[0]) + ", " + str(goal_pos[1]))
    temp_food = dest_blocks.copy()

    in_food = 0
    if (pos[0]-.5, pos[1]-.5) in temp_food:
        temp_food.remove((pos[0]-.5, pos[1]-.5))
        in_food = 15
    
    #find nearest food block
    block_dist = {}
    temp_pos = (pos[0]-.5, pos[1]-.5)
    for i in range(len(temp_food)):
        block_dist[i] = manhattan_distance(temp_pos,dest_blocks[i])
        # block_dist[i] = manhattan_distance(temp_pos,temp_food[i])
        
    if len(temp_food) != 0:
        closest_dest_block = min(block_dist, key=block_dist.get)
        # How far the player is from the nearest destination block
        closest_dist = block_dist.get(closest_dest_block)
    else:
        closest_dist = 0
        # return 10000000
    
    
    # How many destination blocks have not been visited
    blocks_left = len(temp_food)
            
    # How far the player is from the enemy at any given time
    enemy_dist = manhattan_distance(pos,enemy_pos)
    enemy2_dist = manhattan_distance(pos,enemy2_pos)
    # avoid divide by zero errors
    if enemy_dist == 0:
        enemy_dist = .01
    if enemy2_dist == 0:
        enemy2_dist = .01

    if enemy_dist <= 1 or enemy2_dist <= 1:
        return -100000

    goal_dist = manhattan_distance(pos,goal_pos)
    
    # Try 1
    score = 0
    if (pos == enemy_pos or pos == enemy2_pos):
        return -100000000
    if enemy_dist < enemy2_dist:
        enemy_dist = (50/enemy_dist) * -1
        enemy2_dist = (50/enemy2_dist) * -1
    else:
        enemy2_dist = (50/enemy2_dist) * -1
        enemy_dist = (50/enemy_dist) * -1
    #Weights   
    # enemy_dist = (50/enemy_dist) * -1
    if len(dest_blocks) == 0:
        goal_dist = 10 * goal_dist * -1
        closest_dist = 0
    else:
        goal_dist = 0
        closest_dist = 100 * closest_dist * -1 
    # blocks_left *= 1000000   * -1
    
    score += enemy_dist 
    score += enemy2_dist
    score += closest_dist
    score += in_food
    score += goal_dist
    
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
            newPosition = [pos[0] + 1, pos[1]]
        elif move == "right":
            newPosition = [pos[0] - 1, pos[1]]
        elif move == "back":
            newPosition = [pos[0], pos[1] - 1]
        else: # straight
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

    return bestMove

def chooseActionTwoEnemies(pos, wstate, dest_blocks, enemy_pos, enemy2_pos, goal_pos):
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
            newPosition = [pos[0] + 1, pos[1]]
        elif move == "right":
            newPosition = [pos[0] - 1, pos[1]]
        elif move == "back":
            newPosition = [pos[0], pos[1] - 1]
        else: # straight
            newPosition = [pos[0], pos[1] + 1]
        score = evalfuncReflexTwoEnemies(newPosition, enemy_pos, enemy2_pos, goal_pos, dest_blocks)
        print(move + ": " + str(score))
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

def reflexAgentMoveTwoEnemies(agent, pos, wstate, dest_blocks, enemy_pos, enemy2_pos, goal_pos):
    ### YOUR CODE HERE ###
    # get the direction the agent is supposed to move in
    action = chooseActionTwoEnemies(pos, wstate, dest_blocks, enemy_pos, enemy2_pos, goal_pos)
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












################################################
# minimax functions
###############################################
# http://www.giocc.com/concise-implementation-of-minimax-through-higher-order-functions.html


def minimaxEvalfunc(pos, wstate, enemy_pos, enemy2_pos, goal_pos, dest_blocks):
    # while not at goal state 
    # stop if the algorithm goes to a certain depth
    legalPositions = getLegalPositions(pos, wstate)

    best_position = legalPositions[0]
    best_score = float('-inf')

    # print("hello")
    for position in legalPositions:
        score = takeMinScore(position, enemy_pos, enemy2_pos, goal_pos, dest_blocks, 1, wstate)
        # print(score)
        if score > best_score:
            best_position = position
            best_score = score
    
    if best_position == [pos[0] + 1, pos[1]]:
        move = "left"
    elif best_position == [pos[0] - 1, pos[1]]:
        move = "right"
    elif best_position == [pos[0], pos[1] - 1]:
        move = "back"
    elif best_position == [pos[0], pos[1] + 1]: # forward
        move = "forward"

    # return best_position
    return move


def takeMaxScore(pos, enemy_pos, enemy2_pos, goal_pos, dest_blocks, depth, wstate):
        # might want to change the max depth, might want to add a condition to return something if it is at an end state
    if depth == 3:
        return evalfuncReflexTwoEnemies(pos, enemy_pos, enemy2_pos, goal_pos, dest_blocks)
    # find the next possible moves for each enemy
    legalPositions = getLegalPositions(pos, wstate)
    best_score = float('-inf')
    for position in legalPositions:
        score = takeMinScore(position, enemy_pos, enemy2_pos, goal_pos, dest_blocks, depth + 1, wstate)
        if score > best_score:
            best_score = score
    return best_score
   

def takeMinScore(pos, enemy_pos, enemy2_pos, goal_pos, dest_blocks, depth, wstate):
    # assume both enemies move at the same time toward the player
    # might want to change the max depth, might want to add a condition to return something if it is at an end state
    if depth == 3:
        return evalfuncReflexTwoEnemies(pos, enemy_pos, enemy2_pos, goal_pos, dest_blocks)
    # find the next possible moves for each enemy
    legalPositions = getLegalPositions(enemy_pos, wstate)
    legalPositions2 = getLegalPositions(enemy2_pos, wstate)
    best_score = float('inf')
    # we know that the enemy will move to the closest position to the player in the most likely scenario
    closestDist = math.inf
    closestDistPosition = legalPositions[0]
    closestDist2 = math.inf
    closestDistPosition2 = legalPositions2[0]
    for position in legalPositions:
        dist = manhattan_distance(enemy_pos, pos)
        if dist < closestDist:
            closestDist = dist
            closestDistPosition = position
    for position in legalPositions2:
        dist = manhattan_distance(enemy2_pos, pos)
        if dist < closestDist2:
            closestDist2 = dist
            closestDistPosition2 = position

    best_score = takeMaxScore(pos, closestDistPosition, closestDistPosition2, goal_pos, dest_blocks, depth+1, wstate)
    return best_score

def getLegalPositions(pos, wstate):
    legalMoves = ["left", "right", "back", "forward"]
    illegalMoveList = illegalMoves(wstate)
    for move in illegalMoveList:
        legalMoves.remove(move)
    # evaluate the moves that are legal, choose the one with the best score
    # legalScores = []
    newPositions = []
    # change the position depending on the direction of the move
    for move in legalMoves:
        if move == "left":
            newPosition = [pos[0] + 1, pos[1]]
        elif move == "right":
            newPosition = [pos[0] - 1, pos[1]]
        elif move == "back":
            newPosition = [pos[0], pos[1] - 1]
        else: # straight
            newPosition = [pos[0], pos[1] + 1]
        newPositions.append(newPosition)
    
    return newPositions


def minimaxAgentMove(agent, pos, wstate, dest_blocks, enemy_pos, enemy2_pos, goal_pos):
    ### YOUR CODE HERE ###
    # get the direction the agent is supposed to move in
    action = minimaxEvalfunc(pos, wstate, enemy_pos, enemy2_pos, goal_pos, dest_blocks)
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



def value(pos, player_ws, enemy_pos, enemy2_pos, enemy1_ws, enemy2_ws, goal_pos, dest_blocks, depth, whos_turn):
    if depth == 3:
        return evalfuncReflexTwoEnemies(pos, enemy_pos, enemy2_pos, goal_pos, dest_blocks)

    if whos_turn == "player":
        return max_val(pos, player_ws, enemy_pos, enemy2_pos, enemy1_ws, enemy2_ws, goal_pos, dest_blocks, depth, whos_turn)
    else:
        return exp_value(pos, player_ws, enemy_pos, enemy2_pos, enemy1_ws, enemy2_ws, goal_pos, dest_blocks, depth, whos_turn)

def max_val(pos, player_ws, enemy_pos, enemy2_pos, enemy1_ws, enemy2_ws, goal_pos, dest_blocks, depth, whos_turn):
    v = -100000

    legalMoves = getLegalPositions(pos, wstate)

    for move in legalMoves:
        whos_turn = "enemy"
        v = max(v, value(move, player_ws, enemy_pos, enemy2_pos, enemy1_ws, enemy2_ws, goal_pos, dest_blocks, depth+1, whos_turn))

    return v

def exp_value(pos, player_ws, enemy_pos, enemy2_pos, enemy1_ws, enemy2_ws, goal_pos, dest_blocks, depth, whos_turn)
    v = 0

    legalMoves1 = getLegalPositions(enemy_pos, enemy1_ws)
    legalMoves2 = getLegalPositions(enemy_pos2, enemy2_ws)

    closest_dist1 = 10000
    closest_dist2 = 10000

    for position in legalMoves1:
        dist = manhattan_distance(enemy_pos, pos)
        if dist < closestDist:
            closestDist1 = dist
            closestDistPosition1 = position
    for position in legalMoves2:
        dist = manhattan_distance(enemy2_pos, pos)
        if dist < closestDist2:
            closestDist2 = dist
            closestDistPosition2 = position

    for moves_1 in legalMoves1:
        for moves_2 in legalMoves2:
            if moves_1 == closestDistPosition1:
                p1 = 0.4
            else:
                p1 = 0.6
            if moves_2 == closestDistPosition2:
                p2 = 0.4
            else:
                p2 = 0.6

            whos_turn = "player"

            v += p1*p2*value(pos, player_ws, moves_1, moves_2, enemy1_ws, enemy2_ws, goal_pos, dest_blocks, depth, whos_turn)



