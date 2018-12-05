import random 
import time
import copy
import os

size = 10

# def reflex_eval(moves, players, food):
    # vals = []
    # for i in moves:
        # tmp = 0
        # tmp -= 100*manhattan_distance(i, players[1])
        # tmp -= 100*manhattan_distance(i, players[2])
        # tmp += 100*manhattan_distance(i, players[3])
        # for j in food:
            # tmp -= manhattan_distance(i, j)
        # vals.append(tmp)
    # return moves[vals.index(max(vals))]   

def reflex_eval(moves, players, food):
    vals = []
    for i in moves:
        tmp_food = copy.deepcopy(food)
        tmp = 0
        in_food = 0
        if i in tmp_food:
            print("getting food!")
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
            return -100000
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
    if vals.count(max(vals)) > 1:
        choices = []
        for i in vals:
            if i == max(vals):
                choices.append(i)
        print(moves[random.randint(0,len(choices)-1)])
        time.sleep(.2)
        return moves[random.randint(0,len(choices)-1)]
    print(moves[vals.index(max(vals))])
    time.sleep(.2)
    return moves[vals.index(max(vals))]
    
def find_closest_food(players, food):
    closest_dist = size*size
    # closest_food = None
    for i in food:
        tmp = manhattan_distance(players[0], i)
        if tmp < closest_dist:
            closest_dist = tmp
            # closest_food = i
    return closest_dist
    
def main():
    grid, players, food = setup(size)
    score = 0
    printGrid(grid, players, food, score)
    for i in range(50):
        players = move(players, food)
        score = check_score(players, food, score)
        print("food left: ", len(food))
        os.system('cls' if os.name == 'nt' else 'clear')
        printGrid(grid, players, food, score)
        time.sleep(.2)
        if players[0] in players[1:]:
            break

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
    grid2 = copy.deepcopy(grid)
   
    # display food
    for i in food:
        grid2[i[0]][i[1]] = 'O'
      
    # display players
    c = 0
    for i in players:
        char = 'X'
        if c == 0:
            char = 'P'
        if c == 3:
            char = 'G'
        grid2[i[0]][i[1]] = char
        c += 1
    
    # print grid
    print('\n'.join(['|'.join(['{:2}'.format(item) for item in row]) for row in grid2]))
    print("Score: ", score)
       

# moves all players except for the main agent
# currently all moves are random
def move(players, food):
    # player
    player_moves = get_moves(players[0])
    players[0] = reflex_eval(player_moves, players, food)

    # first enemy
    enemy_moves = get_moves(players[1])
    players[1] = enemy_moves[random.randint(0,len(enemy_moves)-1)]
    
    # second enemy
    enemy_moves = get_moves(players[2])
    players[2] = enemy_moves[random.randint(0,len(enemy_moves)-1)]
    
    # goal
    goal_moves = get_moves(players[3])
    players[3] = goal_moves[random.randint(0,len(goal_moves)-1)]
    
    return players
    
# determines legal moves for a player
def get_moves(player):
    moves = [(0,1), (0,-1), (1,0), (-1,0)]
    ret = []
    for i in moves:
        tmp = [player, i]
        val = (sum(e[0] for e in tmp), sum(e[1] for e in tmp))
        if val[0] >= 0 and val[0] < size and val[1] >= 0 and val[1] < size:
            ret.append(val)
    return ret
    
# distance function
def manhattan_distance(start, end):
    sx, sy = start
    ex, ey = end
    return abs(ex - sx) + abs(ey - sy)
  
def check_score(players, food, score):
    if players[0] == players[1] or players[0] == players[2]:
        score -= 100
    if players[0] == players[3]:
        score += 300
    if players[0] in food:
        score += 25
        food.remove(players[0])
    else:
        score -= 1
    return score
  
if __name__ == '__main__':
    main()
