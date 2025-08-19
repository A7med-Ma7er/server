#!/usr/bin/python2.7
#_*_ coding:utf-8 _*_

import sys
import traceback
import commands
import xlrd, os, sys, re, getopt
from xml.dom import minidom
from string import Template
import MySQLdb

reload(sys)
sys.setdefaultencoding('utf-8')

db_ip = "192.168.1.248"
db_user = "wanyue"
db_passwd = "wanyue"
db_name = "wy_game_config"

serverPath = "/home/tangbaoyan/work/server"


def execute_sql(sql):
    db = MySQLdb.connect(db_ip, db_user, db_passwd, db_name, charset='utf8')
    cursor = db.cursor()
    cursor.execute(sql)
    db.commit()
    cursor.close()
    db.close()

def parse_config(config_file):
    all_sheets = {}
    fp = open(config_file, "r")
    content = fp.read()
    fp.close()
    try:
        charset = re.compile(".*\s*encoding=\"([^\"]+)\".*", re.M).match(content).group(1)
    except:
        charset = "utf-8"
    if charset.upper() != "utf-8":
        content = re.sub(charset, "utf-8", content)
        content = content.decode(charset).encode("utf-8")
    try:
        dom = minidom.parseString(content)
        print "开始解析%s文件..." % config_file
    except Exception, e:
        print "xml文件解析错误: %s" % e
        exit

    tables = dom.getElementsByTagName("table")
    for table in tables:
        file_name = table.attributes["file_name"].value
        print "Excel File:", file_name
        sheets = table.getElementsByTagName("sheet")
        all_sheets[file_name] = {}
        for sheet in sheets:
            sheet_name = sheet.attributes["sheet_name"].value
            table_name = sheet.attributes["table_name"].value
            table_name = table_name.encode("utf-8")
            #start_line = sheet.attributes["start_line"].value
            fields = sheet.getElementsByTagName("field")            
            #all_sheets[file_name][sheet_name] = {"table_name":table_name, "start_line":start_line, "data":[]}         
            all_sheets[file_name][sheet_name] = {"table_name":table_name, "data":[]}         
            for i, field in enumerate(fields):
                col_name = field.attributes["col_name"].value
                sql_name = field.attributes["sql_name"].value
                col_isstring = field.attributes["isstring"].value
                field_data = {"col_name":col_name, "sql_name":sql_name, "isstring":col_isstring}
                all_sheets[file_name][sheet_name]["data"].append(field_data)

    print "#" * 80
    print "========>解析 %s文件完成!" % config_file
    print all_sheets
    print "#" * 80
    return all_sheets




def genSQL(pbdFile, structName, structConf):
    pbd = open(pbdFile)
    pbdStr = pbd.read()
    pbd.close()
    sys.path.append("%s/Tools/Excel2Pbd/" % serverPath)
    sys.path.append("%s/ServerPbd" % serverPath)
    exec("from pbd_server_pb2 import *")
    exec("proto_struct = %s()" % structName)
    proto_struct.ParseFromString(pbdStr)

    sql = ''.join(["INSERT INTO `", structConf["table_name"], "` VALUES "])
    valuestr = ''
    i = 0
    for data in proto_struct.datas:
        if i > 0:
            valuestr = ''.join([valuestr, ","])
        i = i + 1
        valuestr = ''.join([valuestr, "("])
        j = 0
        for conf in structConf["data"]:
            if j > 0:
                valuestr = ''.join([valuestr, ","])
            j = j + 1
            exec("v = data.m_%s" % conf["col_name"])
            if conf["isstring"] == "1":
                valuestr = ''.join([valuestr, "'", str(v).encode('utf-8'), "'"])
            else:
                valuestr = ''.join([valuestr, str(v).encode('utf-8')])
        valuestr = ''.join([valuestr, ")"])
    sql = ''.join([sql, valuestr, ";"])
    print sql
    return sql


def main():   
    #解析xml配置文件
    xmlconfigPath = "%s/Tools/Stat" % serverPath
    pbdPath = "%s/ServerPbd/TableData" % serverPath

    all_sheets = parse_config("%s/xls_config.xml" % xmlconfigPath)
    #解析Excel数据文件
    #extract_excel(all_sheets, "/home/tangbaoyan/.eagle/pbd/")
    heroSql = genSQL("%s/Hero_Hero.pbd" % pbdPath, "MsgTableHeros", all_sheets["Hero.xlsx"]["Hero"])
    execute_sql(heroSql)
    itemSql = genSQL("%s/Item_Item.pbd" % pbdPath, "MsgTableItem", all_sheets["Item.xlsx"]["Item"])
    execute_sql(itemSql)

if __name__ == "__main__":
    main()




"""
def extract_excel(all_sheets, xls_dir):
    for file_name in all_sheets.keys(): 
        fp = os.path.join(xls_dir, file_name.encode("utf-8")) 
        if not os.path.exists(fp):
            assert False, "%s\n找不到源文件：%s\n%s" % ("#"*60, fp, "#"*60)                  
        print "Excel文件===", fp
        book = xlrd.open_workbook(fp)
        print "开始解析Excel文件", fp
        for sheet_name, sheet_config in all_sheets[file_name].items():
            table_name = sheet_config["table_name"]
            fields = sheet_config["data"]
            print "开始读取 <%s>工作表 数据" % unicode(sheet_name).encode("utf-8")               
            try:                         
                sheet = book.sheet_by_name(sheet_name)
            except Exception, e:
                assert False, "%s\n%s中可能没有<%s>工作表\n%s\n%s" % \
                ("#" * 40, unicode(file_name).encode("utf-8"), unicode(sheet_name).encode("utf-8"), str(e), "#" * 40)
            #总行数
            row_num = sheet.nrows
            col_num = sheet.ncols
            #取得对应所要获取字段的列号
            sql = ''.join(["replace into ", table_name, "("]) 
            for i in range(0, len(fields)):
                field = fields[i]
                print field
                sql = ''.join([sql, field["sql_name"]])
                if i != len(fields) - 1:
                    sql = ''.join([sql, ","])
                for c in range(col_num):           
                    if sheet.cell_value(0, c) == field["col_name"]:
                        fields[i]["col_index"] = c
                        print c
            sql = ''.join([sql, ") values"]);
            start_line = int(all_sheets[file_name][sheet_name]["start_line"])
            for r in range(start_line, row_num):    
                sql = ''.join([sql, "("])
                for c in range(0, len(fields)):
                    field = fields[c]
                    val = sheet.cell_value(r, field["col_index"])
                    if isinstance(val, int) or isinstance(val, float):
                        val = str(val)
                    else:
                        val = ''.join(["'", val, "'"])
                    sql = ''.join([sql, val])
                    if c != len(fields) - 1:
                        sql = ''.join([sql, ","])
                sql = ''.join([sql, ")"])
                if r != row_num - 1:
                    sql = ''.join([sql, ","])
            execute_sql(sql)

    print "#" * 80    
"""

