import socket
import struct
import sys
import os
import thread

try:
        from Queue import PriorityQueue  # ver. < 3.0
except ImportError:
        from queue import PriorityQueue


class MulticastChat:
    
    multicast_group = ('224.3.29.71',10000)
    multicast_ip = '224.3.29.71'
    hostIp = '0.0.0.0'
    pid = os.getpid()
    queueMsg = PriorityQueue()
    numberAckList = {}
    pid_list = [pid]
    time = 0
    numberOfProcess = 3
    server_address = ((hostIp,10000))
    
    def __init__(self):
        self.sock = self.initConnection()
        self.synchronize(self.numberOfProcess)

        self.pid_list.sort()
        time = self.pid_list.index(self.pid)
        thread.start_new_thread(self.recvListener,())
        print "Ready - Digite sua msg:"
        while True:
                msg = raw_input()
                self.sendMsg(msg)
        print "end"

    
    def initConnection(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        membership = socket.inet_aton(self.multicast_ip) + socket.inet_aton(self.hostIp)

        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, membership)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        sock.bind(self.server_address)

        return sock

    def synchronize(self,numberOfProcess):
        print '\nSincronizing..'

        #print 'Recv %s'%self.pid
        synchroMsg = 'SYN '+ str(self.pid)
    
        while len(self.pid_list) < self.numberOfProcess:
            self.sock.sendto(synchroMsg,self.multicast_group)
            data, address = self.sock.recvfrom(1024)  
            pidRecv = int(data[4:])

            if not (pidRecv in self.pid_list):
                self.pid_list.append(pidRecv)
                #print 'Recv %s'%data
            
            self.sock.sendto(synchroMsg,self.multicast_group)

            

    def sendMsg(self,msg):
        msgTosend = "MSG ID:" + str(self.time) + "-" + str(self.pid) + "\r\nContent:" + msg
        #print "sended: "+msgTosend
        self.sock.sendto(msgTosend,self.multicast_group)
        

    def recvMsg(self,msg, msgId, timeRecv):
        self.queueMsg.put((msgId,msg))
        
        self.time = 1 + max(self.time,timeRecv)
        self.ackMsg(msgId)

    def ackMsg(self, msgId):
        ack = "ACK "+str(msgId)
        self.sock.sendto(ack,self.multicast_group)
        
    def recvAck(self,msgId):
        if msgId in self.numberAckList:
            self.numberAckList[msgId] += 1
        else:
            self.numberAckList[msgId] = 1

    def deliverMsg(self, msgId):
        
        if self.numberAckList[msgId] < self.numberOfProcess:
            return

        time , msg = self.queueMsg.get(False)

        if time != msgId:
            self.queueMsg.put((time,msg))
            return

        print msg

        del self.numberAckList[msgId]

        while not (self.queueMsg.empty()):
            time , msg = self.queueMsg.get(False)
            if(self.numberAckList[time] < self.numberOfProcess):
                self.queueMsg.put((time, msg))
                break

            print msg

            del self.numberAckList[time]

    def recvListener(self):
        while True:
            data, address = self.sock.recvfrom(1024)
            cmd = data[:3]

            if cmd == "ACK":
                msgID = int(data[4:])
                self.recvAck(msgID)
                self.deliverMsg(msgID)
                

            elif cmd == "MSG":
                msgId, contentMsg =  data.split("\r\n")
                timeRecv = int(msgId[7:].split("-")[0])
                msgId = int("".join(msgId[7:].split("-")))
                content = str(msgId) + ": " + contentMsg[8:]
                self.recvMsg(content,msgId,timeRecv)
                

        
MulticastChat()
