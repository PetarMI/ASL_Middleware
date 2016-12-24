package server.nio;

import java.io.IOException;
import java.util.List;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.ConcurrentLinkedQueue;
import java.util.concurrent.LinkedBlockingQueue;

public class QueueManager {
	
	private final int ID;
	private String mcServerIP;
	private int mcServerPort;
	
	private BlockingQueue<MiddlewareDataEvent> getQueue;
	private ConcurrentLinkedQueue<MiddlewareDataEvent> setQueue;
	
	private SetThread setThread;
	
	public QueueManager(int id, String serverIP, int port, List<ServerDetails> setServers,
			int numThreadsPTP) {
		this.ID = id;
		
		this.getQueue = new LinkedBlockingQueue<MiddlewareDataEvent>();
		this.setQueue = new ConcurrentLinkedQueue<MiddlewareDataEvent>();
		
		this.mcServerIP = serverIP;
		this.mcServerPort = port;
		
		this.startWorkers(numThreadsPTP, setServers);
	}
	
	public void enqueueGet(MiddlewareDataEvent getRequest) {
		try {
			getRequest.startQueueTime();
			this.getQueue.put(getRequest);
		} catch (InterruptedException e) {
			e.printStackTrace();
		}
	}
	
	public void enqueueSet(MiddlewareDataEvent setRequest) {
		setRequest.startQueueTime();
		this.setQueue.offer(setRequest);
		this.setThread.wakeUp();
	}
	
	//start threads
	private void startWorkers(int numThreadsPTP, List<ServerDetails> setServers) {
		try {
			// TODO pass only the map of servers
			this.setThread = new SetThread(this.ID, this.setQueue, setServers);
			new Thread(this.setThread).start();
			
			System.out.println("Starting get threads " + numThreadsPTP);
			//start all get threads
			for (int i = 0; i < numThreadsPTP; i++) {
				new Thread(new GetThread(this.ID, i, this.getQueue, this.mcServerIP, this.mcServerPort)).start();
			}
		} catch (IOException e) {
			System.err.println("Unabe to start worker");
			e.printStackTrace();
		}
	}

}
