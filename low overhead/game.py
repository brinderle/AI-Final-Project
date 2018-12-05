import random 
import time
import copy
import os

size = 10

def main():
    grid, players, food = setup(size)
    score = 0
    printGrid(grid, players, food, score)
    for i in range(50):
        players = move(players)
        os.system('cls' if os.name == 'nt' else 'clear')
        printGrid(grid, players, food, score)
        time.sleep(.2)
        print()

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
def move(players):
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
       
if __name__ == '__main__':
    main()
