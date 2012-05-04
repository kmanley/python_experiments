import sys
import zmq

# Socket to talk to server
context = zmq.Context()
socket = context.socket(zmq.SUB)

print "Collecting updates from weather server..."
socket.connect ("tcp://localhost:5556")

# Subscribe to zipcode, default is NYC, 10001
filter = sys.argv[1] if len(sys.argv) > 1 else "10001"
socket.setsockopt(zmq.SUBSCRIBE, filter)

# Process 5 updates
total_temp = 0
for update_nbr in range (5):
  string = socket.recv()
  zipcode, temperature, relhumidity = string.split()
  print "got %s, %s, %s" % (zipcode, temperature, relhumidity)
  total_temp += int(temperature)

print "Average temperature for zipcode '%s' was %dF" % (
  filter, total_temp / update_nbr)