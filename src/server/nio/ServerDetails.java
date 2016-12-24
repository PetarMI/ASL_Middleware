package server.nio;

/**
 * @author petar
 * Auxiliary class to store the info pair for a memcached server
 */

public class ServerDetails {
	
	private String serverIP;
	private int serverPort;
	
	public ServerDetails(String serverIP, int port) {
		this.serverIP = serverIP;
		this.serverPort = port;
	}

	public String getIP() {
		return this.serverIP;
	}
	
	public int getPort() {
		return this.serverPort;
	}
}
