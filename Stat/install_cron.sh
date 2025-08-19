#/bin/bash

path=$(dirname $0)
path=${path/\./$(pwd)}

echo $path

echo "00 03 * * * root $path/load_stat_data" > /etc/cron.d/load_stat_data
mkdir -p /weywell/stat/log && chmod 777 -R /weywell/stat/log
