import org.apache.log4j.Layout;
import org.apache.log4j.MDC;
import org.apache.log4j.spi.LoggingEvent;
import org.json.JSONObject;

import java.io.PrintWriter;
import java.io.StringWriter;
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

        // Adding exception stack trace
        if (event.getThrowableInformation() != null) {
            StringWriter sw = new StringWriter();
            PrintWriter pw = new PrintWriter(sw);
            event.getThrowableInformation().getThrowable().printStackTrace(pw);
            json.put("stackTrace", sw.toString());
        }

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

