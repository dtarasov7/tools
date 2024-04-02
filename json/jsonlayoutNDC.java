import org.apache.log4j.Layout;
import org.apache.log4j.MDC;
import org.apache.log4j.NDC;
import org.apache.log4j.spi.LoggingEvent;
import org.json.JSONObject;

import java.io.PrintWriter;
import java.io.StringWriter;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;

public class JsonLayoutWithMDC extends Layout {
    private String dateFormat = "yyyy-MM-dd HH:mm:ss";
    private Map<String, String> staticFields = new HashMap<>();
    private boolean includeNDC = true;

    public void setDateFormat(String dateFormat) {
        this.dateFormat = dateFormat;
    }

    public void addStaticField(String key, String value) {
        staticFields.put(key, value);
    }

    public void setIncludeNDC(boolean includeNDC) {
        this.includeNDC = includeNDC;
    }

    @Override
    public String format(LoggingEvent event) {
        JSONObject json = new JSONObject();
        json.put("timestamp", formatDate(event.getTimeStamp(), dateFormat));
        json.put("level", event.getLevel().toString());
        json.put("logger", event.getLoggerName());
        json.put("message", escapeJsonString(event.getMessage().toString()));
        json.put("thread", event.getThreadName());

        // Adding MDC properties
        JSONObject mdcJson = new JSONObject();
        @SuppressWarnings("unchecked")
        Iterator<String> mdcKeys = MDC.getContext().getKeys();
        while (mdcKeys.hasNext()) {
            String key = mdcKeys.next();
            mdcJson.put(key, MDC.get(key));
        }
        json.put("mdc", mdcJson);

        // Adding NDC stack
        if (includeNDC) {
            json.put("ndc", NDC.get());
        }

        // Adding exception stack trace
        if (event.getThrowableInformation() != null) {
            StringWriter sw = new StringWriter();
            PrintWriter pw = new PrintWriter(sw);
            event.getThrowableInformation().getThrowable().printStackTrace(pw);
            json.put("stackTrace", sw.toString());
        }

        // Adding static fields
        for (Map.Entry<String, String> entry : staticFields.entrySet()) {
            json.put(entry.getKey(), entry.getValue());
        }

        return json.toString() + "\n";
    }

    private String formatDate(long timestamp, String dateFormat) {
        SimpleDateFormat sdf = new SimpleDateFormat(dateFormat);
        return sdf.format(new Date(timestamp));
    }

    private String escapeJsonString(String input) {
        // Escape special characters
        // You can use the escapeJsonString method from the previous example if needed
        return input;
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

//log4j.rootLogger=INFO, stdout
//log4j.appender.stdout=org.apache.log4j.ConsoleAppender
//log4j.appender.stdout.layout=your.package.JsonLayoutWithMDC
//log4j.appender.stdout.layout.dateFormat=yyyy-MM-dd'T'HH:mm:ss.SSSZ
//log4j.appender.stdout.layout.includeNDC=true
