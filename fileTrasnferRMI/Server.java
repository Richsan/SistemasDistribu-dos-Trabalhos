import java.rmi.registry.Registry;
import java.rmi.registry.LocateRegistry;
import java.rmi.RemoteException;
import java.rmi.server.UnicastRemoteObject;
import java.io.FileOutputStream;


public class Server implements FileTransfer
{

	private String errorMsg;
	
	private FileOutputStream openFile(RemoteFileChunk file)
	{
		try{
			
			FileOutputStream fo = new FileOutputStream("serverDir/"+file.getName(),!file.isFirstChunck());

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
			FileTransfer stub = (FileTransfer) UnicastRemoteObject.exportObject(obj, 0);

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
