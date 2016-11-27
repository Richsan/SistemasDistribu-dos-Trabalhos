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
