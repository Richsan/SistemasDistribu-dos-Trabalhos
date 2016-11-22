#!/bin/sh

rpcgen -C transferFile.x

cc -c client.c -o client.o
cc -c transferFile_clnt.c -o transferFile_clnt.o
cc -c transferFile_xdr.c -o transferFile_xdr.o
cc -o client client.o transferFile_clnt.o transferFile_xdr.o -lnsl
cc -c server.c -o server.o
cc -c transferFile_svc.c -o transferFile_svc.o
cc -o server server.o transferFile_svc.o transferFile_xdr.o -lnsl
rm *.o
rm -f transferFile_xdr.c transferFile_svc.c transferFile.h transferFile_clnt.c

