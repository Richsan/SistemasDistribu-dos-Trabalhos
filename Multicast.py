import socket
import struct
import sys
import os

multicast_group = ('224.3.29.71',10000)
multicast_ip = '224.3.29.71'
pid = os.getpid()
queue = []
pid_list = [pid]

def initConnection():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    membership = socket.inet_aton(multicast_ip) + socket.inet_aton('0.0.0.0')

    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, membership)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server_address = (('0.0.0.0',10000))

    sock.bind(server_address)

    return sock


sock = initConnection()

print >>sys.stderr, '\nSincronizing..'

print >>sys.stderr , 'Recv %s'%pid
msg = 'ACK '+str(pid)

while len(pid_list) < 3:
    sock.sendto(msg,multicast_group)
    data, address = sock.recvfrom(1024)  
    pidRecv = data[4:]

    if not (int(pidRecv) in pid_list):
        pid_list.append(int(pidRecv))
        print >>sys.stderr , 'Recv %s'%data
        
    sock.sendto(msg,multicast_group)

pid_list.sort()
tempo = pid_list.index(pid)

print "end"
