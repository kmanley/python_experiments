#!/usr/bin/env python

import socket
import binascii

def main():
  MCAST_GRP = '224.1.1.1' 
  MCAST_PORT = 5007
  sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
  sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32) 
  sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 1)

  #sock.bind((MCAST_GRP, MCAST_PORT))
  sock.bind(('', MCAST_PORT))
  host = socket.gethostbyname(socket.gethostname())
  sock.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_IF, socket.inet_aton(host))
  sock.setsockopt(socket.SOL_IP, socket.IP_ADD_MEMBERSHIP, 
                  socket.inet_aton(MCAST_GRP) + socket.inet_aton(host))

  while 1:
    try:
      data, addr = sock.recvfrom(1024)
    except socket.error, e:
      print 'Expection'
    #hexdata = binascii.hexlify(data)
    #print 'Data = %s' % hexdata
    print data

if __name__ == '__main__':
  main()
