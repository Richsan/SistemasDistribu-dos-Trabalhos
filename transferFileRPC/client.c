#include <stdio.h>
#include <string.h>
#include <sys/time.h>
#include "transferFile.h"

void extractName(char *argv, char * fileName)
{
	int i,j,len;
	
	len = strlen(argv);
	
	for(i = len -1; i >=0 && argv[i] != '/'; i--);

	if(i > 0)
	{
		i++;
		for(j = 0; i < len;i++, j++)
			fileName[j] = argv[i];
		
		fileName[j] = '\0';
	}
	else
		strcpy(fileName,argv);
	
}

int main(int argc,char **argv)
{
	CLIENT *cl;
	transferFile_in in;
	transferFile_out *outp;
	FILE *file;
	int readBytes;
	char fileName[4096];
	
	struct timeval time;

	if(argc != 3)
	{
		printf("usage: client <hostname><pathFile>");
		return 1;
	}

	extractName(argv[2],fileName);

	cl = clnt_create(argv[1],TRANSFERFILE_PROG,TRANSFERFILE_VERS,"tcp");

  
	if(cl == NULL)
	{
		printf("%s",clnt_sperror(cl,argv[1]));
		return 1;
	}

	file = fopen(argv[2],"r");

	if(file == NULL)
	{
		puts("File doesn't exist");
		return 1;
	}
	
	in.name = fileName;	

	in.size = 0;
	in.firstChunk = 1;

	gettimeofday(&time, NULL);
	long inicio = ((unsigned long long)time.tv_sec * 1000000) + time.tv_usec;
	
	while(1)
	{
		in.size = fread(in.data,1,MAXFILE,file);
		outp = transfer_file_1(&in,cl);
		
		if(!(outp->sucess))
		{
			puts("Falha durante envio");
			return 1;
		}

		if(in.size < MAXFILE)
			break;
		
		in.firstChunk = 0;
	}
	
	fclose(file);

	gettimeofday(&time, NULL);
	long fim = ((unsigned long long)time.tv_sec * 1000000) + time.tv_usec;
	
	puts("Arquivo enviado com sucesso!");
	printf("Tempo de transferencia em segundos: %g\n",(double)(fim - inicio)/1000000);

	exit(0);
}
