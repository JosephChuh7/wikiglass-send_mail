#!/usr/bin/python
# -*- coding: utf-8 -*-
import mysql.connector
from mysql.connector import errorcode


def connect_db(db_config):
    '''
    :param db_config: a dict contains configuration of db  e.g.
                db_config = {
                    'user' : PB_DB_USERNAME,
                    'password' : PB_DB_PWD,
                    'host' : PB_DB_HOST,
                    'database' : PB_DB_NAME,
                    'charset' : CHARSET
                    }
    :return: connection conn
    '''
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except mysql.connector.Error as err:
        handle_db_except(err)

def close_db_conn(conn):
    if conn:
        conn.close()

def handle_db_except(err):
    if not err: #if err is empty, just return
        return

    print ("connect to db fails!")

    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Something is wrong with your user name or password")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist")
    else:
        pass
    print (err)


def db_exec(conn, sql_cmd, *param):

    '''
    :param conn: MySQL connection
    :param sql_cmd: SQL command
    :param param:  parameters in SQL command
    :return: cur.fetchall() if exists
    '''

    # global exec_num

    cur = conn.cursor()
    result = []
    try:
        cur.execute(sql_cmd, *param)
        result = cur.fetchall()
    except mysql.connector.Error as err:
        print(err)

    finally:
        cur.close()

    # exec_num +=1
    # print ("第 {} 次执行".format(exec_num))
    return result


