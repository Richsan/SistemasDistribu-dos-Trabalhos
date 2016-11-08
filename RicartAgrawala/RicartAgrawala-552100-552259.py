#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
 * Universidade Federal de São Carlos - Campus Sorocaba
 * Disciplina: Sistemas Distribuídos
 * 
 * Exclusão Mútua Ricart & Agrawala 
 *
 * Alunos: 
 * Carolina Pascale Campos            RA: 552100
 * Henrique Manoel de Lima Sebastião  RA: 552259
 *
 * Execução: python RicartAgrawala552100-552259.py n
 *
 * onde n = numero de processos na comunicação, como consequência 
 * você terá que iniciar mais n-1 instancias do processo para
 * passar da fase de sincronização
 *
 * No nosso programa, o recurso compartilhado é a message board
 * Para um processo poder escrever algo na message board
 *  antes ele tem que fazer uma requisição de uso aceita por todos
 *  os outros processos.Portanto, só um processo por vez pode
 *  escrever na message board.
 *
 * Comandos:
 * LIST -> Vai listar todas as mensagens da message Board
 * REQ -> requisita recurso compartilhado (message Board)
 * RELEASE -> libera recurso requisitado (message board)
"""


import socket
import struct
from sys import argv
from sys import stdout
import os
import thread
import time


try:
    from Queue import PriorityQueue  # ver. < 3.0
except ImportError:
    from queue import PriorityQueue

class RicartAgrawalaSim:

    multicast_group = ('224.3.29.71',10000)
    multicast_ip = '224.3.29.71'
    hostIp = '0.0.0.0'
    pid = os.getpid()
    queueMsg = PriorityQueue()
    queueResource = PriorityQueue()
    numberAckList = {}
    oksNumberReceived = 0
    pid_list = [pid]
    time = 0
    server_address = ((hostIp,10000))
    msgBoard = []
    usingResource = False
    requestedResource = False

    
    
    def __init__(self, numberOfProcesses):

        self.numberOfProcesses = numberOfProcesses

        self.sock = self.initConnection()
        self.synchronize(self.numberOfProcesses)

        self.pid_list.sort()
        self.pid = self.pid_list.index(self.pid)
        
        
        thread.start_new_thread(self.recvListener,())

        print "Ready - "+self.presentationMsg()
        print "Send your command:"

        while True:
            msg = raw_input()
            if   msg[:3] == "PID":
                print self.presentationMsg()

            elif msg[:4] == "LIST":
                self.printMsgBoard()
                
            elif msg[:3] == "REQ":
                self.sendRequestMsg()

                
    def presentationMsg(self):
        
        return "I'm the process no. "+str(self.pid)

    
    def printMsgBoard(self):

        for i in self.msgBoard:
            print i

            
    def getResource(self):
        
        self.usingResource = True
        self.requestedResource = False
        
        while True:
            print "\rResource is yours, send messages:"
            msg = raw_input(">")

            if msg == "RELEASE":
                self.releaseResource()
                break
            else:
                self.sendMsg(msg);


    def releaseResource(self):

        self.usingResource = False;
        print "\rReleasing resource.."
        while not (self.queueResource.empty()):
            time , msgID = self.queueResource.get(False)
            self.sendOkMsg(msgID)
        print "\rResource released"


    def sendRequestMsg(self):

        self.time += 1
        reqMsg = "REQ "+str(self.time) + "-" + str(self.pid)

        self.requestedResource = True
        self.sock.sendto(reqMsg,self.multicast_group)

        print("Waiting for answers about request...")

        while not self.usingResource:
            pass

        self.getResource()
        
    def initConnection(self):

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        membership = socket.inet_aton( self.multicast_ip)
        membership += socket.inet_aton(self.hostIp)

        sock.setsockopt( socket.IPPROTO_IP,
                         socket.IP_ADD_MEMBERSHIP,
                         membership )

        sock.setsockopt( socket.SOL_SOCKET,
                         socket.SO_REUSEPORT,
                         1 )

        sock.bind(self.server_address)

        return sock

    
    def synchronize(self,numberOfProcesses):

        print '\nSynchronizing..'

        #print 'Recv %s'%self.pid
        synchroMsg = 'SYN '+ str(self.pid)
    
        while len(self.pid_list) < self.numberOfProcesses:
            self.sock.sendto( synchroMsg, self.multicast_group )
            
            data, address = self.sock.recvfrom(1024)  
            pidRecv = int(data[4:])

            if not (pidRecv in self.pid_list):
                self.pid_list.append(pidRecv)
                #print 'Recv %s'%data
            
            self.sock.sendto(synchroMsg,self.multicast_group)


    def sendMsg(self,msg):

        self.time += 1
        msgTosend = "MSG ID:" + str(self.time) + "-" + str(self.pid) + "\r\nContent:" + msg
        #print "sended: "+msgTosend
            
        self.sock.sendto(msgTosend,self.multicast_group)
        

    def deliverMsg(self, msgId):
        
        if self.numberAckList[msgId] < self.numberOfProcesses:
            return

        time , msg = self.queueMsg.get(False)

        if time != msgId:
            self.queueMsg.put((time,msg))
            return

        self.msgBoard.append(msg)
        print('\r'+msg)
        self.time +=1
        
        del self.numberAckList[msgId]

        while not (self.queueMsg.empty()):
            time , msg = self.queueMsg.get(False)
            if(self.numberAckList[time] < self.numberOfProcesses):
                self.queueMsg.put((time, msg))
                break

            self.msgBoard.append(msg)
            print('\r'+msg)
            self.time += 1
            del self.numberAckList[time]
    

    def recvMsg(self,msg, msgId, timestamp,senderId):

        msgGuard = str(senderId) + " - Time "+str(timestamp)+": " + msg.split(":")[1] 
        self.queueMsg.put((msgId,msgGuard))
        
        self.time = 1 + max(self.time,timestamp)
        self.sendAckMsg(msgId)


    def sendAckMsg(self, msgId):

        self.time += 1
        ack = "ACK "+str(msgId) + ":" + str(self.time)
        self.sock.sendto(ack,self.multicast_group)

        
    def recvAck(self,msgId, timestamp):
        
        self.time = 1 + max(self.time, timestamp)
        
        if msgId in self.numberAckList:
            self.numberAckList[msgId] += 1
        else:
            self.numberAckList[msgId] = 1

    def sendOkMsg(self, msgId):

        self.time += 1
        okMsg = "OK "+ msgId + ":" + str(self.time)+"-"+str(self.pid);
        self.sock.sendto(okMsg,self.multicast_group)

    def sendNOkMsg(self, msgId):

        self.time += 1
        nokMsg = "NOK "+ msgId + ":" + str(self.time)+"-"+str(self.pid)
        self.sock.sendto(nokMsg,self.multicast_group)

            
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

            elif cmd == "REQ":
                msgID = data[4:]
                timestamp = int(data[4:].split("-")[0])
                ok = False
                
                if self.requestedResource:
                    if self.time >= timestamp:
                        ok = True

                    else:
                        self.queueResource.put((timestamp,msgID))
                        ok = False

                elif not self.usingResource:
                    ok = True

                else:
                    self.queueResource.put((timestamp,msgID))
                    ok = False

                self.time = 1 + max(self.time, timestamp)
                if ok:
                    self.sendOkMsg(msgID)
                else:
                    self.sendNOkMsg(msgID)

                    
            elif data[:2] == "OK":
                idDest = int(data[3:].split(":")[0].split("-")[1])
                timestamp = int(data[3:].split(":")[1].split("-")[0])
                idSend = int(data[3:].split(":")[1].split("-")[1])
            
                self.time = 1 + max(self.time, timestamp)

                if self.requestedResource and idDest == self.pid:
                    print "Received OK from pid "+str(idSend)
                    self.oksNumberReceived += 1
                    if self.oksNumberReceived == self.numberOfProcesses:
                        self.usingResource = True
                        self.requestedResource = False
                        self.pidUsingResource = -1
                        self.resourceBusy = False
                        self.oksNumberReceived = 0

            elif cmd == "NOK":
                idDest = int(data[4:].split(":")[0].split("-")[1])
                timestamp = int(data[4:].split(":")[1].split("-")[0])
                idSend = int(data[4:].split(":")[1].split("-")[1])
                
                self.time = 1 + max(self.time, timestamp)
                
                if idDest == self.pid:
                    print "Receveid NOK from pid "+str(idSend)
                    self.resourceBusy = True
                    self.pidUsingResource = idSend
                    
if len(argv) <= 1:
    raise Exception("You must provide the number of processes as argument!")
else:
    RicartAgrawalaSim(int(argv[1]))
