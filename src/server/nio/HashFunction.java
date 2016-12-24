package server.nio;

import java.nio.ByteBuffer;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;

public class HashFunction {

	private MessageDigest md;
	private ByteBuffer buffer;
	
	public HashFunction() {
		try {
			buffer = ByteBuffer.allocate(128);
			this.md = MessageDigest.getInstance("md5");
		} catch (NoSuchAlgorithmException e) {
			e.printStackTrace();
		}
	}
	
	public Long hash(String str) {
		return this.md5(str);
	}
	
	private Long md5(String str) {
		byte[] msgBytes = str.getBytes();
		this.md.update(msgBytes);
		
		byte[] msgDigest = this.md.digest();
		
		this.buffer.clear();
		this.buffer.put(msgDigest);
		this.buffer.flip();
		
		return this.buffer.getLong();
	}
	
	//DJB2 hashing algorithm implementation
	private int djb2Hash(String str) {
		int hash = 5381;
		for (int i = 0; i < str.length(); i++) {
			hash = str.charAt(i) + ((hash << 5) - hash);
		}
		return hash;
	}
	
}
