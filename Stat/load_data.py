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
log_root = "/weywell/stat/log/"


log_path = ""

def log(content):
    print ''.join([datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), ", - ", content])

def get_path():
    if len(sys.argv) < 2:
        date = datetime.date.today() #+ datetime.timedelta(-1)
        date_str = date.strftime("%Y%m%d")
    else:
        date_str = sys.argv[1]
    global log_path
    log_path = ''.join([log_root, date_str])
    
def print_config():
    log("[config] 配置,db_ip:%s, db_user:%s, db_passwd:%s, db_name:%s, config_file:%s, log_root:%s, log_path:%s" % (db_ip, db_user, db_passwd, db_name, config_file, log_root, log_path))

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
        load = stat_config.attributes["load"].value
        stat_map[proto] = {"proto": proto, "table_suffix": table_suffix, "out_db": out_db, "out_log": out_log, "load": load} 
    return stat_map

def load_data_into_table(templat_name, table_name, filename, table_suffix):
    try:
        db = MySQLdb.connect(db_ip, db_user, db_passwd, db_name)
        cursor = db.cursor()
        cursor.execute("select 1 from information_schema.tables where table_schema = database() and table_name ='%s'" % table_name)
        table_num = cursor.fetchall();
        if len(table_num) > 0 and table_suffix == '_{zone}_{date}':
            cursor.execute("drop table if exists %s " % table_name)
            cursor.execute("create table if not exists %s like %s" % (table_name, templat_name))
        if len(table_num) < 1:
            cursor.execute("create table if not exists %s like %s" % (table_name, templat_name))
        cursor.execute("load data infile '%s' replace into table %s" % (filename, table_name))
        db.commit()
        cursor.close()
        db.close()
        log("[oad_data_into_table] 成功,%s,%s,%s" % (templat_name, filename, table_name))
    except MySQLdb.Error, e:
        log("[oad_data_into_table] 失败,%s,%d,%s" % (templat_name, e.args[0], e.args[1]))

def load_data(stat_map, dir):
    log("[load_data] dir:%s" % dir)
    for parent,dirnames,filenames in os.walk(dir):
        for filenames in filenames:
            full_file_name = os.path.join(parent, filenames)
            proto = full_file_name.split('.')[0].split('/')[-1]
            log(" == %s ----========================---- %s" % (full_file_name, proto))
            if proto not in stat_map:
                log("未配置,%s,%s" % (proto, full_file_name))
                continue
            if stat_map[proto]['load'] == '0':
                log("禁用,%s,%s" % (proto, full_file_name))
                continue
            date = full_file_name.split('/')[-3]
            zone = full_file_name.split('/')[-2]
            if stat_map[proto]['table_suffix'] == '_{zone}_{date}':
                table_name = ''.join([proto, "_", zone, "_", date])
            elif stat_map[proto]['table_suffix'] == '_{zone}':
                table_name = ''.join([proto, "_", zone])
            load_data_into_table(proto, table_name, full_file_name, stat_map[proto]['table_suffix'])

def main():   
    log("开始加载数据################################################")
    get_path()
    print_config()
    stat_map = parse_config(config_file)
    print stat_map
    load_data(stat_map, log_path)
    log("结束加载数据################################################")

if __name__ == "__main__":
    main()
