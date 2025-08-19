#!/usr/bin/python2.7
#_*_ coding:utf-8 _*_

import sys
import traceback
import commands
import os, sys, re, getopt
from xml.dom import minidom
import MySQLdb
import datetime
import time

db_ip = "127.0.0.1"
db_user = "weygame"
db_passwd = "PQbwA5Wa"
db_name = "wy_stat"
config_file = "stat_config.xml"



def log(content):
	print ''.join([datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), ",", content])

def parse_config(config_file_name):
	dom = minidom.parse(config_file_name)
	root = dom.documentElement

	stat_map = {}
	stat_configs = root.getElementsByTagName("stat")
	for stat_config in stat_configs:
		proto = stat_config.attributes["proto"].value
		table_suffix = stat_config.attributes["table_suffix"].value
		out_db = stat_config.attributes["db"].value
		out_log = stat_config.attributes["log"].value
		stat_map[proto] = {"proto": proto, "table_suffix": table_suffix, "db": out_db, "log": out_log} 
	return stat_map

def update_config(stat_map):
	for key in stat_map:
		stat_config = stat_map[key]
		db = MySQLdb.connect(db_ip, db_user, db_passwd, db_name)
		cursor = db.cursor()
		cursor.execute("insert into Stat_OutputConfig(stattype, log, db) values('%s',%s,%s) on duplicate key update log=%s,db=%s" % (stat_config["proto"], stat_config["log"], stat_config["db"], stat_config["log"], stat_config["db"]))
		db.commit()
		cursor.close()
		db.close()

def main():   
	stat_map = parse_config(config_file)
	update_config(stat_map)

if __name__ == "__main__":
    main()
