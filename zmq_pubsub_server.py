import zmq
import random
import time

context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind("tcp://*:5556")

ctr = 0
while True:
  zipcode = random.randrange(1,20000)
  temperature = random.randrange(1,215) - 80
  relhumidity = random.randrange(1,50) + 10
  socket.send("%d %d %d" % (zipcode, temperature, relhumidity))
  ctr += 1
  if ctr % 1000 == 0:
     print ctr
  #time.sleep(0.1)
