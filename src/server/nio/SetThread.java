package server.nio;

import java.io.IOException;
import java.net.InetSocketAddress;
import java.net.StandardSocketOptions;
import java.nio.ByteBuffer;
import java.nio.channels.SelectionKey;
import java.nio.channels.Selector;
import java.nio.channels.SocketChannel;
import java.nio.channels.spi.SelectorProvider;
import java.util.*;
import java.util.concurrent.ConcurrentLinkedQueue;
import java.util.logging.FileHandler;
import java.util.logging.Level;
import java.util.logging.Logger;

public class SetThread implements Runnable {
	
	//Logging stuff
	private final int tID;
	private int counter = 0;
	private int jobsCount = 0;
	
	private ConcurrentLinkedQueue<MiddlewareDataEvent> setQueue;

	private Selector selector;
	
	//Store the connections to all servers for the replication
	private List<SocketChannel> socketChannels;
	private ByteBuffer readBuffer = ByteBuffer.allocate(256 * 1024);
	private ByteBuffer writeBuffer = ByteBuffer.allocate(2048);

	//Map selection keys to data events
	private Map<SelectionKey, Queue<MiddlewareDataEvent>> events;
	
	//Keep a map between channels and what data is to be written on them
	private Map<SocketChannel, MiddlewareDataEvent> pendingData;
	
	private RequestParser requestParser;
	
	public SetThread(int tid, ConcurrentLinkedQueue<MiddlewareDataEvent> setQueue, 
			List<ServerDetails> servers) throws IOException{
		this.tID = tid;
		
		this.setQueue = setQueue;
		this.selector = this.initSelector();
		
		this.pendingData = new HashMap<SocketChannel, MiddlewareDataEvent>();
		
		this.events = new HashMap<SelectionKey, Queue<MiddlewareDataEvent>>();
		this.requestParser = new RequestParser();
		
		//Open the connection to all servers
		this.initiateConnections(servers);
	}
	
	public void wakeUp() {
		this.selector.wakeup();
	}
	
	public void send(MiddlewareDataEvent dataEvent) {
		
		dataEvent.startProcessQueueTime();
		
		//send on all channels
		for (SocketChannel socket : this.socketChannels) {
			this.pendingData.put(socket, dataEvent);
			
			SelectionKey key = socket.keyFor(this.selector);
			key.interestOps(SelectionKey.OP_WRITE);
		}
		this.jobsCount++;
		
		this.writeBuffer.clear();
		byte[] dataCopy = new byte[dataEvent.requestData.length];
		System.arraycopy(dataEvent.requestData, 0, dataCopy, 0, dataEvent.requestData.length);
		this.writeBuffer.put(dataCopy);
		this.writeBuffer.flip();
	}
	
	//main method is responsible for taking events off the queue
	//and sending the request to a memcached server
	public void run() {
		MiddlewareDataEvent dataEvent;
		
	    while(true) {
	    	// Wait for data to become available

			dataEvent = (MiddlewareDataEvent) setQueue.poll();
			if (dataEvent != null) {
				dataEvent.stopQueueTime();
				this.send(dataEvent);
			}
			
			//Logging
			if (++this.counter == 25) {
				System.out.println(this.toString());
				this.counter = 0;
			}
			
			try {
				// Wait for an event one of the registered channels
				this.selector.select();
				
				// Iterate over the set of keys for which events are available
				Iterator<SelectionKey> selectedKeys = this.selector.selectedKeys().iterator();

				while (selectedKeys.hasNext()) {
					SelectionKey key = (SelectionKey) selectedKeys.next();
					selectedKeys.remove();

					if (!key.isValid()) {
						continue;
					}

					// Check what event is available and deal with it
					if (key.isConnectable()) {
						this.finishConnection(key);
					} else if (key.isReadable()) {
						this.read(key);
					} else if (key.isWritable()) {
						this.write(key);
					}
				}
			} catch (Exception e) {
				e.printStackTrace();
			}
	    }
	}
	
	private void read(SelectionKey key) throws IOException {
		SocketChannel socketChannel = (SocketChannel) key.channel();
		this.readBuffer.clear();

		int numRead;
		try {
			numRead = socketChannel.read(this.readBuffer);
		} catch (IOException e) {
			key.cancel();
			socketChannel.close();
			return;
		}

		//TODO decide what to do about this
		if (numRead == -1) {
			System.err.println("Memcached closed the connection");
			key.channel().close();
			key.cancel();
			return;
		}
		
		//Parse the response
		byte[] dataCopy = new byte[numRead];
		System.arraycopy(this.readBuffer.array(), 0, dataCopy, 0, numRead);
		
		String[] responses = this.requestParser.parseResponse(dataCopy);

		for (String response : responses) {
			//The response was just \r\n
			if (response.length() == 0) {
				continue;
			}
			
			//Request could not be stored
			if (!response.equals("STORED")) {
				response = "ERROR";
			}

			MiddlewareDataEvent responseEvent = this.events.get(key).poll();
			if (responseEvent == null) {
				continue;
			}
			
			responseEvent.setValid(response);
			responseEvent.counter++;
			if (responseEvent.counter == this.socketChannels.size()) {
				responseEvent.stopServerTime();
				this.handleResponse(responseEvent, new String(response + "\r\n").getBytes());
				this.jobsCount--;
			}
		}
		
	}
	
	private void handleResponse(MiddlewareDataEvent event, byte[] dataCopy)
			throws IOException {
		event.responseData = dataCopy;
		event.startReturnEnqueueTime();
		event.server.send(event);
	}
	
	private void write(SelectionKey key) throws IOException {
		SocketChannel socketChannel = (SocketChannel) key.channel();
		
		MiddlewareDataEvent event = this.pendingData.get(socketChannel);
		event.stopProcessQueueTime();
		
		//ByteBuffer buf = ByteBuffer.wrap(event.requestData);
		
		//add the event to the queue
		try {
			this.events.get(key).add(event);
		} catch (IllegalStateException ise) {
			ise.printStackTrace();
		}

		event.startServerTime();
		
		while(writeBuffer.hasRemaining()) {
			socketChannel.write(this.writeBuffer);
		}
		this.writeBuffer.rewind();
		//data is sent and now we wait for a response
		key.interestOps(SelectionKey.OP_READ);
	}
	
	private void finishConnection(SelectionKey key) throws IOException {
		SocketChannel socketChannel = (SocketChannel) key.channel();

		try {
			socketChannel.finishConnect();
			
			//init the event queue for this socket
			this.events.put(key, new ArrayDeque<MiddlewareDataEvent>());
		} catch (IOException e) {
			System.out.println(e);
			key.cancel();
			return;
		}
	
		//This channel is now open for writing
		key.interestOps(SelectionKey.OP_READ);
	}
	
	private Selector initSelector() throws IOException {
		// Create a new selector
	    return SelectorProvider.provider().openSelector();
	}
	
	private void initiateConnections(List<ServerDetails> servers) throws IOException {
		this.socketChannels = new ArrayList<SocketChannel>();
	    
		//do this for all servers
		for(ServerDetails server : servers) {
			
			// Create a non-blocking socket channel
		    SocketChannel socketChannel = SocketChannel.open();
		    socketChannel.configureBlocking(false);
		    socketChannel.setOption(StandardSocketOptions.SO_RCVBUF, 256 * 1024); 
		    socketChannel.setOption(StandardSocketOptions.SO_SNDBUF, 256 * 1024);
		  
		    System.out.println("Connection to " + server.getIP() + ":" + server.getPort());
		    // Kick off connection establishment
		    socketChannel.connect(new InetSocketAddress(server.getIP(), server.getPort()));
		  
		    socketChannel.register(this.selector, SelectionKey.OP_CONNECT);
		    
		    this.socketChannels.add(socketChannel);
		}
	}
	
	@Override
	public String toString() {
		
		return String.format("%d,%d,%d,%d", 1, this.tID, this.setQueue.size(), jobsCount);
	}
}