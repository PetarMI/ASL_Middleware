package server.nio;

import java.io.IOException;
import java.net.InetSocketAddress;
import java.nio.ByteBuffer;
import java.nio.channels.*;
import java.nio.channels.spi.SelectorProvider;
import java.util.HashMap;
import java.util.Iterator;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.logging.FileHandler;
import java.util.logging.Level;
import java.util.logging.Logger;

public class HashingServer implements Runnable {
	
	public static final String VERSION = "2.0.0";
	
	//Logging stuff
	private Logger logger = Logger.getLogger(MiddlewareDataEvent.class.getName());	
	private int getCounter = 0;
	private int setCounter = 0;
	FileHandler fh;
	
	//First get all necessary parameters
	//The IP address and port on which the server will operate
	private String middlewareIP;
	private int port;
	
	//Server channel on which connection will be accepted from Clients
	private ServerSocketChannel serverChannel;
	
	//Selector to handle all channels in a single thread
	private Selector selector;
	
	//Buffer in which all data from a channel is read
	private ByteBuffer readBuffer = ByteBuffer.allocate(2048);
	
	//Class that processes each incoming read/write request
	private RequestHandler requestHandler;
	
	//Keep a list of all channels whose interest has to change
	private List<ChangeRequest> pendingChanges;
	
	//TODO should it be synchronized 
	//Keep track of what data should be written to which channel
	Map<SocketChannel, MiddlewareDataEvent> pendingData;
	
	public HashingServer(String address, int port, List<String> memcAddresses,
			int numThreadsPTP, int replication) throws IOException {
		
		//Parameter assignment
		this.middlewareIP = address;
		this.port = port;
		
		//Services setup
		this.selector = initSelector();
		this.requestHandler = new RequestHandler(memcAddresses, numThreadsPTP, replication);
		this.pendingChanges = new LinkedList<ChangeRequest>();
		this.pendingData = new HashMap<SocketChannel, MiddlewareDataEvent>();
		
		//configure Logger
		logger.setUseParentHandlers(false);
		this.logger.setLevel(Level.INFO);
		this.fh = new FileHandler("RequestLog.log");
		fh.setFormatter(new EventFormatter());
		this.logger.addHandler(fh);
		
		//Log info about parameters
		logger.info(String.format("Servers: %d | Threads: %d | Replication: %d", 
				memcAddresses.size(), numThreadsPTP, replication));
	}
	
	public void send(MiddlewareDataEvent event) {
		synchronized (this.pendingChanges) {
			// Set this channel to be interested in writing
			this.pendingChanges.add(new ChangeRequest(event.socket, ChangeRequest.CHANGEOPS, SelectionKey.OP_WRITE));
	      
			// add the data that has to be written to the queue for the channel
			synchronized (this.pendingData) {
				this.pendingData.put(event.socket, event);
				event.stopReturnEnqueueTime();
				event.startReturnQueueTime();
			}
	    }
	    
	    // Finally, wake up our selecting thread so it can make the required changes
	    this.selector.wakeup();
	}
	
	public void run() {
		
		System.out.println(VERSION);
		
		while (true) {
			try {
				// Process all pending changes
		        synchronized(this.pendingChanges) {
		        	Iterator<ChangeRequest> changes = this.pendingChanges.iterator();
		        	while (changes.hasNext()) {
		        		ChangeRequest change = (ChangeRequest) changes.next();
		        		switch(change.type) {
		        		case ChangeRequest.CHANGEOPS:
		        			SelectionKey key = change.socket.keyFor(this.selector);
		        			key.interestOps(change.ops);
		        		}
		        	}
		        	this.pendingChanges.clear();
		        }
		        
				//Wait for an event on one of the registered channels
				this.selector.select();
				
				//Examine the events
				Iterator<SelectionKey> readyKeys = this.selector.selectedKeys().iterator();

				while(readyKeys.hasNext()) {
					SelectionKey key = readyKeys.next();
					readyKeys.remove();
					
					if (!key.isValid()) {
						continue;
					}
					
					//Check what kind of event we have and process it
					if (key.isAcceptable()) {
						this.accept(key);
					} else if (key.isReadable()) {
						this.read(key);
					} else if (key.isWritable()) {
						this.write(key);
					}
				}
			}
			catch (IOException e) {
				System.err.println(e.getMessage());
			}
		}
	}
	
	private Selector initSelector() throws IOException {
		
		//Create server selector
		Selector selector = SelectorProvider.provider().openSelector();
		
		//Initialize the server channel
		this.serverChannel = ServerSocketChannel.open();
		this.serverChannel.configureBlocking(false);
		
		//Bind the server socket to an address and port
		InetSocketAddress isa = new InetSocketAddress(this.middlewareIP, this.port);
	    this.serverChannel.socket().bind(isa);
	    
	    //Register the server channel to the selector
	    this.serverChannel.register(selector, SelectionKey.OP_ACCEPT);
	    
	    return selector;
	}
	
	private void accept(SelectionKey key) throws IOException {
		//If it is acceptable, the channel key can only be a server one
		ServerSocketChannel serverSocketChannel = (ServerSocketChannel) key.channel();
		
		//Make a non-blocking socket channel for that connection
		SocketChannel connSocketChannel = serverSocketChannel.accept();
		connSocketChannel.configureBlocking(false);
		
		//Register the new connection's channel with the selector 
		//and specify we want to read from it
		connSocketChannel.register(this.selector, SelectionKey.OP_READ);
	}
	
	private void read(SelectionKey key) throws IOException {
		SocketChannel socketChannel = (SocketChannel) key.channel();
		
		//Empty buffer so it is ready to store the new data
		this.readBuffer.clear();
		
		//Read from the buffer
		int bytesRead = 0; 
		byte[] responseData;
		try {
			bytesRead = socketChannel.read(this.readBuffer);
		} catch (IOException ioe) {
			ioe.printStackTrace();
			//A problem with the connection on the remote side
			key.channel().close();
			key.cancel();
			return;
		}
		
		//Check if the connection has been closed cleanly by the client
		if (bytesRead == -1) {
			//in this case we close the key and channel on this side as well
			System.err.println("Connection closed by client");
			key.channel().close();
			key.cancel();
			return;
		} else {
			//Make a copy of the array data and pass it for processing
			responseData = new byte[bytesRead];
			System.arraycopy(this.readBuffer.array(), 0, responseData, 0, bytesRead);
			
			//create event and start clock
			MiddlewareDataEvent requestEvent = new MiddlewareDataEvent(this, socketChannel, responseData);
			requestEvent.startTotalTime();
			this.requestHandler.processRequest(requestEvent, bytesRead);
		}
		
	}
	
	private void write(SelectionKey key) throws IOException {
		SocketChannel socketChannel = (SocketChannel) key.channel();
	
		synchronized (this.pendingData) {
			MiddlewareDataEvent event = this.pendingData.get(socketChannel);
			event.stopReturnQueueTime();
			socketChannel.write(ByteBuffer.wrap(event.responseData));
			event.stopTotalTime();
			if (event.op) {
				if (++this.getCounter == 500) {
					logger.info(event.toString());
					this.getCounter = 0;
				}
			} else {
				if (++this.setCounter == 25) {
					logger.info(event.toString());
					this.setCounter = 0;
				}
			}
			
			key.interestOps(SelectionKey.OP_READ);
		}
	}
	
}
