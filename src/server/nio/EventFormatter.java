package server.nio;

import java.util.logging.Formatter;
import java.util.logging.LogRecord;

public class EventFormatter extends Formatter {

	@Override
	public String format(LogRecord record) {
		return (record.getMessage() + "\n");
	}
	
}
