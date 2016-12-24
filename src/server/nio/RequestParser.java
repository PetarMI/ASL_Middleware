package server.nio;

import java.io.UnsupportedEncodingException;
import java.nio.charset.Charset;

public class RequestParser {
	
	/** 
	 * Parse the incoming request
	 * return an array containing the operation type and key 
	 */
	public String[] parse(byte[] bufferData) {
		String data = this.parseData(bufferData, 0);
		
		return data.split("\\s+");
	}
	
	private String parseData(byte[] data, int offset) {
		for (int i = offset; i < data.length - 1; i++) {
            if (data[i] == 13) {
                if (data[i+1] == 10) {
                	return new String(data, offset, i - offset, Charset.forName("UTF-8"));
                }
            }
        }
        return new String(data, Charset.forName("UTF-8"));
    }
	
	public String[] parseResponse(byte[] respData) {
		String[] responses = new String[5];
		try {
			responses = new String(respData, "UTF-8").split("\r\n");
		} catch (UnsupportedEncodingException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
		return responses;
	}
	
	/*public List<byte[]> parseResponse(byte[] respData) {
		if (respData.length % 8 != 0) {
			logger.info(Integer.toString(respData.length));
			try {
				logger.info(new String(respData, "ASCII"));
			} catch (UnsupportedEncodingException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
		}
		List<byte[]> responses = new LinkedList<byte[]>();
		int offset = 0;
		for (int i = 0; i < respData.length - 1; i++) {
            if (respData[i] == 13) {
                if (respData[i+1] == 10) {
                	byte[] byteChunk = new byte[i + 2 - offset];
                	System.arraycopy(respData, offset, byteChunk, 0, i + 2 - offset);
                	responses.add(byteChunk);
                	offset = i + 2;
                }
            }
        }
		
		return responses;
	}*/
}
