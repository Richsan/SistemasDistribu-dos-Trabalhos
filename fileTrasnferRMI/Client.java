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

import java.rmi.registry.LocateRegistry;
import java.rmi.registry.Registry;
import java.io.FileInputStream;

public class Client {

	
	public static void main(String[] args) {

		if (args.length < 2)
		{
			System.err.println("Voce deve passar o host e o nome do arquivo como argumento!");
			return;
		}
		
		String host = args[0];
		String fileName = args[1];

		System.out.println(host);
		
		try {
			Registry registry = LocateRegistry.getRegistry(host);
			FileTransfer stub = (FileTransfer) registry.lookup("FileTransfer");
						
			FileInputStream fi = new FileInputStream(fileName);

			
			byte[] buffer = new byte[4096];
			RemoteFileChunk remoteFileChunk = new RemoteFileChunk(fileName,true);
			String response;
			

			// Get current time
			long start = System.currentTimeMillis();

			while(fi.read(buffer) > 0)
			{
				remoteFileChunk.setData(buffer);

				response = stub.sendFile(remoteFileChunk);

				if(!response.equals("ok"))
				{
					System.out.println("Error: " + response);
					fi.close();
					return;
				}
				remoteFileChunk.setFirstChunk(false);
			}
			
			fi.close();
			// Get elapsed time in milliseconds
			long elapsedTimeMillis = System.currentTimeMillis()-start;

			// Get elapsed time in seconds
			float elapsedTimeSec = elapsedTimeMillis/1000F;

			System.out.println("Arquivo enviado com sucesso!");
			System.out.println("Tempo de Envio: "+String.format( "%.2f",elapsedTimeSec)+" seconds");
		}
		catch (Exception e)
		{
			System.err.println("Client exception: " + e.toString());
			e.printStackTrace();
		}
	}
}
