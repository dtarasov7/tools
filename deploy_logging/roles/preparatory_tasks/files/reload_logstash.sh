docker_path=$(whereis docker | awk '{print $2}')
$docker_path exec logstash kill -SIGHUP 1
