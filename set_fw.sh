firewall-cmd --zone=public --add-port=9200/tcp --permanent
firewall-cmd --zone=public --add-port=9300/tcp --permanent
firewall-cmd --zone=public --add-port=5601/tcp --permanent
firewall-cmd --zone=public --add-port=5044/tcp --permanent
firewall-cmd --zone=public --add-port=9600/tcp --permanent
firewall-cmd --reload
