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
		
		try {
			Registry registry = LocateRegistry.getRegistry(host);
			FileTransfer stub = (FileTransfer) registry.lookup("FileTransfer");
						
			FileInputStream fi = new FileInputStream(fileName);

			
			byte[] buffer = new byte[4096];
			RemoteFileChunk remoteFileChunk = new RemoteFileChunk(fileName,true);
			String response;

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
			System.out.println("Arquivo enviado com sucesso!");
		}
		catch (Exception e)
		{
			System.err.println("Client exception: " + e.toString());
			e.printStackTrace();
		}
	}
}
