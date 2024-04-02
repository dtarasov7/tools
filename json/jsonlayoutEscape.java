import org.apache.log4j.Layout;
import org.apache.log4j.MDC;
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

    public void setDateFormat(String dateFormat) {
        this.dateFormat = dateFormat;
    }

    public void addStaticField(String key, String value) {
        staticFields.put(key, value);
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
        StringBuilder result = new StringBuilder();
        for (char ch : input.toCharArray()) {
            switch (ch) {
                case '"':
                    result.append("\\\"");
                    break;
                case '\\':
                    result.append("\\\\");
                    break;
                case '\b':
                    result.append("\\b");
                    break;
                case '\f':
                    result.append("\\f");
                    break;
                case '\n':
                    result.append("\\n");
                    break;
                case '\r':
                    result.append("\\r");
                    break;
                case '\t':
                    result.append("\\t");
                    break;
		case '/':
                    result.append("\\/");
                    break;
                default:
                    if (Character.isISOControl(ch)) {
                        result.append(String.format("\\u%04X", (int) ch));
                    } else {
                        result.append(ch);
                    }
                    break;
            }
        }
        return result.toString();
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

