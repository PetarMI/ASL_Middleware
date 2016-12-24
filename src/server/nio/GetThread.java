package server.nio;

import java.io.IOException;
import java.net.InetSocketAddress;
import java.nio.ByteBuffer;
import java.nio.channels.SocketChannel;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.LinkedBlockingQueue;
import java.util.concurrent.RejectedExecutionException;
import java.util.logging.FileHandler;
import java.util.logging.Level;
import java.util.logging.Logger;

public class GetThread implements Runnable {	
	//Logging stuff
	private final int qmID;
	private final int tID;
	private int counter = 0;
	
	private String serverIP;
	private int port;
	
	private BlockingQueue<MiddlewareDataEvent> getQueue;
	
	// The event that has to be processes
	private MiddlewareDataEvent event;
	
	private SocketChannel socket;
	private ByteBuffer readBuffer;
	
	public GetThread(int qmid, int tid, BlockingQueue<MiddlewareDataEvent> getQueue, String ip, int port) 
			throws IOException {
		this.qmID = qmid;
		this.tID = tid;
		this.getQueue = getQueue;
		
		this.serverIP = ip;
		this.port = port;
		
		this.readBuffer = ByteBuffer.allocate(2048);
		
		this.initConnection();
	}
	
	@Override
	public void run() {
		
		while(true) {
			try {
				// Wait for an event to become available
				this.event = this.getQueue.take();
				this.event.stopQueueTime();
				
				//Logging
				if (++this.counter == 100) {
					System.out.println(this.toString());
					this.counter = 0;
				}

				this.write();
				byte[] responseData = this.read();

				this.handleResponse(responseData);
				
			} catch (IOException e) {
				e.printStackTrace();
			}catch (InterruptedException ie) {
				ie.printStackTrace();
			} 
		}
	}
	
	private byte[] read() throws IOException {
		this.readBuffer.clear();
		
		int bytesRead = this.socket.read(this.readBuffer);
		
		if (bytesRead == -1) {
			System.err.println("Memchached closed connection");
			this.socket.close();
		}
		
		this.event.stopServerTime();
		
		byte[] dataCopy = new byte[bytesRead];
		System.arraycopy(this.readBuffer.array(), 0, dataCopy, 0, bytesRead);
		return dataCopy;
	}
	
	//initiates sending data back to memaslap client
	private void handleResponse(byte[] data) {
		this.event.responseData = data;
		// Return to sender
		this.event.startReturnEnqueueTime();
	    this.event.server.send(this.event);
	}
	
	private void write() throws IOException {
		ByteBuffer buf = ByteBuffer.wrap(this.event.requestData);
		//TODO is there anything more to writing a buffer
		this.event.startServerTime();
		while (buf.hasRemaining()) {
			this.socket.write(buf);
		}
	}
	
	private void initConnection() throws IOException {
	    // Create a socket channel
	    this.socket = SocketChannel.open();
	    this.socket.configureBlocking(true);
	  
	    // Establish connection to memcached
	    try {
	    	this.socket.connect(new InetSocketAddress(this.serverIP, this.port));
	    } catch (Exception e) {
	    	System.err.println(this.serverIP + ":" + this.port);
	    	e.printStackTrace();
	    }
	    
	}
	
	@Override
	public String toString() {
		return String.format("%d,%d,%d,%d", 0, this.qmID, this.tID, this.getQueue.size());
	}
}
