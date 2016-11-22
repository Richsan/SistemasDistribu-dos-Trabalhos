#include<stdio.h>
#include<string.h>
#include "transferFile.h"

transferFile_out * transfer_file_1_svc(transferFile_in *inp, struct svc_req * rqstp)
{
	static transferFile_out out;
	
	FILE *file;
	char path[4096] = "";

	strcat(path,"serverDir/");
	strcat(path,inp->name);
	
	if(inp->firstChunk)
		file = fopen(path,"w");
	else
		file = fopen(path,"a");

	if(file == NULL)
	{
		out.sucess = 0;
		return &out;
	}

	fwrite(inp->data,1,inp->size,file);
	
	fclose(file);
	
	out.sucess = 1;
	return &out;
}
