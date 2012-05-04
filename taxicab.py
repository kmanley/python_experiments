import pprint
N = 100
X = {}
results = []

for i in range(1, N):
    for j in range(i+1, N):
        product = i**3 + j**3
        X.setdefault(product, []).append((i,j))
        if len(X[product]) == 2:
            #print "%d: %s" % (product, X[product])
            results.append((product, X[product]))
results.sort()
pprint.pprint(results)

#import sys
#N = 20000
#X = {}
#T = 4
#
#for i in range(1, N):
#    for j in range(i+1, N):
#        product = i**3 + j**3
#        X.setdefault(product, []).append((i,j))
#        if len(X[product]) == T:
#            print "%d: %s" % (product, X[product])
#            sys.exit(0)

