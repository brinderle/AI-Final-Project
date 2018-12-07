def expectimax(grid, players, food, walls, goal_reached):
    vals = []
    moves = get_moves(players[0], grid, walls)
    for i in moves:
        tmp = exp_val(grid, players, food, walls, 1, goal_reached)
        vals.append(tmp)
    # print(vals)
    choices = []
    for i in vals:
        # if i == max(vals):
        #     i += random.randint(0,10000)
        # choices.append(i)
        if isinstance(i, float):
            # if i > best_score:
            #     best_score = val
            choices.append(i)
        else:
            for i in range(len(vals)):
                if vals[i] == max(vals):
                    choices.append(vals[i])
    # return moves[choices.index(max(choices))]
    return moves[choices.index(choices[0])], goal_reached

# todo    
def max_val(grid, players, food, walls, depth, goal_reached):
    player_moves = get_moves(players[0], grid, walls)
    if depth == 5:
        return reflex_eval(player_moves, players, food, goal_reached), goal_reached
    # else:
        # return exp_val(grid, players, food, walls, depth-1, goal_reached)
    best_score = float('-inf')
    for i in range(len(player_moves)):
        pred_players = copy.deepcopy(players)
        pred_players[0] = player_moves[i]
        val, goal_reached = exp_val(grid, pred_players, food, walls, depth+1, goal_reached)
        # print(val)
        if isinstance(val, float):
            if val > best_score:
                best_score = val
        else:
            for i in range(len(val)):
                if val[i] > best_score:
                    best_score = val[i]
            # best_score = max(val)
    
    return best_score, goal_reached
 
# todo 
def exp_val(grid, players, food, walls, depth, goal_reached):
    if depth == 5:
        moves = get_moves(players[0], grid, walls)
        return reflex_eval(moves, players, food, goal_reached), goal_reached
    enemy1_moves = get_moves(players[1], grid, walls)
    enemy2_moves = get_moves(players[2], grid, walls)
    
    closest_dist1 = math.inf
    closest_dist2 = math.inf
    closest_pos1 = enemy1_moves[0]
    closest_pos2 = enemy2_moves[0]
    
    for i in enemy1_moves:
        dist = manhattan_distance(players[0], i)
        if dist < closest_dist1:
            rand = random.randint(1,11)
            if rand <= 4:
                closest_dist1 = dist
                closest_pos1 = i
    for i in enemy2_moves:
        dist = manhattan_distance(players[0], i)
        if dist < closest_dist2:
            rand = random.randint(1,11)
            if rand <= 4:
                closest_dist2 = dist
                closest_pos2 = i
    
    pred_players = copy.deepcopy(players)
    pred_players[1] = closest_pos1
    pred_players[2] = closest_pos2
    
    return max_val(grid, pred_players, food, walls, depth+1, goal_reached)

def moveExpectimax(grid, players, food, walls, score, goal_reached):
    # player
    player_moves = get_moves(players[0], grid, walls)
    vals, goal_reached = expectimax(grid, players, food, walls, goal_reached)
    players[0] = choose_move(player_moves, vals)
    
    score, goal_reached = check_score(grid, players, food, score, goal_reached)
    printGrid(grid, players, food, score)
    time.sleep(.1)

    # first enemy
    enemy_moves = get_moves(players[1], grid, walls)
    players[1] = enemyAgentMoveWithProb(enemy_moves, players[1], players[0])
    
    score, goal_reached = check_score(grid, players, food, score, goal_reached)
    printGrid(grid, players, food, score)
    time.sleep(.1)
    
    # second enemy
    enemy_moves = get_moves(players[2], grid, walls)
    players[2] = enemyAgentMoveWithProb(enemy_moves, players[2], players[0])
    
    score, goal_reached = check_score(grid, players, food, score, goal_reached)
    printGrid(grid, players, food, score)
    time.sleep(.1)
    
    # goal
    goal_moves = get_moves(players[3], grid, walls)
    players[3] = goal_moves[random.randint(0,len(goal_moves)-1)]
        
    score, goal_reached = check_score(grid, players, food, score, goal_reached) 
    printGrid(grid, players, food, score)
    # time.sleep(.1)
        
    return players, food, score, goal_reached