package server.nio;

import java.nio.channels.SocketChannel;
import java.nio.charset.Charset;

class MiddlewareDataEvent {
	public HashingServer server;
	public SocketChannel socket;
	public byte[] requestData;
	public byte[] responseData;
	
	//variables to store time
	private long startTotalTime;
	private long startParseTime;
	private long startQueueTime;
	private long startProcessQueueTime = 0;
	private long startServerTime;
	private long startReturnEnqueueTime;
	private long startReturnQueueTime;
	private long stopTotalTime;
	private long stopParseTime;
	private long stopQueueTime;
	private long stopProcessQueueTime = 0;
	private long stopServerTime;
	private long stopReturnEnqueueTime;
	private long stopReturnQueueTime;
	
	private String getResult = "Retrieved";
	private String setResult = "STORED";
	
	//Variables used for set replication
	public int counter = 0;
	private boolean processedOnce = false;
	
	public boolean op;
	
	public MiddlewareDataEvent(HashingServer server, SocketChannel socket, byte[] data) {
		this.server = server;
		this.socket = socket;
		this.requestData = data;
	}
	
	/*@Override
	public String toString() {
		String opType = op ? "get" : "set";
		String opRes = op ? getResult : setResult;
		
		return String.format("%s,%d,%d,%d,%d,%d,%d,%s", opType, this.startParseTime, 
				this.startQueueTime, this.startProcessQueueTime, this.startServerTime, this.startReturnTime, 
				this.startTotalTime,	opRes);
	}*/
	
	@Override
	public String toString() {
		String opType = op ? "get" : "set";
		String opRes = op ? getResult : setResult;
		
		return String.format("%s,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d", opType, this.startParseTime, 
				this.stopParseTime, this.startQueueTime, this.stopQueueTime, this.startProcessQueueTime, 
				this.stopProcessQueueTime, this.startServerTime, this.stopServerTime, this.startReturnEnqueueTime, 
				this.stopReturnEnqueueTime, this.startReturnQueueTime, this.stopReturnQueueTime,
				this.startTotalTime, this.stopTotalTime);
	}
	
	public void startTotalTime() {
		this.startTotalTime = System.nanoTime();
	}
	
	public void stopTotalTime() {
		/*long stopTime = System.nanoTime();
		this.startTotalTime = stopTime - this.startTotalTime;*/
		this.stopTotalTime = System.nanoTime();
	}
	
	public void startParseTime() {
		this.startParseTime = System.nanoTime();
	}
	
	public void stopParseTime() {
		/*long stopTime = System.nanoTime();
		this.startParseTime = stopTime - this.startParseTime;*/
		this.stopParseTime = System.nanoTime();
	}
	
	public void startQueueTime() {
		this.startQueueTime = System.nanoTime();
	}
	
	public void stopQueueTime() {
		/*long stopTime = System.nanoTime();
		this.startQueueTime = stopTime - this.startQueueTime;*/
		this.stopQueueTime = System.nanoTime();
	}
	
	public void startProcessQueueTime() {
		this.startProcessQueueTime = System.nanoTime();
	}
	
	public void stopProcessQueueTime() {
		if (!this.processedOnce) {
			/*long stopTime = System.nanoTime();
			this.startProcessQueueTime = stopTime - this.startProcessQueueTime;*/
			this.stopProcessQueueTime = System.nanoTime();
			this.processedOnce = true;
		}
	}
	
	public void startServerTime() {
		this.startServerTime = System.nanoTime();
	}
	
	public void stopServerTime() {
		/*long stopTime = System.nanoTime();
		this.startServerTime = stopTime - this.startServerTime;*/
		this.stopServerTime = System.nanoTime();
	}
	
	public void startReturnEnqueueTime() {
		this.startReturnEnqueueTime = System.nanoTime();
	}
	
	public void stopReturnEnqueueTime() {
		/*long stopTime = System.nanoTime();
		this.startReturnTime = stopTime - this.startReturnTime;*/
		this.stopReturnEnqueueTime = System.nanoTime();
	}
	
	public void startReturnQueueTime() {
		this.startReturnQueueTime = System.nanoTime();
	}
	
	public void stopReturnQueueTime() {
		/*long stopTime = System.nanoTime();
		this.startReturnTime = stopTime - this.startReturnTime;*/
		this.stopReturnQueueTime = System.nanoTime();
	}
	
	public long getTotalTime() {
		return this.startTotalTime;
	}
	
	public void setValid(byte[] data) {
		if (this.setResult.equals("STORED")) {
	        for (int i = 0; i < data.length - 1; i++) {
	            if (data[i] == 13) {
	                if (data[i+1] == 10) {
	                	this.setResult = new String(data, 0, i, 
	                			Charset.forName("UTF-8"));
	                }
	            }
	        }	
		}
	}
	
	public void setValid(String data) {
		this.setResult = data;
	}
}