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

    multicast_group = ('224.3.29.71',10000)
    multicast_ip = '224.3.29.71'
    hostIp = '0.0.0.0'
    server_address = ((hostIp,10000))
    __bufferSize = 1026
    __running = True
    __leader = 1
    __leaderFlag = False
    
    def __init__(self, hostname,id):
        self.id = id
        self.sock = socket(AF_INET, SOCK_DGRAM)

        membership = inet_aton(self.multicast_ip) + inet_aton(self.hostIp)
                
        self.sock.setsockopt(IPPROTO_IP, IP_ADD_MEMBERSHIP, membership)
        self.sock.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)

        self.sock.bind(self.server_address)
        t = Thread(target = self.msgRecvListener, args = ())
        t.start()
        
        self.msgSender()
        
            
            
    def msgSender(self):
        while self.__running:
            if self.__leader == self.id:
                msg = raw_input("leader>")
            else:
                msg = raw_input(">")
                
            if msg == "CLOSE":
                self.close()
                break
            self.sendMulticastMsg(msg)

            
    def msgRecvListener(self):
        while self.__running:
            msg, _ =  self.sock.recvfrom(self.__bufferSize);
            if not self.__running:
                break
            self.recvMsg(msg)
            

    def recvMsg(self, msg):
                
        if msg[:4] == "QUIT":
            idSender = int(msg[5:])
            if idSender != self.id:
                print("Received: " + msg)
                
            if idSender == self.__leader:
                t = Thread(target = self.startElection, args = ())
                t.start()
                        
        elif msg[:2] == "OK":
            idSender = int(msg[3:])

            if(idSender > self.id):
                print("Received: " + msg)
            
            if self.__leaderFlag and idSender > self.id:
                self.__leaderFlag = False

        elif msg[:8] == "ELECTION":
            idSender = int(msg[9:])

            if idSender < self.id:
                print("Received: " + msg)
                self.sendOkMsg()
                if not self.__leaderFlag:
                    t = Thread(target = self.startElection,args = ())
                    t.start()
                
        elif msg[:6] == "LEADER":
            idSender = int(msg[7:])

            if idSender != self.id:
                print("Received: " + msg)

            
            if idSender != self.__leader:
                self.__leader = idSender

        else:
            print("Received: " + msg)
                
    def sendMulticastMsg(self,msg):
        self.sock.sendto(msg,self.multicast_group)
    

    def sendOkMsg(self):
        print("Sending: "+"OK "+str(self.id))
        self.sendMulticastMsg("OK "+str(self.id))
        
    def close(self):
        self.__running = False
        self.sendMulticastMsg("QUIT "+str(self.id))
        


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
    
    Node('',int(argv[1]))
