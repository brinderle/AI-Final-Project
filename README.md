# AI-Final-Project

Most of the changes I have made have been in multiAgent.py.  Here are some of the notes I took about changes I made or wanted to make.
* increased NUM_AGENTS from 2 to 4
* initially the start positions are "P" for player, "G" for enemy, need to add start positions for the moving goal and other enemy
  * P = player, E = enemy1, F = enemy2, G = Goal
  * change parts in mazeCreator()
  * change section below GenEnemyStart(x, z) to initialize variables for positions of the agents
* add GenGoalStart(x, z) function, maybe GenEnemy2Start(x, z) also
* update XML to have the other enemy and goal agents
  * other enemy still named "Enemy"
* use enemyAgentMoveRand(ah, world_state) for the random actions of the other enemy and goal agents

I made one test layout called openClassicMulti.lay.
You will need to have 4 minecraft servers running to support the 4 agents
