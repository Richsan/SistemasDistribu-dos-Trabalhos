#define MAXNAME 1024
const MAXFILE =  4096;

typedef string filename<MAXNAME>;

typedef opaque fileContent[MAXFILE];

struct transferFile_in
{
	filename name;
	int size;
	int firstChunk;
	fileContent data;
		
};

struct transferFile_out
{
	long sucess;
};

program TRANSFERFILE_PROG
{
	version TRANSFERFILE_VERS
	{
		transferFile_out  transfer_file(transferFile_in *)=1;
	} = 1;
} = 0x31230000;
