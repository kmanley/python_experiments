"""
Conclusions: blosc doesn't seem to compress very well, though it is fast
"""
import sys, blosc, hashlib, random, zlib, sys, cPickle, base64, bz2
from bw.util.decorators import timed

D = {}

NUMKEYS = 100000

for i in range(NUMKEYS):
  D[hashlib.md5(str(i)).hexdigest()] = hashlib.md5(str(random.randrange(1000000))).hexdigest() + hashlib.md5(str(random.randrange(1000000))).hexdigest() + hashlib.md5(str(random.randrange(1000000))).hexdigest() + hashlib.md5(str(random.randrange(1000000))).hexdigest()

#print D
#sys.exit(0)

#data = base64.encodestring(cPickle.dumps(D, protocol=2))
data = cPickle.dumps(D, protocol=2)
datalen = float(len(data))
print "datalen: %s" % int(datalen)

@timed
def test_zlib():
   c = zlib.compress(data)
   print "zlib compressed len: %s" % len(c)
   print "zlib ratio: %s" % (datalen / len(c))
   return c

@timed
def test_bz2():
    c = bz2.compress(data)
    print "bz2 compressed len: %s" % len(c)
    print "bz2 ratio: %s" % (datalen / len(c))
    return c

@timed
def test_blosc():
   c = blosc.compress(data, typesize=1, clevel=9, shuffle=False) #True)
   print "blosc compressed len: %s" % len(c)
   print "blosc ratio: %s" % (datalen / len(c))
   return c

zc = test_zlib()
print "-" * 80
b2 = test_bz2()
print "-" * 80
bc = test_blosc()
print "-" * 80

assert zlib.decompress(zc) == data
assert bz2.decompress(b2) == data
assert blosc.decompress(bc) == data

