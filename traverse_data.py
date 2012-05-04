import sys
import json
import ujson
import pprint

class mylist(list):
    pass

l = [1,2,3, [100,200,300]]

def traverse(o):
    if type(o) == list:
        newobj = mylist()
        for item in o:
            newobj.append(traverse(item))
        return newobj
    elif type(o) == int:
        return o

#class MyDecoder(json.JSONDecoder):
#    def decode(self, s):
#        print "DECODE: >%s<" % s
#        #s2 = s.replace("[", "mylist([").replace("]", "])")
#        return json.JSONDecoder.decode(self, s)
#        #print "DECODE: >%s<" % s
#        #return []
#    #def raw_decode(self, s):
#    #    print "DECODE: >%s<" % s
#    #    return (1,2)
#
#j = ujson.encode(l)
#print json.loads(j, cls=MyDecoder)
#
#

print type(l)
print type(l[3])

o2 = traverse(l)
print type(o2)
print type(o2[3])

pprint.pprint(o2)