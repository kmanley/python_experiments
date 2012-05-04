import timeit
#from time import clock
import random
'''
Created on Apr 17, 2012

@author: adrian.czebiniak
'''

N = 10000
glist = range(N)
random.shuffle(glist)
expected = sorted(glist)

def quick_sort(lst):
    if len(lst) <= 1:
        return lst
    else:
        pivot = lst.pop(-1)
        
        left_list = [x for x in lst if x < pivot]
        right_list = [x for x in lst if x >= pivot]

        return quick_sort(left_list) + [pivot] + quick_sort(right_list)
    
def quick_sort_test():
    actual = quick_sort(glist[::])
    assert actual == expected
    return actual    

def merge_sort(lst):
    if len(lst) <= 1:
        return lst
    else:
        middle_index = int(len(lst) / 2) 
        
        left_list = merge_sort(lst[0:middle_index])
        right_list = merge_sort(lst[middle_index:])

        new_list = []
        while len(left_list) > 0:
            if len(right_list) > 0:
                if left_list[0] < right_list[0]:
                    new_list.append(left_list.pop(0))
                else:
                    new_list.append(right_list.pop(0))
            else:
                new_list.append(left_list.pop(0))
                
        new_list += right_list
        
        return new_list
    
def merge_sort_test():
    actual = merge_sort(glist[::])
    assert actual == expected
    return actual    
    
def verify_sorted(sorted_list):
    for i in range(1, len(sorted_list)):
        if sorted_list[i-1] > sorted_list[i]:
            print "List is NOT sorted!"
            return False
    return True

if __name__ == '__main__':
    ITERS = 10
    print "quicksort: %.5f secs/call" % (timeit.timeit("quick_sort_test()", "from __main__ import quick_sort_test", number=ITERS) / float(ITERS))
    print "mergesort: %.5f secs/call" % (timeit.timeit("merge_sort_test()", "from __main__ import merge_sort_test", number=ITERS) / float(ITERS))
    
    