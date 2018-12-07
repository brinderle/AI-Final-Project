total = 0
count = 0
f = open("25x25MazeReflexResults.txt", "r")
for i in range(100):
    score = float(f.readline().strip())
    #print(score)
    total += score
f.close()
total = total/100
string = "Avg score over 100 tests: "+str(total)
q = open("25x25MazeReflexResults.txt", "a")
q.write(string)
q.close()