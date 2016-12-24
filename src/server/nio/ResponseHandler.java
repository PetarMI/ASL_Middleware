package server.nio;

import java.nio.channels.SocketChannel;

public class ResponseHandler {

	private HashingServer server;
	private SocketChannel socket;
	
	public ResponseHandler() {
		
	}
	
	public ResponseHandler(HashingServer server, SocketChannel socket) {
		this.configureHandler(server, socket);
	}
	
	//initiates sending data back to memaslap client
	public void handleResponse(byte[] data) {
		// Return to sender
	    //this.server.send(this.socket, data);
	}
	
	public void configureHandler(HashingServer server, SocketChannel socket) {
		this.server = server;
		this.socket = socket;
	}
}
