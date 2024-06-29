https://unix.stackexchange.com/questions/413878/json-array-to-bash-variables-using-jq


cat 1.json | python3 -c 'import json,sys;obj=json.load(sys.stdin)["SITE_DATA"];[print(f"{k}={v}") for k,v in obj.items()]'

cat 1.json | python3 -c "import json,sys;obj=json.load(sys.stdin)[\"SITE_DATA\"];[print(f\"{k}={v}\") for k,v in obj.items()]"

https://www.squash.io/how-to-import-json-from-a-bash-script-on-linux/

