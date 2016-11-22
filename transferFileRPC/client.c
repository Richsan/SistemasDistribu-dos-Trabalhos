#include <stdio.h>
#include <string.h>
#include "transferFile.h"

int main(int argc,char **argv)
{
	CLIENT *cl;
	transferFile_in in;
	transferFile_out *outp;
	FILE *file;
	int readBytes;


	if(argc != 3)
	{
		printf("usage: client <hostname><pathFile>");
		return 1;
	}

	cl = clnt_create(argv[1],TRANSFERFILE_PROG,TRANSFERFILE_VERS,"tcp");

  
	if(cl == NULL)
	{
		printf("%s",clnt_sperror(cl,argv[1]));
		return 1;
	}

	file = fopen(argv[2],"r");
	
	in.name = argv[2];	

	in.size = 0;
	in.firstChunk = 1;
	while(1)
	{
		in.size = fread(in.data,1,MAXFILE,file);
		outp = transfer_file_1(&in,cl);
		
		if(!(outp->sucess))
		{
			printf("Deu ruin");
			return 1;
		}

		if(in.size < MAXFILE)
			break;
		
		in.firstChunk = 0;
	}	
	fclose(file);

	printf("Arquivo enviado com sucesso!\n");

	exit(0);
}
