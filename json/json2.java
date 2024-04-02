We create an instance of JsonLayoutWithMDC and set some configurations such as date format and including NDC.
We create a mock LoggingEvent object with some sample log data.
We invoke the format method of JsonLayoutWithMDC to generate the log message.
We assert that the generated log message matches the expected JSON format based on the configured layout.


import org.apache.log4j.Layout;
import org.apache.log4j.MDC;
import org.apache.log4j.spi.LoggingEvent;
import org.json.JSONObject;

import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Iterator;

public class JsonLayoutWithMDC extends Layout {
    private String dateFormat = "yyyy-MM-dd HH:mm:ss";

    public void setDateFormat(String dateFormat) {
        this.dateFormat = dateFormat;
    }

    @Override
    public String format(LoggingEvent event) {
        JSONObject json = new JSONObject();
        json.put("timestamp", formatDate(event.getTimeStamp(), dateFormat));
        json.put("level", event.getLevel().toString());
        json.put("logger", event.getLoggerName());
        json.put("message", event.getMessage().toString());
        json.put("thread", event.getThreadName());

        // Adding MDC properties
        JSONObject mdcJson = new JSONObject();
        @SuppressWarnings("unchecked")
        Iterator<String> keys = MDC.getContext().getKeys();
        while (keys.hasNext()) {
            String key = keys.next();
            mdcJson.put(key, MDC.get(key));
        }
        json.put("mdc", mdcJson);

        return json.toString() + "\n";
    }

    private String formatDate(long timestamp, String dateFormat) {
        SimpleDateFormat sdf = new SimpleDateFormat(dateFormat);
        return sdf.format(new Date(timestamp));
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

