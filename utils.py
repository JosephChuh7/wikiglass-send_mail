#!/usr/bin/python
# -*- coding: utf-8 -*-
import mysql.connector
import time
import datetime
import math
import logging
import ConfigParser
from mysql.connector import errorcode
from datetime import timedelta

import sys

class Global_config():
    def __init__(self):
        CONFIG = ConfigParser.ConfigParser()
        # config file path
        CONFIG.read("/home/oper/wikiglass-data-service/wikiglass-service-platform/codes/settings/global.conf")
        #CONFIG.read("/Users/joseph/work/ra/global.conf")
        # year version
        self.YEAR = CONFIG.get("system_version", "year")
        # pbworks_db config
        self.PB_DB_USERNAME = CONFIG.get("pbworks_db_conf", "username")
        self.PB_DB_PWD = CONFIG.get("pbworks_db_conf", "password")
        self.PB_DB_HOST = CONFIG.get("pbworks_db_conf", "db_host")
        self.PB_DB_NAME = CONFIG.get("pbworks_db_conf", "db_name")
        # log file path
        self.LOGFILE = CONFIG.get("logs_conf", "common_log")
        # email txt files directory
        self.EMAIL_DIR = CONFIG.get("email_text", "text_directory")


def mean(values):
    return sum(values)/len(values)


# Standard deviation is not outputted to the email, for reference only
def stdev(values):
    length = len(values)
    m = mean(values)
    total_sum = 0
    for i in range(length):
        total_sum += (values[i]-m)**2
    return int(math.sqrt(total_sum/(length-1)))


# transform every element in a 2d list to utf-8
# parameters: @list_2d : a 2d list
# return a new 2d list with all elements coding in utf-8
def list_2d_encode_utf8(list_2d):
    result_list = []
    for row in list_2d:
        temp = []
        for i in range(0, len(row)):
            if isinstance(row[i], unicode):
                temp.append(row[i].encode('utf-8'))
            else:
                temp.append(row[i])

        result_list.append(temp)
    return result_list

def get_date_ymd(timestamp):
    return datetime.datetime.fromtimestamp(timestamp).strftime('%Y/%m/%d')

if __name__=='__main__':
    pass