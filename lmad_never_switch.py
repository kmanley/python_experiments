# test
import random
trials = int(raw_input("how many trials? ").strip())
wins = 0
for i in range(trials):
    prize_door = random.randrange(3)
    choice = random.randrange(3)
    temp = range(3)
    random.shuffle(temp)
    for index in temp:
        if index != choice and index != prize_door:
            removed_door = index
            break
    #print 'prize door %s' % prize_door
    #print 'choice %s' % choice
    #print 'removed door %s' % removed_door
    if choice == prize_door:
        #print 'win!'
        wins += 1
    else:
        pass
        #print 'loss'
    #print '-' * 40        
print "%.2f%% chance of winning" % (wins / float(trials) * 100.0)

        
    
    