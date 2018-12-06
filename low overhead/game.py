import random 
import time
import copy
import os
import math
import sys

size = 10

def main():     
    grid, players, food = setup(size)
    score = 0
    layoutFile = sys.argv[1] + ".lay"
    grid, players, food, walls = setupLayout(layoutFile)
    printGrid(grid, players, food, score)
    for i in range(500):
        players, food, score = expectimove(grid, players, food, walls, score)

def readGrid(layoutFile):
    with open(layoutFile) as layout:
        rows = layout.readlines()
        print(rows)

def getLayout(name):
    matrix = tryToLoad("layouts/" + name)
    return matrix

def tryToLoad(fullname):
    if (not os.path.exists(fullname)): return None
    f = open(fullname)
    print(f)
    Matrix = [line.strip() for line in f]
    f.close()
    return Matrix

def setupLayout(layoutFile):
    grid = getLayout(layoutFile)
    food = []
    players = [(0,0), (0,0), (0,0), (0,0)]
    walls = []
    for i in range(len(grid)):
        grid[i] = list(grid[i])
        for j in range(len(grid[i])):
            if grid[i][j] == '.':
                food.append((i,j))
                grid[i][j] = ' '
            elif grid[i][j] == 'P':
                players[0] = (i,j)
                grid[i][j] = ' '
            elif grid[i][j] == 'E':
                players[1] = (i,j)
                grid[i][j] = ' '
            elif grid[i][j] == 'F':
                players[2] = (i,j)
                grid[i][j] = ' '
            elif grid[i][j] == 'G':
                players[3] = (i,j)
                grid[i][j] = ' '
            elif grid[i][j] == "%":
                walls.append((i,j))
    return grid, players, food, walls
        
# randomly generates food and player locations     
def setup(size):
    # make map
    grid = [[' ' for x in range(size)] for y in range(size)] 

    # generate foods
    food = []
    for i in range(int(size*size/4)):
        x = random.randint(0,size-1)
        y = random.randint(0,size-1)
        if (x,y) not in food:
            food.append((x,y))
            
    # put food on grid
    # for f in food:
        # grid[f[0]][f[1]] = 1
        
    # create players
    players = [(0,0), (0,0), (0,0), (0,0)]
    # players[0] is character
    # 1 is enemy
    # 2 is enemy
    # 3 is goal

    # randomly distribute players
    while len(players) != len(set(players)):
        players[0] = (random.randint(0,size-1), random.randint(0,size-1))
        players[1] = (random.randint(0,size-1), random.randint(0,size-1))
        players[2] = (random.randint(0,size-1), random.randint(0,size-1))
        players[3] = (random.randint(0,size-1), random.randint(0,size-1))
  
    return grid, players, food
    
# prints grid and score
def printGrid(grid, players, food, score):
    os.system('cls' if os.name == 'nt' else 'clear')
  
    grid2 = copy.deepcopy(grid)
   
    # display food
    for i in food:
        grid2[i[0]][i[1]] = '.'
      
    # display players
    c = 0
    for i in players:
        if c == 0:
            char = 'P'
        if c == 1:
            char = 'E'
        if c == 2:
            char = 'F'
        if c == 3:
            char = 'G'
        grid2[i[0]][i[1]] = char
        c += 1
    
    # print grid
    print('\n'.join([' '.join(['{:2}'.format(item) for item in row]) for row in grid2]))
    print("Score: ", score)
       
# moves all players except for the main agent
# currently all moves are random
def move(grid, players, food, walls, score):
    # player
    player_moves = get_moves(players[0], grid, walls)
    vals = reflex_eval(player_moves, players, food)
    players[0] = choose_move(player_moves, vals)
    
    score = check_score(grid, players, food, score)
    printGrid(grid, players, food, score)
    # time.sleep(.1)

    # first enemy
    enemy_moves = get_moves(players[1], grid, walls)
    players[1] = enemy_moves[random.randint(0,len(enemy_moves)-1)]
    
    score = check_score(grid, players, food, score)
    printGrid(grid, players, food, score)
    # time.sleep(.1)
    
    # second enemy
    enemy_moves = get_moves(players[2], grid, walls)
    players[2] = enemy_moves[random.randint(0,len(enemy_moves)-1)]
    
    score = check_score(grid, players, food, score)
    printGrid(grid, players, food, score)
    # time.sleep(.1)
    
    # goal
    goal_moves = get_moves(players[3], grid, walls)
    players[3] = goal_moves[random.randint(0,len(goal_moves)-1)]
        
    score = check_score(grid, players, food, score) 
    printGrid(grid, players, food, score)
    # time.sleep(.1)
        
    return players, food, score
    
# determines legal moves for a player
def get_moves(player, grid, walls):
    moves = [(0,1), (0,-1), (1,0), (-1,0)]
    ret = []
    for i in moves:
        tmp = [player, i]
        val = (sum(e[0] for e in tmp), sum(e[1] for e in tmp))
        if val[0] >= 0 and val[0] < len(grid) and val[1] >= 0 and val[1] < len(grid[0]):
            if val not in walls:
                ret.append(val)
    return ret

# distance function
def manhattan_distance(start, end):
    sx, sy = start
    ex, ey = end
    return abs(ex - sx) + abs(ey - sy)
  
# updates score; removes food if necessary
# ends game if player touches goal or enemy
def check_score(grid, players, food, score):
    if players[0] == players[1] or players[0] == players[2]:
        score -= 100
        printGrid(grid, players, food, score)
        quit()
    elif players[0] == players[3]:
        score += 300
        printGrid(grid, players, food, score)
        quit()
    if players[0] in food:
        score += 25
        food.remove(players[0])
        printGrid(grid, players, food, score)
        # time.sleep(.1)
        return score
    else:
        score -= .25
    return score

# finds closest food block and returns distance to it    
def find_closest_food(players, food):
    closest_dist = size*size
    # closest_food = None
    for i in food:
        tmp = manhattan_distance(players[0], i)
        if tmp < closest_dist:
            closest_dist = tmp
            # closest_food = i
    return closest_dist

# reflex evaluation function
def reflex_eval(moves, players, food):
    vals = []
    for i in moves:
        tmp_food = copy.deepcopy(food)
        tmp = 0
        in_food = 0
        if i in tmp_food:
            tmp_food.remove(i)
            in_food = 15   
        if len(tmp_food) != 0:
            closest_dist = find_closest_food(players, food)
                
            # closest_dist = manhattan_distance(players[0], closest_food)
        else:
            closest_dist = 0
        enemy1_dist = manhattan_distance(players[0], players[1])
        enemy2_dist = manhattan_distance(players[0], players[2])
        if enemy1_dist <= 1 or enemy2_dist <= 1:
            tmp = -100000
        goal_dist = manhattan_distance(players[0], players[3])
        if enemy1_dist < enemy2_dist:
            enemy1_dist = (50/enemy1_dist) * -1
            enemy2_dist = (50/enemy2_dist) * -1
        else:
            enemy2_dist = (50/enemy2_dist) * -1
            enemy1_dist = (50/enemy1_dist) * -1
        tmp += enemy1_dist 
        tmp += enemy2_dist
        tmp += closest_dist
        tmp += in_food
        tmp += goal_dist
        vals.append(tmp)
    
    return vals

def choose_move(moves, vals):
    print(moves)
    print(vals)
    # time.sleep(1)    
    if vals.count(max(vals)) > 1:
        choices = []
        for i in range(len(vals)):
            if vals[i] == max(vals):
                choices.append(moves[i])
        print(choices, " ...choosing...")
        print(choices[random.randint(0,len(choices)-1)])
        # time.sleep(1)
        return choices[random.randint(0,len(choices)-1)]
    print(moves[vals.index(max(vals))])
    # time.sleep(1)
    return moves[vals.index(max(vals))]
        
# todo
def minimax_eval(moves, players, food):
    vals = [0]
    for i in moves:
        tmp = get_min_score(moves, players, food, 7)
        vals.append(tmp)
    print(vals)
    choices = []
    for i in vals:
        if i == max(vals):
            i += random.randint(0,10000)
        choices.append(i)
    return moves[choices.index(max(choices))]

# todo    
def get_max_score(moves, players, food, depth):
    if depth == 3:
        return evalfuncReflexTwoEnemies(pos, enemy_pos, enemy2_pos, goal_pos, dest_blocks)
    else:
        return get_min_score(moves, players, food, depth-1)
    # player_moves = get_moves(players[0])
    # best_score = float('-inf')
    # for i in player_moves:
        # val = get_min_score(moves, players, food, depth-1)
        # if val > best_score:
            # best_score = val
    
    return best_score
 
# todo 
def get_min_score(moves, players, food, depth):
    if depth == 3:
        return reflex_eval(moves, players, food)
    enemy1_moves = get_moves(players[1])
    enemy2_moves = get_moves(players[2])
    
    closest_dist1 = math.inf
    closest_dist2 = math.inf
    closest_pos1 = enemy1_moves[0]
    closest_pos2 = enemy2_moves[0]
    
    for i in enemy1_moves:
        dist = manhattan_distance(players[0], i)
        if dist < closest_dist1:
            closest_dist1 = dist
            closest_pos1 = i
    for i in enemy2_moves:
        dist = manhattan_distance(players[0], i)
        if dist < closest_dist2:
            closest_dist2 = dist
            closest_pos2 = i
    
    pred_players = copy.deepcopy(players)
    pred_players[1] = closest_pos1
    pred_players[2] = closest_pos2
    
    return get_max_score(moves, pred_players, food, depth-1)
    

def value(grid, players, food, walls, depth, moves, whos_turn):
    if depth == 3:
        legalMoves = get_moves(players[0], grid, walls)
        vals = reflex_eval(legalMoves, players, food)
        
        best_score = max(vals)
        # print(best_score)
        # best_score = -100000000
        # for i in range(len(vals)):
        #     if vals[i] > best_score:
        #         best_score = vals[i]
        # print(best_score)
        return best_score


    if whos_turn == "player":
        return max_val(grid, players, food, walls, depth, moves, whos_turn)
    else:
        return exp_value(grid, players, food, walls, depth, moves, whos_turn)

def max_val(grid, players, food, walls, depth, moves, whos_turn):
    v = -100000

    legalMoves = get_moves(players[0], grid, walls)

    for move in legalMoves:
        whos_turn = "enemy"
        players[0] = move
        v = max(v, value(grid, players, food, walls, depth+1, moves, whos_turn))

    return v

def exp_value(grid, players, food, walls, depth, moves, whos_turn):
    v = 0

    legalMoves1 = get_moves(players[1], grid, walls)
    legalMoves2 = get_moves(players[2], grid, walls)

    closestDist = 10000
    closestDist2 = 10000

    for position in legalMoves1:
        dist = manhattan_distance(players[1], players[0])
        if dist < closestDist:
            closestDist1 = dist
            closestDistPosition1 = position
    for position in legalMoves2:
        dist = manhattan_distance(players[2], players[0])
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
            players[1] = moves_1
            players[2] = moves_2
            v += p1*p2*value(grid, players, food, walls, depth+1, moves, whos_turn)

            return v


def expectimove(grid, players, food, walls, score):
    player_moves = get_moves(players[0], grid, walls)
    best_move = player_moves[0]
    best_score = -10000000

    for i in range(len(player_moves)):
        vals = value(grid, players, food, walls, 0, player_moves[i], "player")
        if vals > best_score:
            best_score = vals
            best_move = player_moves[i]

    print(best_move)
    players[0] = best_move
    # players[0] = choose_move(player_moves, vals)
    
    score = check_score(grid, players, food, score)
    printGrid(grid, players, food, score)
    time.sleep(.1)

    # first enemy
    enemy_moves = get_moves(players[1], grid, walls)
    players[1] = enemy_moves[random.randint(0,len(enemy_moves)-1)]
    
    score = check_score(grid, players, food, score)
    printGrid(grid, players, food, score)
    time.sleep(.1)
    
    # second enemy
    enemy_moves = get_moves(players[2], grid, walls)
    players[2] = enemy_moves[random.randint(0,len(enemy_moves)-1)]
    
    score = check_score(grid, players, food, score)
    printGrid(grid, players, food, score)
    time.sleep(.1)
    
    # goal
    goal_moves = get_moves(players[3], grid, walls)
    players[3] = goal_moves[random.randint(0,len(goal_moves)-1)]
        
    score = check_score(grid, players, food, score) 
    printGrid(grid, players, food, score)
    time.sleep(.1)
        
    return players, food, score

if __name__ == '__main__':
    main()
