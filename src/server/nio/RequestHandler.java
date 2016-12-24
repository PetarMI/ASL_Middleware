package server.nio;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;

public class RequestHandler {

	private List<QueueManager> allManagers;
		
	//The component is responsible for hashing the key and
	//returning the correct QueueManager for the specific request
	private HashingHandler<QueueManager> hashingHandler;
	private RequestParser requestParser;
	
	public RequestHandler(List<String> memcServers, int numThreadsPTP, int replication) {
		this.initManagers(memcServers, numThreadsPTP, replication);
		this.hashingHandler = new HashingHandler<QueueManager>(this.allManagers);
		this.requestParser = new RequestParser();
	}

	public void processRequest(MiddlewareDataEvent event, int bytesRead) {
		//parse the operation and the key
		event.startParseTime();
		String[] data = requestParser.parse(event.requestData);
		String op = data[0];
		String key = data[1];

		//Get the queue manager to which this request has to be sent
		QueueManager queueManager = this.hashingHandler.get(key);
		event.stopParseTime();
		
		if (op.equals("set")) {
			//System.out.println("Found a set event");
			event.op = false;
			queueManager.enqueueSet(event);
		} else if (op.equals("get")) {
			event.op = true;
			//System.out.println("Found a get event");
			queueManager.enqueueGet(event);
		} else if (op.equals("delete")){
			event.op = false;
			queueManager.enqueueSet(event);
		} else {
			System.out.println(op);
			System.err.println("Unknown operation");
		}
		
	}
	
	private void initManagers(List<String> memcServers, int numThreadsPTP, int replication) {
		int numServers = memcServers.size();
		System.out.println("Initializing managers: " + numServers);
		this.allManagers = new LinkedList<QueueManager>();
		
		for (int i = 0; i < numServers; i++) {
			//Main server details
			String[] serverInfo = memcServers.get(i).split(":");
			String serverIP = serverInfo[0];
			int serverPort = Integer.parseInt(serverInfo[1]);
			
			//Add all replication servers
			List<ServerDetails> replServers = new ArrayList<ServerDetails>();
			replServers.add(new ServerDetails(serverIP, serverPort));
			System.out.println(String.format("Adding new manager at ip: %1$s and port: %2$d", serverIP, serverPort));
			
			for (int j = 1; j < replication; j++) {
				int serverInd = (i + j) % numServers;
				String[] replServerInfo = memcServers.get(serverInd).split(":");
				String replServerIP = replServerInfo[0];
				int replServerPort = Integer.parseInt(replServerInfo[1]);
				System.out.println("Server for set " + replServerIP + ":" + replServerPort);
				replServers.add(new ServerDetails(replServerIP, replServerPort));
			}
			
			QueueManager qm = new QueueManager(i, serverIP, serverPort, replServers,
					numThreadsPTP);
			//instantiate manager
			this.allManagers.add(qm);
		}
	}
}
