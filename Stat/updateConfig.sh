#!/bin/bash

DB_NAME="wy_stat"
DB_IP="127.0.0.1"
DB_USER="weygame"
DB_PASS="PQbwA5Wa"

#日志类型配置
grep "LogType_" SceneServer/LogType.h | awk -F' ' '{print $3""$5}' | sed -e "s/,/,'/g" -e "s/$/'/g" | while read line
do
	mysql -u$DB_USER -h$DB_IP -p$DB_PASS -e "use $DB_NAME; replace into stat_config_logtype(id, name) values ($line)"
done

DB_NAME="wy_plat"
DB_IP="127.0.0.1"
DB_USER="wygame"
DB_PASS="PQbwA5Wa"

grep AccType_ common/LoginMsg.proto | awk -F' ' '{print $3""$5$6}' | sed -e "s/;/;'/g" -e "s/$/'/g" -e "s/;/,/g" | while read line
do
	mysql -u$DB_USER -h$DB_IP -p$DB_PASS -e "use $DB_NAME; replace into AccTypeList(acctype, typename) values ($line)"
done
