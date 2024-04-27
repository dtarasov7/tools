#!/bin/bash
#Удаляе все файлы старше n-дней (14 дней в данном примере и файлы с расширеним .zip)
#set -x

HOST_BK_PATH=/path/to/backups

#ls -tr /path/to/backups/*.zip | head -n -14 | xargs --no-run-if-empty rm

FOR_DELETE=$(ls -tr $HOST_BK_PATH/*.zip | head -n -14)

while IFS= read -r FILE_PATH; do
if [ -z "$FILE_PATH" ]; then
      echo "No files to delete"
else
      FILE_NAME=$(basename ${FILE_PATH})
      ls $FILE_PATH | xargs --no-run-if-empty rm
      echo "Backup file $FILE_NAME was deleted"
fi
done <<< "$FOR_DELETE"
