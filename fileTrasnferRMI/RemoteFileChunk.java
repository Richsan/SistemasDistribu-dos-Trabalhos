/*
* Universidade Federal de São Carlos - Campus Sorocaba
 * Disciplina: Sistemas Distribuídos
 * 
 * Upload de Arquivo com RMI
 *
 * Alunos: 
 * Carolina Pascale Campos            RA: 552100
 * Henrique Manoel de Lima Sebastião  RA: 552259
 *
 * Compilação: javac FileTransfer.java RemoteFileChunk.java Server.java Client.java
 *
 * Execução (Servidor Windows): java Server 
 * Execução (Cliente): java Client host arquivo
 * OBS: Garanta que antes de executar o servidor, exista um diretório 
 *		chamado "serverDir" na mesma pasta que o Server.class
*/

import java.io.Serializable;

public class RemoteFileChunk implements Serializable
{

	
	public RemoteFileChunk(String fileName)
	{
		this.firstChunk = false;
		this.name = fileName;
	}

	public RemoteFileChunk(String fileName,boolean firstChunk)
	{
		this.firstChunk = firstChunk;
		this.name = fileName;
	}

	public byte[] getData()
	{
		return this.data;
	}
	public void setData(byte[] data)
	{
		this.data = data;
	}

	public boolean isFirstChunck()
	{
		return this.firstChunk;
	}

	public void setFirstChunk(boolean firstChunk)
	{
		this.firstChunk = firstChunk;
	}

	public String getName()
	{
		return this.name;
	}
	
	private byte[] data;
	private boolean firstChunk;
	private String name;
}
