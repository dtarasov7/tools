export PROMPT_COMMAND='RETRN_VAL=$?;
if [ -f /tmp/lastoutput.tmp ]; then
    LAST_OUTPUT=$(cat /tmp/lastoutput.tmp);
    rm /tmp/lastoutput.tmp;
fi;
logger -S 10000 -p local6.debug "{\"user\": \"$(whoami)\", \"path\": \"$(pwd)\", \"pid\": \"$$\", \"command\": \"$(history 1 | sed "s/^[ ]*[0-9]\+[ ]*//" )\", \"status\": \"$RETRN_VAL\", \"output\": \"$LAST_OUTPUT\"}"; unset LAST_OUTPUT; '

logoutput() { output=$(while read input; do echo "$input"; done < "${1:-/dev/stdin}"); echo -e "$output"; echo -e "$output" | head -c 10000 > /tmp/lastoutput.tmp; return $?; }

