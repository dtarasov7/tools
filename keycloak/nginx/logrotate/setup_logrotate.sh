#!/bin/bash
set +x
rm -f /etc/logrotate.d/wcms-portal
cp wcms-portal /etc/logrotate.d/
