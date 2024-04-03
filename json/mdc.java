// Adding MDC properties
JSONObject mdcJson = new JSONObject();
Map<?, ?> mdcContext = MDC.getContext();
if (mdcContext != null) {
    for (Map.Entry<?, ?> entry : mdcContext.entrySet()) {
        Object key = entry.getKey();
        Object value = entry.getValue();
        if (key != null && value != null) {
            mdcJson.put(key.toString(), value.toString());
        }
    }
}
json.put("mdc", mdcJson);
