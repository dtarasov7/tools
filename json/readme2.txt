log4j.rootLogger=DEBUG, STDOUT

log4j.appender.STDOUT=org.apache.log4j.ConsoleAppender
log4j.appender.STDOUT.layout=your.package.JsonLayoutWithMDC
log4j.appender.STDOUT.layout.dateFormat=yyyy-MM-dd'T'HH:mm:ss.SSSZ

