import java.rmi.Remote;
import java.rmi.RemoteException;

public interface FileTransfer extends Remote {

	String sendFile(RemoteFileChunk file) throws RemoteException;

}
