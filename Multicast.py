import socket
import struct
from sys import argv
import os
import thread
import time

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
    server_address = ((hostIp,10000))
    conversationList = []
    
    def __init__(self, numberOfProcess):
        self.numberOfProcess = numberOfProcess

        self.sock = self.initConnection()
        self.synchronize(self.numberOfProcess)

        self.pid_list.sort()
        self.pid = self.pid_list.index(self.pid)
        
        
        thread.start_new_thread(self.recvListener,())
        print "Ready - "+self.presentationMsg()
        print "Send your message:"
        while True:
            msg = raw_input()
            if msg[:4] == "LIST":
                self.printConversationLog()
            elif msg[:3] == "PID":
                print self.presentationMsg()     
            elif msg[:3] == "STP":
                pidStop = int(msg[4:].split("-s")[0])
                seconds = int(msg[4:].split("-s")[1])
                self.sendStopMsg(pidStop,seconds)
            else:
                self.sendMsg(msg)
        print "end"

    def presentationMsg(self):
        return "I'm the process no: "+str(self.pid)

    def printConversationLog(self):
        for i in self.conversationList:
                print i
                    
    def initConnection(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        membership = socket.inet_aton(self.multicast_ip) + socket.inet_aton(self.hostIp)

        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, membership)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

        sock.bind(self.server_address)

        return sock

    def synchronize(self,numberOfProcess):
        print '\nSynchronizing..'

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
        
    def sendStopMsg(self, pidNo, seconds):
        msg = "STP "+str(pidNo)+" -s "+str(seconds)
        self.sock.sendto(msg,self.multicast_group)

    def sendMsg(self,msg):
        self.time += 1
        msgTosend = "MSG ID:" + str(self.time) + "-" + str(self.pid) + "\r\nContent:" + msg
        #print "sended: "+msgTosend
        self.sock.sendto(msgTosend,self.multicast_group)
        

    def recvMsg(self,msg, msgId, timestamp,senderId):
        msgGuard = str(senderId) + " - Time "+str(timestamp)+": " + msg.split(":")[1] 
        self.queueMsg.put((msgId,msgGuard))
        
        self.time = 1 + max(self.time,timestamp)
        self.ackMsg(msgId)

    def ackMsg(self, msgId):
        ack = "ACK "+str(msgId) + ":" + str(self.time)
        self.time += 1
        self.sock.sendto(ack,self.multicast_group)
        
    def recvAck(self,msgId, timestamp):
        self.time = 1 + max(self.time, timestamp)
        
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

        self.conversationList.append(msg)
        print msg
        self.time +=1
        
        del self.numberAckList[msgId]

        while not (self.queueMsg.empty()):
            time , msg = self.queueMsg.get(False)
            if(self.numberAckList[time] < self.numberOfProcess):
                self.queueMsg.put((time, msg))
                break

            self.conversationList.append(msg)
            print msg
            self.time += 1
            del self.numberAckList[time]

    def recvListener(self):
        while True:

            data, address = self.sock.recvfrom(1024)
            cmd = data[:3]

            if cmd == "ACK":
                msgID = int(data.split(":")[0][4:])
                timestamp = int(data.split(":")[1])
                self.recvAck(msgID,timestamp)
                self.deliverMsg(msgID)
                

            elif cmd == "MSG":
                msgId, contentMsg =  data.split("\r\n")
                timeRecv = int(msgId[7:].split("-")[0])
                senderId = int(msgId[7:].split("-")[1])
                msgId = int("".join(msgId[7:].split("-")))
                content = str(msgId) + ": " + contentMsg[8:]
                self.recvMsg(content,msgId,timeRecv,senderId)
                
            elif cmd == "STP":
                stopPid = int(data[4:].split("-s")[0])
                seconds = int(data[4:].split("-s")[1])
                if stopPid != self.pid:
                    continue    
                print "Stopped to listen for %d seconds"%seconds
                time.sleep(seconds)
                print "Woke up"

if len(argv) <= 1:
    raise Exception("You must provide the number of process as argument!")
else:
    MulticastChat(int(argv[1]))
