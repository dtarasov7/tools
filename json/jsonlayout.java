import org.apache.log4j.Layout;
import org.apache.log4j.spi.LoggingEvent;
import org.json.JSONObject;

public class JsonLayout extends Layout {

    @Override
    public String format(LoggingEvent event) {
        JSONObject json = new JSONObject();
        json.put("timestamp", event.getTimeStamp());
        json.put("level", event.getLevel().toString());
        json.put("logger", event.getLoggerName());
        json.put("message", event.getMessage().toString());
        json.put("thread", event.getThreadName());
        // You can add more fields as needed

        return json.toString() + "\n";
    }

    @Override
    public boolean ignoresThrowable() {
        return false;
    }

    @Override
    public void activateOptions() {
        // Nothing to initialize
    }
    
    @Override
    public void setLocationInfo(boolean locationInfo) {
        // We don't need location info
    }
    
    @Override
    public String getContentType() {
        return "application/json";
    }

    @Override
    public void finalize() {
        // Nothing to finalize
    }
}

