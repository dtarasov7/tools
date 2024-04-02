import org.apache.log4j.Level;
import org.apache.log4j.Logger;
import org.apache.log4j.spi.LoggingEvent;
import org.junit.Test;
import static org.junit.Assert.*;

public class JsonLayoutWithMDCTest {

    @Test
    public void testFormat() {
        JsonLayoutWithMDC layout = new JsonLayoutWithMDC();
        layout.setDateFormat("yyyy-MM-dd'T'HH:mm:ss.SSSZ");
        layout.setIncludeNDC(true);

        LoggingEvent event = new LoggingEvent(
                "org.example.Logger",
                Logger.getLogger(JsonLayoutWithMDCTest.class),
                Level.INFO,
                "Test message",
                new RuntimeException("Test exception")
        );

        String formattedLog = layout.format(event);

        // Assert the expected JSON format based on the configured layout
        assertTrue(formattedLog.contains("\"timestamp\":\""));
        assertTrue(formattedLog.contains("\"level\":\"INFO\""));
        assertTrue(formattedLog.contains("\"logger\":\"org.example.Logger\""));
        assertTrue(formattedLog.contains("\"message\":\"Test message\""));
        assertTrue(formattedLog.contains("\"thread\":\""));
        assertTrue(formattedLog.contains("\"mdc\":{}"));
        assertTrue(formattedLog.contains("\"ndc\":\"\""));
        assertTrue(formattedLog.contains("\"stackTrace\":\"java.lang.RuntimeException: Test exception"));
    }
}

