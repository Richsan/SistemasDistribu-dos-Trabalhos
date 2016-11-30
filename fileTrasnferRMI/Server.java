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

import java.rmi.registry.Registry;
import java.rmi.registry.LocateRegistry;
import java.rmi.RemoteException;
import java.rmi.server.UnicastRemoteObject;
import java.io.FileOutputStream;
import java.io.File;


public class Server implements FileTransfer
{

	private String errorMsg;
	
	private FileOutputStream openFile(RemoteFileChunk file)
	{
		try{
			
			FileOutputStream fo = new FileOutputStream("serverDir"+File.separator+file.getName(),!file.isFirstChunck());

			return fo;
		}
		catch (Exception e)
		{
			this.errorMsg = e.toString();
			return null;
		}
	}
	
	public String sendFile(RemoteFileChunk file)
	{
		FileOutputStream fo = this.openFile(file);
		if(fo == null)
			return this.errorMsg;
		try{
			
			fo.write(file.getData());
			fo.close();
		}
		catch (Exception e)
		{
			return e.toString();
		}

		return "ok";
	}

	public static void main(String[] args)
	{
		try {

			LocateRegistry.createRegistry(1099);
			
			Server obj = new Server();
			FileTransfer stub = (FileTransfer) UnicastRemoteObject.exportObject(obj, 12010);

			// Bind the remote object's stub in the registry
			Registry registry = LocateRegistry.getRegistry();
			registry.bind("FileTransfer", stub);

			System.err.println("Server ready");
		}
		catch (Exception e)
		{
			System.err.println("Server exception: " + e.toString());
			e.printStackTrace();
		}
		
	}


}
