#!/bin/bash

cat version.txt | while read line
do
	mysql -uweygame -h127.0.0.1 -pPQbwA5Wa -e "use wy_stat; set names utf8; insert into __db_version__(version) values ($line)"
done
