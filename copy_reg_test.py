#import copy_reg
import pickle, types
import StringIO

def foo():
    print "FOO CALLED!!"

from pickle import Pickler
dispatch = Pickler.dispatch.copy()
dispatch[list] = foo

#
# register a pickle handler for file objects

def unpickler(position, data):
    print "unpickler called!!"
    #file = StringIO.StringIO(data)
    #file.seek(position)
    #return file

def pickler(code):
    print "pickler called!"
    #position = file.tell()
    #file.seek(0)
    #data = file.read()
    #file.seek(position)
    #return file_unpickler, (position, data)

#copy_reg.pickle(list, pickler, unpickler)

l = [1,2,3]
pickle.dumps(l)

#class mylist(list): pass

#l = mylist([1,2,3])

#print pickle.dumps(l)
