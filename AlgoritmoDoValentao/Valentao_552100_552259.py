#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
 * Universidade Federal de São Carlos - Campus Sorocaba
 * Disciplina: Sistemas Distribuídos
 * 
 * Algoritmo do Valentão 
 *
 * Alunos: 
 * Carolina Pascale Campos            RA: 552100
 * Henrique Manoel de Lima Sebastião  RA: 552259
 *
 * Execucao: python Valentao_552100_552259.py idNo numNoListening listaDeNosAConectar
 *
 * numNoListening se refere a quantos nos o no vai esperar se conectar
 * listaDeNosAConectar se refere a uma lista de ids de nos que ja estao rodando que este no deseja se conectar 
"""

from socket import *
import time
from threading import Thread
import threading
from sys import argv

class Node:

    __connIdx = 0
    __threadLock = threading.Lock()
    __connSocket = socket(AF_INET, SOCK_STREAM)
    __bufferSize = 1026
    __clientSocket = socket(AF_INET, SOCK_STREAM)
    __running = True
    __leader = 1
    __leaderFlag = False
    
    def __init__(self, hostname,id,numNodes,idList):
        self.id = id
        self.__port = 12000+id
        self.__connSocketList = {}
        self.__numNodes = numNodes
        self.hostname = hostname
        self.connectToOthers(idList)
        t = Thread(target = self.connListener, args = (hostname,))
        t.start()
        self.msgSender()
        
    def connListener(self, hostname):
        self.__connSocket
        self.__connSocket.bind((hostname,self.__port))
        self.__connSocket.listen(1)

        while self.__numNodes > 0:
            conn, _ = self.__connSocket.accept()
            self.__connSocketList[self.__connIdx] = conn
            t = Thread(target = self.msgRecvListener, args = (conn,self.__connIdx,))
            self.__connIdx += 1
            t.start()
            self.__numNodes -= 1
            
            
    def msgSender(self):
        while self.__running:
            if self.__leader == self.id:
                print("leader")
            msg = raw_input(">")
            if msg == "CLOSE":
                self.close()
                break
            self.sendMulticastMsg(msg)

            
    def msgRecvListener(self, sock, connId):
        while self.__running:
            msg =  sock.recv(self.__bufferSize);
            if not self.__running:
                break
            self.recvMsg(msg,sock,connId)
            if msg[:4] == "QUIT":
                break;

    def recvMsg(self, msg,sock,connId):
        print("Received: " + msg)
        
        if msg[:4] == "QUIT":
            idSender = int(msg[5:])
            del self.__connSocketList[connId]
            sock.send("QUIT"+str(self.id))
            
            if idSender == self.__leader:
                t = Thread(target = self.startElection, args = ())
                t.start()

            
                
        elif msg[:2] == "OK":
            idSender = int(msg[3:])
            if self.__leaderFlag and idSender >= self.id:
                self.__leaderFlag = False

        elif msg[:8] == "ELECTION":
            idSender = int(msg[9:])
            if idSender < self.id:
                self.sendOkMsg(sock)
                if not self.__leaderFlag:
                    t = Thread(target = self.startElection,args = ())
                    t.start()
                
        elif msg[:6] == "LEADER":
            idSender = int(msg[7:])
            if idSender != self.__leader:
                self.__leader = idSender
                print("Sending: "+msg)
                self.sendMulticastMsg(msg)
        
    def sendMulticastMsg(self,msg):
        for i in self.__connSocketList:
            self.__connSocketList[i].send(msg)

    def connectToOthers(self,idlist):
        for i in idList:
            connSock = socket(AF_INET, SOCK_STREAM)
            connSock.connect((self.hostname,12000+i))
            self.__connSocketList[self.__connIdx] = connSock
            t = Thread(target = self.msgRecvListener, args = (connSock,self.__connIdx,))
            self.__connIdx += 1
            t.start()


    def sendOkMsg(self,sock):
        print("Sending: "+"OK "+str(self.id))
        sock.send("OK "+str(self.id))
        
    def close(self):
        self.sendMulticastMsg("QUIT "+str(self.id))
        self.__running = False
        self.__connSocket.close()

    def startElection(self):
        self.__leaderFlag = True
        print("Sending: "+"ELECTION "+str(self.id))
        self.sendMulticastMsg("ELECTION "+str(self.id))
        self.waitElection()
        
    def waitElection(self):
        time.sleep(2)
        if self.__leaderFlag:
            self.turnLeader()

    def turnLeader(self):
        print("Turned the leader")
        self.__leader = self.id
        print("Sending: "+"LEADER "+str(self.id))
        self.sendMulticastMsg("LEADER "+str(self.id))
        
        

if len(argv) <= 1:
    raise Exception("You must provide the id of processes as argument!")
else:
    idList = []

    for i in range(3,len(argv)):
        idList.append(int(argv[i]))
        
    Node('',int(argv[1]),int(argv[2]),idList)
